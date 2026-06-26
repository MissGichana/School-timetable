import sqlite3
import os
from datetime import datetime
from config import Config

class Database:
    """Database connection and management"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            max_hours INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            credits INTEGER,
            capacity INTEGER NOT NULL,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            capacity INTEGER NOT NULL,
            resources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS time_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_hours INTEGER,
            is_lunch BOOLEAN DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            major TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            semester TEXT,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            UNIQUE(student_id, course_id)
        );
        
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            instructor_id INTEGER NOT NULL,
            classroom_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_hours INTEGER,
            semester TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (instructor_id) REFERENCES instructors(id),
            FOREIGN KEY (classroom_id) REFERENCES classrooms(id)
        );
        
        CREATE TABLE IF NOT EXISTS conflicts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER,
            conflict_type TEXT NOT NULL,
            description TEXT,
            severity TEXT DEFAULT 'high',
            resolved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (schedule_id) REFERENCES schedules(id)
        );
        
        CREATE TABLE IF NOT EXISTS instructor_availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instructor_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            available BOOLEAN DEFAULT 1,
            FOREIGN KEY (instructor_id) REFERENCES instructors(id),
            UNIQUE(instructor_id, day)
        );
        ''')
        
        conn.commit()
        
        # Seed data if empty
        cursor.execute("SELECT COUNT(*) FROM instructors")
        if cursor.fetchone()[0] == 0:
            self.seed_data(conn)
        
        conn.close()
    
    def seed_data(self, conn):
        """Seed initial data"""
        cursor = conn.cursor()
        
        # Instructors
        instructors = [
            ('Dr. Alice Smith', 'alice@school.edu', 'Computer Science'),
            ('Dr. Bob Johnson', 'bob@school.edu', 'Computer Science'),
            ('Prof. Carol White', 'carol@school.edu', 'Mathematics'),
            ('Prof. David Brown', 'david@school.edu', 'Physics'),
            ('Prof. Eve Davis', 'eve@school.edu', 'Chemistry'),
            ('Prof. Frank Miller', 'frank@school.edu', 'Biology'),
            ('Prof. Grace Lee', 'grace@school.edu', 'Engineering'),
        ]
        
        cursor.executemany(
            "INSERT INTO instructors (name, email, department) VALUES (?, ?, ?)",
            instructors
        )
        
        # Courses
        courses = [
            ('CS101', 'Introduction to Python', 3, 60, 'Computer Science'),
            ('CS102', 'Data Structures', 3, 50, 'Computer Science'),
            ('CS103', 'Algorithms', 3, 40, 'Computer Science'),
            ('MATH101', 'Calculus I', 4, 70, 'Mathematics'),
            ('MATH102', 'Linear Algebra', 3, 55, 'Mathematics'),
            ('MATH103', 'Discrete Mathematics', 3, 45, 'Mathematics'),
            ('PHYS101', 'Physics I', 4, 65, 'Physics'),
            ('PHYS102', 'Physics II', 4, 60, 'Physics'),
            ('CHEM101', 'General Chemistry', 4, 55, 'Chemistry'),
            ('CHEM102', 'Organic Chemistry', 4, 50, 'Chemistry'),
            ('BIO101', 'Biology I', 4, 70, 'Biology'),
            ('BIO102', 'Biology II', 4, 65, 'Biology'),
            ('ENG101', 'Engineering Design', 3, 40, 'Engineering'),
            ('ENG102', 'CAD & Modeling', 3, 35, 'Engineering'),
            ('ENG103', 'Robotics', 3, 30, 'Engineering'),
        ]
        
        cursor.executemany(
            "INSERT INTO courses (code, name, credits, capacity, department) VALUES (?, ?, ?, ?, ?)",
            courses
        )
        
        # Classrooms
        classrooms = [
            ('Room 101', 60, 'Projector, Whiteboard'),
            ('Room 102', 50, 'Projector, Whiteboard'),
            ('Lab A', 40, 'Computers, Lab Equipment'),
            ('Auditorium', 100, 'Projector, Microphone'),
            ('Room 203', 35, 'Projector, Whiteboard'),
        ]
        
        cursor.executemany(
            "INSERT INTO classrooms (room_number, capacity, resources) VALUES (?, ?, ?)",
            classrooms
        )
        
        # Time slots
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = []
        
        # Morning slots (8 AM - 1 PM)
        morning_slots = [
            ('08:00', '10:00', 2),
            ('10:00', '12:00', 2),
        ]
        
        # Afternoon slots (2 PM - 5 PM)
        afternoon_slots = [
            ('14:00', '16:00', 2),
            ('15:00', '17:00', 2),
        ]
        
        for day in days:
            for start, end, duration in morning_slots:
                time_slots.append((day, start, end, duration, 0))
            for start, end, duration in afternoon_slots:
                time_slots.append((day, start, end, duration, 0))
        
        cursor.executemany(
            "INSERT INTO time_slots (day, start_time, end_time, duration_hours, is_lunch) VALUES (?, ?, ?, ?, ?)",
            time_slots
        )
        
        # Instructor availability (all available all days by default)
        for i in range(1, 8):
            for day in days:
                cursor.execute(
                    "INSERT INTO instructor_availability (instructor_id, day, available) VALUES (?, ?, 1)",
                    (i, day)
                )
        
        # Students (sample)
        students = [(f'STU{1000+i}', f'Student {i}', f'student{i}@school.edu', 'Computer Science', 1) 
                   for i in range(1, 31)]
        
        cursor.executemany(
            "INSERT INTO students (student_id, name, email, major, year) VALUES (?, ?, ?, ?, ?)",
            students
        )
        
        conn.commit()
    
    def execute_query(self, query, params=()):
        """Execute a query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def fetch_query(self, query, params=()):
        """Fetch query results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def fetch_one(self, query, params=()):
        """Fetch single result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result

# Initialize database
if __name__ == '__main__':
    db = Database()
    print("Database initialized successfully!")