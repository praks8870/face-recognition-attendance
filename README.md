
# Face Recognition Attendance System

## Project Overview
This **Face Recognition Attendance System** is a web application built with Flask that automates attendance marking using live video feed. It employs face recognition technology to capture and log attendance, dynamically storing the data in a PostgreSQL database. The system also provides insightful reports on employee attendance, including working days, leaves, late arrivals, and early departures.

## Key Features
- **Face Recognition**: Automatically marks attendance using a live camera feed.
- **Database Integration**: Attendance records are stored securely in a PostgreSQL database.
- **Attendance Report**: Provides detailed status reports on employee attendance, including:
  - Working Days
  - Worked Days
  - Leave Days
  - Late Arrival Reports (arrival after 9:15 AM)
  - Early Leave Reports (leaving before 6:00 PM)
- **Camera Control**: Users can start and stop the camera feed directly from the homepage.

## Technologies Used
- **Backend**: Flask (Python)
- **Face Recognition**: OpenCV, dlib, face_recognition
- **Database**: PostgreSQL
- **Frontend**: HTML5, Jinja2 (for templating), CSS (for styling)
- **Version Control**: Git

## System Architecture
1. **Face Recognition**: Uses pre-trained face encodings to recognize users from the camera feed.
2. **Attendance Logging**: Once a face is recognized, the system automatically logs the entry ("in") and exit ("out") times in the PostgreSQL database.
3. **Attendance Reports**: The application calculates and displays attendance details such as leaves, late entries, and early exits based on user activity in the month.
4. **Live Camera Feed**: Users can control the live feed with a simple on/off toggle from the homepage.

## Setup and Installation

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.7+
- PostgreSQL
- Git

### Step-by-Step Installation Guide

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/face-recognition-attendance.git
   cd face-recognition-attendance

2. **Set Up a Virtual Environment (optional but recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows, use: venv\Scripts\activate

3. **Install Required Dependencies: Install all the dependencies listed in requirements.txt**:
    ```bash
    pip install -r requirements.txt

4. **Set Up PostgreSQL:**
    ```sql
    CREATE DATABASE postgres;

    CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    status VARCHAR(10),
    date DATE,
    time TIME
    );

5. **Run Flask App and Access the application**:
    ```bash
    python app.py

    Access the Application: Open your browser and go to:
    http://127.0.0.1:5000

## Project Structure

## Key Files

**app.py: The main Flask application responsible for managing routes, processing camera feeds, and handling face recognition.**
**uploads/: A folder containing the reference images used for face recognition.**
**status_report.html: The template for generating the attendance status report.**

## Sample Data

You can find sample attendance data for multiple users logged during September 2024, excluding Sundays.

## Attendance Reports
    - Working Days: All weekdays (Monday to Saturday) except Sundays.
    - Worked Days: Days on which the user marked "in" attendance.
    - Leaves: The difference between working days and worked days.
    - Late: Days where the user logged "in" after 9:15 AM.
    - Early Leave: Days where the user logged "out" before 6:00 PM.
    
## Future Improvements

   - **User Authentication**: Adding a login system to restrict access to admin and employees.
   - **Export Reports**: Allow users to export attendance reports as CSV or PDF.
   - **Mobile Compatibility**: Optimize the UI for mobile devices.
   - **Real-time Notifications**: Notify employees via email/SMS for late arrivals or early leaves.

## Conclusion

This project showcases how to build an effective face recognition system for attendance management using Flask, PostgreSQL, and OpenCV. It's a powerful demonstration of your ability to combine real-time video processing with database management and report generation.