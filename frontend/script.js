const API_BASE_URL = 'http://localhost:5000/api';

// ============ TAB SWITCHING ============

function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active from buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active to button
    event.target.classList.add('active');
    
    // Load data when switching tabs
    if (tabName === 'dashboard') {
        loadDashboard();
    } else if (tabName === 'instructor') {
        loadInstructorSelect();
    } else if (tabName === 'student') {
        loadStudentSelect();
    }
}

// ============ DASHBOARD ============

async function loadDashboard() {
    try {
        // Load statistics
        const statsResponse = await fetch(`${API_BASE_URL}/stats/dashboard`);
        const stats = await statsResponse.json();
        
        document.getElementById('totalCourses').textContent = stats.total_courses;
        document.getElementById('totalInstructors').textContent = stats.total_instructors;
        document.getElementById('totalClassrooms').textContent = stats.total_classrooms;
        document.getElementById('scheduledClasses').textContent = stats.scheduled_classes;
        
        // Load timetable
        loadTimetable();
        
        // Load workload chart
        loadWorkloadChart();
        
        // Load utilization chart
        loadUtilizationChart();
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadTimetable() {
    try {
        const response = await fetch(`${API_BASE_URL}/schedules`);
        const schedules = await response.json();
        
        const tbody = document.getElementById('timetableBody');
        tbody.innerHTML = '';
        
        if (schedules.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No scheduled classes yet</td></tr>';
            return;
        }
        
        schedules.forEach(schedule => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${schedule.course_code}</strong><br>${schedule.course_name}</td>
                <td>${schedule.instructor_name}</td>
                <td>${schedule.day}</td>
                <td>${schedule.start_time} - ${schedule.end_time}</td>
                <td>${schedule.classroom_name}</td>
                <td>${schedule.duration_hours} hrs</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading timetable:', error);
    }
}

async function loadWorkloadChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats/instructor-workload`);
        const workload = await response.json();
        
        const chartDiv = document.getElementById('workloadChart');
        chartDiv.innerHTML = '';
        
        const table = document.createElement('table');
        table.style.width = '100%';
        table.innerHTML = '<tr><th>Instructor</th><th>Classes</th><th>Bar</th></tr>';
        
        workload.forEach(item => {
            const row = document.createElement('tr');
            const barWidth = (item.classes / 5) * 100;
            row.innerHTML = `
                <td><strong>${item.instructor_name}</strong></td>
                <td>${item.classes}</td>
                <td><div style="background: linear-gradient(90deg, #3498db, #2ecc71); width: ${barWidth}%; height: 20px; border-radius: 3px;"></div></td>
            `;
            table.appendChild(row);
        });
        
        chartDiv.appendChild(table);
    } catch (error) {
        console.error('Error loading workload chart:', error);
    }
}

async function loadUtilizationChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats/classroom-utilization`);
        const utilization = await response.json();
        
        const chartDiv = document.getElementById('utilizationChart');
        chartDiv.innerHTML = '';
        
        const table = document.createElement('table');
        table.style.width = '100%';
        table.innerHTML = '<tr><th>Classroom</th><th>Classes</th><th>Capacity</th></tr>';
        
        utilization.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${item.classroom_name}</strong></td>
                <td>${item.classes}</td>
                <td>${item.capacity}</td>
            `;
            table.appendChild(row);
        });
        
        chartDiv.appendChild(table);
    } catch (error) {
        console.error('Error loading utilization chart:', error);
    }
}

// ============ ADMIN PANEL ============

async function generateSchedule() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/generate-schedule`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        const reportDiv = document.getElementById('generationReport');
        reportDiv.classList.add('show');
        
        if (result.success) {
            reportDiv.classList.add('success');
            reportDiv.classList.remove('error');
            reportDiv.innerHTML = `
                <h4>✓ Schedule Generated Successfully!</h4>
                <p><strong>Scheduled Courses:</strong> ${result.scheduled_courses} / ${result.total_courses}</p>
                ${result.failed_courses.length > 0 ? `<p><strong>Failed to Schedule:</strong> ${result.failed_courses.join(', ')}</p>` : ''}
                <p>${result.message}</p>
            `;
        } else {
            reportDiv.classList.add('error');
            reportDiv.classList.remove('success');
            reportDiv.innerHTML = `<h4>✗ Error: ${result.message}</h4>`;
        }
        
        // Reload dashboard
        loadDashboard();
    } catch (error) {
        console.error('Error generating schedule:', error);
        alert('Error generating schedule: ' + error.message);
    }
}

