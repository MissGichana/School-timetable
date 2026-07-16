const API_BASE_URL = 'http://127.0.0.1:5000/api';

// ============ ERROR HANDLING & RETRY LOGIC ============

/**
 * fetchWithRetry - Fetch with automatic retry logic
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @param {number} maxRetries - Number of retry attempts (default: 3)
 * @returns {Promise} Response object
 */
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const response = await fetch(url, options);
            
            // Check for HTTP errors
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response;
        } catch (error) {
            lastError = error;
            console.warn(`Fetch attempt ${attempt}/${maxRetries} failed for ${url}:`, error.message);
            
            // Don't retry on last attempt
            if (attempt < maxRetries) {
                // Exponential backoff: 1s, 2s, 4s
                const delay = Math.pow(2, attempt - 1) * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    throw new Error(`Failed to fetch ${url} after ${maxRetries} attempts. Last error: ${lastError.message}`);
}

/**
 * escapeHtml - Escape HTML special characters to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * showAlert - Display user-friendly alert messages
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, error, warning, info)
 * @param {number} duration - Display duration in ms (default: 5000)
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertDiv = document.getElementById('alertContainer') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${escapeHtml(message)}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    alertDiv.appendChild(alert);
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => alert.remove(), duration);
    }
}

/**
 * createAlertContainer - Create alert container if it doesn't exist
 */
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'alert-container';
    document.body.prepend(container);
    return container;
}

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
        const statsResponse = await fetchWithRetry(`${API_BASE_URL}/stats/dashboard`);
        const stats = await statsResponse.json();
        
        document.getElementById('totalCourses').textContent = stats.total_courses;
        document.getElementById('totalInstructors').textContent = stats.total_instructors;
        document.getElementById('totalClassrooms').textContent = stats.total_classrooms;
        document.getElementById('scheduledClasses').textContent = stats.scheduled_classes;
        
        // Load timetable
        await loadTimetable();
        
        // Load workload chart
        await loadWorkloadChart();
        
        // Load utilization chart
        await loadUtilizationChart();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showAlert(`Dashboard load failed: ${error.message}`, 'error');
    }
}

