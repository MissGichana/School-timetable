import logging
from backend.database import Database
from backend.config import Config

logger = logging.getLogger(__name__)

class ConflictDetector:
    """Detects scheduling conflicts"""
    
    def __init__(self):
        self.db = Database()
    
    @staticmethod
    def time_to_minutes(time_str):
        """Convert time string to minutes"""
        try:
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        except (ValueError, AttributeError) as e:
            logger.error(f"Error converting time {time_str}: {e}")
            raise
    
    def check_lunch_conflict(self, start_time, end_time):
        """Check if schedule overlaps with lunch time"""
        lunch_start = Config.LUNCH_START
        lunch_end = Config.LUNCH_END
        
        try:
            slot_start = self.time_to_minutes(start_time)
            slot_end = self.time_to_minutes(end_time)
            lunch_start_min = self.time_to_minutes(lunch_start)
            lunch_end_min = self.time_to_minutes(lunch_end)
            
            # Check overlap
            return slot_start < lunch_end_min and slot_end > lunch_start_min
        except Exception as e:
            logger.error(f"Lunch conflict check error: {e}")
            return False
    
    def check_instructor_conflict(self, instructor_id, day, start_time, end_time, exclude_schedule_id=None):
        """Check if instructor has class at same time"""
        try:
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
        except Exception as e:
            logger.error(f"Instructor conflict check error: {e}")
            return False
    
    def check_classroom_conflict(self, classroom_id, day, start_time, end_time, exclude_schedule_id=None):
        """Check if classroom is already booked"""
        try:
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
        except Exception as e:
            logger.error(f"Classroom conflict check error: {e}")
            return False
    
    def check_room_capacity(self, course_id, classroom_id):
        """Check if room capacity is adequate"""
        try:
            course = self.db.fetch_one("SELECT capacity FROM courses WHERE id = ?", (course_id,))
            classroom = self.db.fetch_one("SELECT capacity FROM classrooms WHERE id = ?", (classroom_id,))
            
            if not course or not classroom:
                logger.warning(f"Course {course_id} or Classroom {classroom_id} not found")
                return False
            
            return course['capacity'] <= classroom['capacity']
        except Exception as e:
            logger.error(f"Room capacity check error: {e}")
            return False
    
    def check_class_duration(self, start_time, end_time):
        """Check if class duration meets minimum requirement"""
        try:
            duration = (self.time_to_minutes(end_time) - self.time_to_minutes(start_time)) / 60
            return duration >= Config.MIN_CLASS_DURATION
        except Exception as e:
            logger.error(f"Class duration check error: {e}")
            return False
    
    def check_instructor_availability(self, instructor_id, day):
        """Check if instructor is available on this day"""
        try:
            result = self.db.fetch_one(
                "SELECT available FROM instructor_availability WHERE instructor_id = ? AND day = ?",
                (instructor_id, day)
            )
            
            if result is None:
                return True  # Default to available if no record
            return result['available']
        except Exception as e:
            logger.error(f"Instructor availability check error: {e}")
            return False
    
    @staticmethod
    def times_overlap(start1, end1, start2, end2):
        """Check if two time ranges overlap"""
        try:
            start1_min = ConflictDetector.time_to_minutes(start1)
            end1_min = ConflictDetector.time_to_minutes(end1)
            start2_min = ConflictDetector.time_to_minutes(start2)
            end2_min = ConflictDetector.time_to_minutes(end2)
            
            return start1_min < end2_min and end1_min > start2_min
        except Exception as e:
            logger.error(f"Times overlap check error: {e}")
            return False
    
    def get_all_conflicts(self, schedule_id):
        """Get all conflicts for a schedule"""
        conflicts = []
        
        try:
            schedule = self.db.fetch_one("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
            
            if not schedule:
                logger.warning(f"Schedule {schedule_id} not found")
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
        
        except Exception as e:
            logger.error(f"Error getting conflicts for schedule {schedule_id}: {e}")
        
        return conflicts
