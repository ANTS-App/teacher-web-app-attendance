# Teacher Attendance System

A Django web application that helps teachers manage class attendance using randomly generated verification numbers.

## 🚀 Overview

This application allows teachers to:
- Upload their weekly timetable via CSV
- Select classes from the timetable to take attendance
- Generate random verification numbers for students to confirm their presence
- View attendance records in an archive section

## ✨ Features

- **CSV Timetable Upload**: Upload a timetable with 5 rows (weekdays) and 10 columns (time slots from 8am-6pm)
- **Interactive Timetable**: Click on any class to start an attendance session
- **Configurable Sessions**: Choose between 1-minute or 3-minute attendance sessions
- **Real-time Integration**: Uses Firebase for real-time data synchronization with student mobile apps
- **Attendance Archives**: View historical attendance data for all classes

## 🔧 Technical Stack

- **Backend**: Django
- **Database**: SQLite (for timetable storage) + Firebase (for real-time attendance data)
- **Frontend**: Bootstrap for responsive UI

## 📱 How It Works

1. Teacher uploads their timetable CSV
2. When a class ends, the teacher clicks on the class in the timetable
3. Teacher selects the duration for the attendance session (1 or 3 minutes)
4. A random verification number appears on the teacher's screen
5. Students must select this number from options shown in their companion mobile app
6. After the session timer expires, attendance is recorded automatically
7. Records can be viewed in the Archives section

## 🔄 Integration with Student App

This web app pushes verification numbers to Firebase, which the companion student mobile app uses to:
- Display verification options to students (including the teacher's number)
- Record attendance when students select the correct number
- Store attendance records for reporting

## 🏗️ Setup & Installation

See the installation guide for detailed setup instructions.