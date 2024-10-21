from flask import Flask, render_template, Response
import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime, timedelta, time
import calendar
import psycopg2

app = Flask(__name__)

# Load images and encodings
path = 'uploads'
images = []
classNames = []
mylist = os.listdir(path)

for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoded_face = face_recognition.face_encodings(img)
        if encoded_face:
            encodeList.append(encoded_face[0])
    return encodeList

encoded_face_train = findEncodings(images)

def create_attendance_table():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",  
            user="postgres",     
            password="123456"     
        )
        cur = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            status VARCHAR(10),
            date DATE,
            time TIME
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        cur.close()
        conn.close()
        print("Table 'attendance' created successfully!")

    except Exception as e:
        print(f"Error creating table: {e}")

create_attendance_table()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",  
            user="postgres",     
            password="123456"     
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

def markAttendance(name):
    conn = get_db_connection()
    if not conn:
        print("Connection to database failed!")
        return

    cur = conn.cursor()

    try:
        cur.execute("""SELECT status, date, time FROM attendance WHERE name = %s ORDER BY id DESC LIMIT 1""", (name,))
        last_entry = cur.fetchone()

        now = datetime.now()
        current_date = now.date()
        current_time = now.time()

        if last_entry:
            last_status, last_date, last_time = last_entry
            last_datetime = datetime.combine(last_date, last_time)
            time_difference = now - last_datetime

            if time_difference < timedelta(minutes=1):
                print("Entry too soon, skipping.")
                cur.close()
                conn.close()
                return

            if last_status == "in":
                cur.execute("""INSERT INTO attendance (name, status, date, time) VALUES (%s, %s, %s, %s)""", 
                            (name, 'out', current_date, current_time))
            else:
                cur.execute("""INSERT INTO attendance (name, status, date, time) VALUES (%s, %s, %s, %s)""", 
                            (name, 'in', current_date, current_time))
        else:
            cur.execute("""INSERT INTO attendance (name, status, date, time) VALUES (%s, %s, %s, %s)""", 
                        (name, 'in', current_date, current_time))

        conn.commit()
        cur.close()
        conn.close()
        print(f"Attendance marked for {name}.")

    except Exception as e:
        print(f"Error marking attendance: {e}")
        cur.close()
        conn.close()

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            faces_in_frame = face_recognition.face_locations(imgS)
            encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)

            for encode_face, faceloc in zip(encoded_faces, faces_in_frame):
                matches = face_recognition.compare_faces(encoded_face_train, encode_face)
                faceDist = face_recognition.face_distance(encoded_face_train, encode_face)

                if len(faceDist) > 0:
                    matchIndex = np.argmin(faceDist)
                    if matches[matchIndex]:  
                        name = classNames[matchIndex].upper().lower()
                        y1, x2, y2, x1 = faceloc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                        markAttendance(name)

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status_report')
def status_report():
    now = datetime.now()
    year = now.year
    month = now.month

    total_days_in_month = calendar.monthrange(year, month)[1]

    sundays = sum(1 for day in range(1, total_days_in_month + 1) 
                  if calendar.weekday(year, month, day) == calendar.SUNDAY)

    # Calculate total working days (excluding Sundays)
    working_days_in_month = total_days_in_month - sundays

    conn = get_db_connection()
    if not conn:
        return render_template('status_report.html', report=[])

    cur = conn.cursor()

    cur.execute("SELECT DISTINCT name FROM attendance;")
    names = cur.fetchall()

    report = []
    for (name,) in names:
        cur.execute("""
            SELECT COUNT(DISTINCT date) as worked_days
            FROM attendance 
            WHERE name = %s AND status = 'in';
        """, (name,))
        worked_days = cur.fetchone()[0] or 0

        # Calculate leave days
        leave = working_days_in_month - worked_days

        # Calculate late entries (in time > 09:05 AM)
        cur.execute("""
            SELECT COUNT(*) 
            FROM attendance 
            WHERE name = %s AND status = 'in' AND time > '09:15:00';
        """, (name,))
        late_count = cur.fetchone()[0]

        # Calculate early leaves (out time < 18:00 PM)
        cur.execute("""
            SELECT COUNT(*) 
            FROM attendance 
            WHERE name = %s AND status = 'out' AND time < '18:00:00';
        """, (name,))
        early_leave_count = cur.fetchone()[0]

        report.append({
            'name': name,
            'working_days': working_days_in_month,
            'worked_days': worked_days,
            'leave': leave,
            'late': late_count,
            'early_leave': early_leave_count
        })

    cur.close()
    conn.close()
    return render_template('status_report.html', report=report)


@app.template_filter('enumerate')
def enumerate_filter(sequence):
    return enumerate(sequence, start=1)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