async function clearSchedule() {
    if (!confirm('Are you sure you want to clear all schedules?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/clear-schedule`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Schedule cleared successfully!');
            loadDashboard();
        }
    } catch (error) {
        console.error('Error clearing schedule:', error);
        alert('Error clearing schedule');
    }
}

async function addInstructor(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('instructorName').value,
        email: document.getElementById('instructorEmail').value,
        department: document.getElementById('instructorDept').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/add-instructor`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Instructor added successfully!');
            event.target.reset();
        } else {
            alert('Error adding instructor: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function addCourse(event) {
    event.preventDefault();
    
    const data = {
        code: document.getElementById('courseCode').value,
        name: document.getElementById('courseName').value,
        credits: parseInt(document.getElementById('courseCredits').value),
        capacity: parseInt(document.getElementById('courseCapacity').value),
        department: document.getElementById('courseDept').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/add-course`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Course added successfully!');
            event.target.reset();
        } else {
            alert('Error adding course: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function addClassroom(event) {
    event.preventDefault();
    
    const data = {
        room_number: document.getElementById('roomNumber').value,
        capacity: parseInt(document.getElementById('roomCapacity').value),
        resources: document.getElementById('roomResources').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/add-classroom`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Classroom added successfully!');
            event.target.reset();
        } else {
            alert('Error adding classroom: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// ============ INSTRUCTOR VIEW ============

async function loadInstructorSelect() {
    try {
        const response = await fetch(`${API_BASE_URL}/instructors`);
        const instructors = await response.json();
        
        const select = document.getElementById('instructorSelect');
        select.innerHTML = '<option value="">-- Choose an instructor --</option>';
        
        instructors.forEach(instructor => {
            const option = document.createElement('option');
            option.value = instructor.id;
            option.textContent = instructor.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading instructors:', error);
    }
}

async function loadInstructorSchedule() {
    const instructorId = document.getElementById('instructorSelect').value;
    
    if (!instructorId) {
        document.getElementById('instructorScheduleContainer').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/instructor/${instructorId}/schedule`);
        const data = await response.json();
        
        document.getElementById('instructorName').textContent = data.instructor?.name || 'Unknown';
        
        const tbody = document.getElementById('instructorScheduleBody');
        tbody.innerHTML = '';
        
        if (data.schedule.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No scheduled classes</td></tr>';
        } else {
            data.schedule.forEach(schedule => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${schedule.course_code}</strong><br>${schedule.course_name}</td>
                    <td>${schedule.day}</td>
                    <td>${schedule.start_time} - ${schedule.end_time}</td>
                    <td>${schedule.classroom_name}</td>
                    <td>${schedule.duration_hours} hrs</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        document.getElementById('instructorScheduleContainer').style.display = 'block';
    } catch (error) {
        console.error('Error loading instructor schedule:', error);
    }
}

// ============ STUDENT VIEW ============

async function loadStudentSelect() {
    try {
        const response = await fetch(`${API_BASE_URL}/students`);
        const students = await response.json();
        
        const select = document.getElementById('studentSelect');
        select.innerHTML = '<option value="">-- Choose a student --</option>';
        
        students.forEach(student => {
            const option = document.createElement('option');
            option.value = student.id;
            option.textContent = `${student.name} (${student.student_id})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

async function loadStudentSchedule() {
    const studentId = document.getElementById('studentSelect').value;
    
    if (!studentId) {
        document.getElementById('studentScheduleContainer').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/student/${studentId}/schedule`);
        const data = await response.json();
        
        document.getElementById('studentName').textContent = data.student?.name || 'Unknown';
        
        const tbody = document.getElementById('studentScheduleBody');
        tbody.innerHTML = '';
        
        if (data.schedule.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No enrolled classes</td></tr>';
        } else {
            data.schedule.forEach(schedule => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${schedule.course_code}</strong><br>${schedule.course_name}</td>
                    <td>${schedule.instructor_name}</td>
                    <td>${schedule.day}</td>
                    <td>${schedule.start_time} - ${schedule.end_time}</td>
                    <td>${schedule.classroom_name}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        document.getElementById('studentScheduleContainer').style.display = 'block';
    } catch (error) {
        console.error('Error loading student schedule:', error);
    }
}

// ============ LOAD ON START ============

window.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});