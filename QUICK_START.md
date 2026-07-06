# 🚀 QUICK START - School Timetable System

## ⚡ 5-Minute Setup

### **Terminal 1: Setup Backend**

```bash
# Step 1: Navigate to project
cd School-timetable-system

# Step 2: Create virtual environment
python -m venv venv

# Step 3: Activate (Choose one):
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Create .env file
cp .env.example .env

# Step 6: Initialize database
python -m backend.database

# Step 7: Start backend server
python backend/app.py
```

**Expected Output:**
```
INFO:__main__:Services initialized successfully
INFO:__main__:Starting Flask app on 0.0.0.0:5000
 * Running on http://0.0.0.0:5000
```

---

### **Terminal 2: Start Frontend**

```bash
# Navigate to frontend folder (in new terminal)
cd School-timetable-system/frontend

# Start simple HTTP server
python -m http.server 3000
```

**Expected Output:**
```
Serving HTTP on 0.0.0.0 port 3000
```

---

## 🌐 Access Application

**Open Browser:** http://localhost:3000

---

## ✅ Verify Everything Works

1. **Dashboard Tab** - Should show statistics (0 courses initially)
2. **Admin Panel** - Click "Generate Schedule" button
3. **Dashboard Again** - Stats should update
4. **Instructor View** - Select an instructor, see their schedule
5. **Student View** - Select a student, see their schedule

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Port 5000 already in use" | Change `FLASK_PORT=5001` in `.env` |
| "Module not found" | Activate venv: `source venv/bin/activate` |
| "CORS error" | Both services must run (backend + frontend) |
| "Database not found" | Run: `python -m backend.database` |
| Page shows 404 | Check frontend terminal - must say "Serving HTTP" |

---

## 📊 What You Can Do

✅ View complete timetable  
✅ Generate automatic schedules  
✅ Add instructors, courses, classrooms  
✅ View instructor workload  
✅ View classroom utilization  
✅ Check student schedules  
✅ View conflicts (if any)  

---

## 📁 Default Data

- **7 Instructors** (Dr. Alice Smith, etc.)
- **15 Courses** (CS101, MATH101, etc.)
- **5 Classrooms** (Room 101, Lab A, Auditorium, etc.)
- **30 Students** (Student 1-30)

---

## 🛑 Stop Application

**In each terminal:** Press `Ctrl+C`

---

## 🔄 Next Run (After First Setup)

```bash
# Just activate venv and run servers
cd School-timetable-system

# Terminal 1:
source venv/bin/activate  # or venv\Scripts\activate on Windows
python backend/app.py

# Terminal 2:
cd frontend
python -m http.server 3000
```

---

## 📝 Configuration

Edit `.env` to change:

```bash
FLASK_DEBUG=False          # Set True for development
FLASK_PORT=5000           # Change if port in use
FRONTEND_URL=http://localhost:3000  # Frontend address
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
```

---

## 📍 File Locations

- **Database:** `database/timetable.db`
- **Logs:** `backend/logs/app.log`
- **Config:** `.env` (create from `.env.example`)
- **Frontend:** `frontend/index.html`
- **Backend API:** `backend/app.py`

---

## 🧪 Test API Directly

```bash
# Test backend is running
curl http://localhost:5000/api/health

# Should return: {"status": "ok", "message": "Server is running"}
```

---

## 💡 Pro Tips

1. **Keep 2 terminals open** - one for backend, one for frontend
2. **Check logs** if something breaks: `tail -f backend/logs/app.log`
3. **Clear schedule** if data gets messy: Admin Panel → "Clear Schedule"
4. **Add your own data** in Admin Panel: Instructors, Courses, Classrooms
5. **Use browser DevTools** (F12) to see network requests

---

## 📞 Something Wrong?

1. Check both terminals are running
2. Check `.env` file exists
3. Check database initialized: `ls database/timetable.db`
4. Check Python version: `python --version` (needs 3.7+)
5. Check ports are free: `lsof -i :5000` and `lsof -i :3000`

---

## 🎉 You're All Set!

Enjoy your School Timetable System! 🎓

For more details, see `DEPLOYMENT_GUIDE.md`
