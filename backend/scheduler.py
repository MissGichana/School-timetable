import random
from database import Database
from conflict_detector import ConflictDetector
from config import Config

class Scheduler:
    """Intelligent scheduling algorithm"""
    
    def __init__(self):
        self.db = Database()
        self.conflict_detector = ConflictDetector()
    
    def generate_schedule(self):
        """Generate complete timetable for all courses"""
        
        # Clear existing schedules
        self.db.execute_query("DELETE FROM schedules")
        self.db.execute_query("DELETE FROM conflicts")
        
        # Get data
        courses = self.db.fetch_query("SELECT * FROM courses")
        instructors = self.db.fetch_query("SELECT * FROM instructors")
        classrooms = self.db.fetch_query("SELECT * FROM classrooms ORDER BY capacity DESC")
        time_slots = self.db.fetch_query("SELECT DISTINCT day, start_time, end_time FROM time_slots ORDER BY day, start_time")
        
        if not courses or not instructors or not classrooms or not time_slots:
            return {'success': False, 'message': 'Insufficient data to schedule'}
        
        scheduled_courses = 0
        failed_courses = []
        
        # Distribute courses among instructors
        instructor_workload = {inst['id']: 0 for inst in instructors}
        
        for course in courses:
            # Select instructor with lowest workload
            best_instructor = min(instructor_workload, key=instructor_workload.get)
            instructor = next(inst for inst in instructors if inst['id'] == best_instructor)
            
            # Find available time slot
            scheduled = False
            attempts = 0
            max_attempts = 20
            
            while not scheduled and attempts < max_attempts:
                # Pick random time slot
                time_slot = random.choice(time_slots)
                day = time_slot['day']
                start_time = time_slot['start_time']
                end_time = time_slot['end_time']
                
                # Select appropriate classroom
                classroom = self.select_classroom(course, classrooms)
                if not classroom:
                    attempts += 1
                    continue
                
                # Check all constraints
                if (not self.conflict_detector.check_lunch_conflict(start_time, end_time) and
                    not self.conflict_detector.check_instructor_conflict(instructor['id'], day, start_time, end_time) and
                    not self.conflict_detector.check_classroom_conflict(classroom['id'], day, start_time, end_time) and
                    self.conflict_detector.check_room_capacity(course['id'], classroom['id']) and
                    self.conflict_detector.check_instructor_availability(instructor['id'], day)):
                    
                    # Save schedule
                    duration = 2  # 2 hours
                    self.db.execute_query("""
                        INSERT INTO schedules (course_id, instructor_id, classroom_id, day, start_time, end_time, duration_hours, semester)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (course['id'], instructor['id'], classroom['id'], day, start_time, end_time, duration, Config.SEMESTER))
                    
                    instructor_workload[instructor['id']] += 1
                    scheduled_courses += 1
                    scheduled = True
                
                attempts += 1
            
            if not scheduled:
                failed_courses.append(course['code'])
        
        return {
            'success': True,
            'scheduled_courses': scheduled_courses,
            'total_courses': len(courses),
            'failed_courses': failed_courses,
            'message': f'Successfully scheduled {scheduled_courses} out of {len(courses)} courses'
        }
    
    def select_classroom(self, course, classrooms):
        """Select appropriate classroom for course"""
        suitable_rooms = [c for c in classrooms if c['capacity'] >= course['capacity']]
        
        if not suitable_rooms:
            return None
        
        # Prefer smallest room that fits
        return min(suitable_rooms, key=lambda x: x['capacity'])
    
    def get_instructor_workload(self):
        """Get workload for each instructor"""
        instructors = self.db.fetch_query("SELECT * FROM instructors")
        workload = []
        
        for instructor in instructors:
            count = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM schedules WHERE instructor_id = ?",
                (instructor['id'],)
            )
            
            workload.append({
                'instructor_id': instructor['id'],
                'instructor_name': instructor['name'],
                'classes': count['count'],
                'department': instructor['department']
            })
        
        return workload
    
    def get_classroom_utilization(self):
        """Get utilization rate for each classroom"""
        classrooms = self.db.fetch_query("SELECT * FROM classrooms")
        utilization = []
        
        for classroom in classrooms:
            count = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM schedules WHERE classroom_id = ?",
                (classroom['id'],)
            )
            
            utilization.append({
                'classroom_id': classroom['id'],
                'classroom_name': classroom['room_number'],
                'classes': count['count'],
                'capacity': classroom['capacity']
            })
        
        return utilization