async function loadTimetable() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/schedules`);
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
                <td><strong>${escapeHtml(schedule.course_code)}</strong><br>${escapeHtml(schedule.course_name)}</td>
                <td>${escapeHtml(schedule.instructor_name)}</td>
                <td>${escapeHtml(schedule.day)}</td>
                <td>${escapeHtml(schedule.start_time)} - ${escapeHtml(schedule.end_time)}</td>
                <td>${escapeHtml(schedule.classroom_name)}</td>
                <td>${escapeHtml(schedule.duration_hours)} hrs</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading timetable:', error);
        showAlert(`Timetable load failed: ${error.message}`, 'error');
    }
}

async function loadWorkloadChart() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/stats/instructor-workload`);
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
                <td><strong>${escapeHtml(item.instructor_name)}</strong></td>
                <td>${escapeHtml(item.classes)}</td>
                <td><div style="background: linear-gradient(90deg, #3498db, #2ecc71); width: ${barWidth}%; height: 20px; border-radius: 3px;"></div></td>
            `;
            table.appendChild(row);
        });
        
        chartDiv.appendChild(table);
    } catch (error) {
        console.error('Error loading workload chart:', error);
        showAlert(`Workload chart load failed: ${error.message}`, 'error');
    }
}

async function loadUtilizationChart() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/stats/classroom-utilization`);
        const utilization = await response.json();
        
        const chartDiv = document.getElementById('utilizationChart');
        chartDiv.innerHTML = '';
        
        const table = document.createElement('table');
        table.style.width = '100%';
        table.innerHTML = '<tr><th>Classroom</th><th>Classes</th><th>Capacity</th></tr>';
        
        utilization.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${escapeHtml(item.classroom_name)}</strong></td>
                <td>${escapeHtml(item.classes)}</td>
                <td>${escapeHtml(item.capacity)}</td>
            `;
            table.appendChild(row);
        });
        
        chartDiv.appendChild(table);
    } catch (error) {
        console.error('Error loading utilization chart:', error);
        showAlert(`Utilization chart load failed: ${error.message}`, 'error');
    }
}

// ============ ADMIN PANEL ============

async function generateSchedule() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/admin/generate-schedule`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
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
                ${result.failed_courses && result.failed_courses.length > 0 ? `<p><strong>Failed to Schedule:</strong> ${result.failed_courses.join(', ')}</p>` : ''}
                <p>${escapeHtml(result.message)}</p>
            `;
            showAlert('Schedule generated successfully!', 'success');
        } else {
            reportDiv.classList.add('error');
            reportDiv.classList.remove('success');
            reportDiv.innerHTML = `<h4>✗ Error: ${escapeHtml(result.message || result.error)}</h4>`;
            showAlert(`Error: ${result.message || result.error}`, 'error');
        }
        
        // Reload dashboard
        await loadDashboard();
    } catch (error) {
        console.error('Error generating schedule:', error);
        showAlert(`Schedule generation failed: ${error.message}`, 'error');
    }
}

async function clearSchedule() {
    if (!confirm('Are you sure you want to clear all schedules?')) return;
    
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/admin/clear-schedule`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Schedule cleared successfully!', 'success');
            await loadDashboard();
        } else {
            showAlert(`Error: ${result.message || result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error clearing schedule:', error);
        showAlert(`Clear schedule failed: ${error.message}`, 'error');
    }
}

async function addInstructor(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('instructorName').value,
        email: document.getElementById('instructorEmail').value,
        department: document.getElementById('instructorDept').value
    };
    
    // Validate input
    if (!data.name || !data.email || !data.department) {
        showAlert('All fields are required!', 'warning');
        return;
    }
    
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/admin/add-instructor`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Instructor added successfully!', 'success');
            event.target.reset();
        } else {
            showAlert(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert(`Add instructor failed: ${error.message}`, 'error');
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
    
    // Validate input
    if (!data.code || !data.name || !data.credits || !data.capacity || !data.department) {
        showAlert('All fields are required!', 'warning');
        return;
    }
    
    if (data.credits <= 0 || data.capacity <= 0) {
        showAlert('Credits and capacity must be greater than 0!', 'warning');
        return;
    }
    
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/admin/add-course`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Course added successfully!', 'success');
            event.target.reset();
        } else {
            showAlert(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert(`Add course failed: ${error.message}`, 'error');
    }
}

async function addClassroom(event) {
    event.preventDefault();
    
    const data = {
        room_number: document.getElementById('roomNumber').value,
        capacity: parseInt(document.getElementById('roomCapacity').value),
        resources: document.getElementById('roomResources').value
    };
    
    // Validate input
    if (!data.room_number || !data.capacity) {
        showAlert('Room number and capacity are required!', 'warning');
        return;
    }
    
    if (data.capacity <= 0) {
        showAlert('Capacity must be greater than 0!', 'warning');
        return;
    }
    
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/admin/add-classroom`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Classroom added successfully!', 'success');
            event.target.reset();
        } else {
            showAlert(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert(`Add classroom failed: ${error.message}`, 'error');
    }
}

// ============ INSTRUCTOR VIEW ============

async function loadInstructorSelect() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/instructors`);
        const instructors = await response.json();
        
        const select = document.getElementById('instructorSelect');
        select.innerHTML = '<option value="">-- Choose an instructor --</option>';
        
        instructors.forEach(instructor => {
            const option = document.createElement('option');
            option.value = instructor.id;
            option.textContent = escapeHtml(instructor.name);
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading instructors:', error);
        showAlert(`Load instructors failed: ${error.message}`, 'error');
    }
}

async function loadInstructorSchedule() {
    const instructorId = document.getElementById('instructorSelect').value;
    
    if (!instructorId) {
        document.getElementById('instructorScheduleContainer').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/instructor/${instructorId}/schedule`);
        const data = await response.json();
        
        document.getElementById('instructorName').textContent = escapeHtml(data.instructor?.name || 'Unknown');
        
        const tbody = document.getElementById('instructorScheduleBody');
        tbody.innerHTML = '';
        
        if (data.schedule.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No scheduled classes</td></tr>';
        } else {
            data.schedule.forEach(schedule => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${escapeHtml(schedule.course_code)}</strong><br>${escapeHtml(schedule.course_name)}</td>
                    <td>${escapeHtml(schedule.day)}</td>
                    <td>${escapeHtml(schedule.start_time)} - ${escapeHtml(schedule.end_time)}</td>
                    <td>${escapeHtml(schedule.classroom_name)}</td>
                    <td>${escapeHtml(schedule.duration_hours)} hrs</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        document.getElementById('instructorScheduleContainer').style.display = 'block';
    } catch (error) {
        console.error('Error loading instructor schedule:', error);
        showAlert(`Load instructor schedule failed: ${error.message}`, 'error');
    }
}

// ============ STUDENT VIEW ============

async function loadStudentSelect() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/students`);
        const students = await response.json();
        
        const select = document.getElementById('studentSelect');
        select.innerHTML = '<option value="">-- Choose a student --</option>';
        
        students.forEach(student => {
            const option = document.createElement('option');
            option.value = student.id;
            option.textContent = `${escapeHtml(student.name)} (${escapeHtml(student.student_id)})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading students:', error);
        showAlert(`Load students failed: ${error.message}`, 'error');
    }
}

async function loadStudentSchedule() {
    const studentId = document.getElementById('studentSelect').value;
    
    if (!studentId) {
        document.getElementById('studentScheduleContainer').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/student/${studentId}/schedule`);
        const data = await response.json();
        
        document.getElementById('studentName').textContent = escapeHtml(data.student?.name || 'Unknown');
        
        const tbody = document.getElementById('studentScheduleBody');
        tbody.innerHTML = '';
        
        if (data.schedule.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No enrolled classes</td></tr>';
        } else {
            data.schedule.forEach(schedule => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${escapeHtml(schedule.course_code)}</strong><br>${escapeHtml(schedule.course_name)}</td>
                    <td>${escapeHtml(schedule.instructor_name)}</td>
                    <td>${escapeHtml(schedule.day)}</td>
                    <td>${escapeHtml(schedule.start_time)} - ${escapeHtml(schedule.end_time)}</td>
                    <td>${escapeHtml(schedule.classroom_name)}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        document.getElementById('studentScheduleContainer').style.display = 'block';
    } catch (error) {
        console.error('Error loading student schedule:', error);
        showAlert(`Load student schedule failed: ${error.message}`, 'error');
    }
}

// ============ LOAD ON START ============

window.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
