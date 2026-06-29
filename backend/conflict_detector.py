from database import Database
from config import Config

class ConflictDetector:
    """Detects scheduling conflicts"""
    
    def __init__(self):
        self.db = Database()
    
    def check_lunch_conflict(self, start_time, end_time):
        """Check if schedule overlaps with lunch time"""
        lunch_start = Config.LUNCH_START
        lunch_end = Config.LUNCH_END
        
        # Convert to minutes for easier comparison
        def time_to_minutes(time_str):
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        
        slot_start = time_to_minutes(start_time)
        slot_end = time_to_minutes(end_time)
        lunch_start_min = time_to_minutes(lunch_start)
        lunch_end_min = time_to_minutes(lunch_end)
        
        # Check overlap
        if slot_start < lunch_end_min and slot_end > lunch_start_min:
            return True
        return False
    
    def check_instructor_conflict(self, instructor_id, day, start_time, end_time, exclude_schedule_id=None):
        """Check if instructor has class at same time"""
        query = """
        SELECT * FROM schedules 
        WHERE instructor_id = ? AND day = ?
        """
        params = [instructor_id, day]
        
        if exclude_schedule_id:
            query += " AND id != ?"
            params.append(exclude_schedule_id)
        
        existing_classes = self.db.fetch_query(query, params)
        
        for cls in existing_classes:
            if self.times_overlap(start_time, end_time, cls['start_time'], cls['end_time']):
                return True
        return False
    
    def check_classroom_conflict(self, classroom_id, day, start_time, end_time, exclude_schedule_id=None):
        """Check if classroom is already booked"""
        query = """
        SELECT * FROM schedules 
        WHERE classroom_id = ? AND day = ?
        """
        params = [classroom_id, day]
        
        if exclude_schedule_id:
            query += " AND id != ?"
            params.append(exclude_schedule_id)
        
        existing_classes = self.db.fetch_query(query, params)
        
        for cls in existing_classes:
            if self.times_overlap(start_time, end_time, cls['start_time'], cls['end_time']):
                return True
        return False
    
    def check_room_capacity(self, course_id, classroom_id):
        """Check if room capacity is adequate"""
        course = self.db.fetch_one("SELECT capacity FROM courses WHERE id = ?", (course_id,))
        classroom = self.db.fetch_one("SELECT capacity FROM classrooms WHERE id = ?", (classroom_id,))
        
        if course['capacity'] > classroom['capacity']:
            return False
        return True
    
    def check_class_duration(self, start_time, end_time):
        """Check if class duration meets minimum requirement"""
        def time_to_minutes(time_str):
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        
        duration = (time_to_minutes(end_time) - time_to_minutes(start_time)) / 60
        return duration >= Config.MIN_CLASS_DURATION
    
    def check_instructor_availability(self, instructor_id, day):
        """Check if instructor is available on this day"""
        result = self.db.fetch_one(
            "SELECT available FROM instructor_availability WHERE instructor_id = ? AND day = ?",
            (instructor_id, day)
        )
        
        if result is None:
            return True  # Default to available if no record
        return result['available']
    
    def times_overlap(self, start1, end1, start2, end2):
        """Check if two time ranges overlap"""
        def time_to_minutes(time_str):
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        
        start1_min = time_to_minutes(start1)
        end1_min = time_to_minutes(end1)
        start2_min = time_to_minutes(start2)
        end2_min = time_to_minutes(end2)
        
        return start1_min < end2_min and end1_min > start2_min
    
    def get_all_conflicts(self, schedule_id):
        """Get all conflicts for a schedule"""
        conflicts = []
        
        schedule = self.db.fetch_one("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
        
        if not schedule:
            return conflicts
        
        # Check lunch conflict
        if self.check_lunch_conflict(schedule['start_time'], schedule['end_time']):
            conflicts.append({
                'type': 'LUNCH_OVERLAP',
                'description': 'Class overlaps with lunch time (1 PM - 2 PM)',
                'severity': 'high'
            })
        
        # Check instructor conflict
        if self.check_instructor_conflict(schedule['instructor_id'], schedule['day'], 
                                         schedule['start_time'], schedule['end_time'], schedule['id']):
            conflicts.append({
                'type': 'INSTRUCTOR_DOUBLE_BOOKING',
                'description': 'Instructor is already scheduled at this time',
                'severity': 'high'
            })
        
        # Check classroom conflict
        if self.check_classroom_conflict(schedule['classroom_id'], schedule['day'],
                                        schedule['start_time'], schedule['end_time'], schedule['id']):
            conflicts.append({
                'type': 'CLASSROOM_CONFLICT',
                'description': 'Classroom is already booked at this time',
                'severity': 'high'
            })
        
        # Check room capacity
        if not self.check_room_capacity(schedule['course_id'], schedule['classroom_id']):
            conflicts.append({
                'type': 'CAPACITY_VIOLATION',
                'description': 'Room capacity is insufficient for class size',
                'severity': 'high'
            })
        
        # Check class duration
        if not self.check_class_duration(schedule['start_time'], schedule['end_time']):
            conflicts.append({
                'type': 'DURATION_VIOLATION',
                'description': f'Class duration is less than {Config.MIN_CLASS_DURATION} hours',
                'severity': 'high'
            })
        
        # Check instructor availability
        if not self.check_instructor_availability(schedule['instructor_id'], schedule['day']):
            conflicts.append({
                'type': 'AVAILABILITY_VIOLATION',
                'description': 'Instructor is not available on this day',
                'severity': 'high'
            })
        
        return conflicts