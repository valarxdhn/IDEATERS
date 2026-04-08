# 🚀 EduDew Quick Start Guide

**Get EduDew running in 5 minutes!**

---

## ⚡ 5-Minute Setup

### Prerequisites Check
```bash
# Check Python
python3 --version  # Should be 3.9+

# Check Node.js
node --version     # Should be 14.0+
npm --version      # Should be 6.0+
```

### Step 1: Clone & Navigate
```bash
git clone https://github.com/yourusername/edulrew.git
cd edulrew
```

### Step 2: Backend Setup (2 min)
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### Step 3: Frontend Setup (2 min)
```bash
# Install React dependencies
cd frontend
npm install
cd ..
```

### Step 4: Run the Application (1 min)

**Terminal 1 - Backend**:
```bash
source venv/bin/activate
python edulrew_backend.py
# Wait for: "Running on http://127.0.0.1:5000"
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm start
# Browser opens at http://localhost:3000
```

### Step 5: Login with Demo Credentials
```
Email: teacher@example.com
Password: password123
```

✅ **You're ready!**

---

## 📱 First Steps in the App

### 1. Create a Student
1. Click "👥 Students" in navigation
2. Click "Add New Student"
3. Fill in:
   - Name: "Rahul Kumar"
   - Enrollment ID: "STU_2024_001"
   - Class: "VI"
   - Gender: "Male"
   - Age: "12"
4. Click "Create Student"

### 2. Add Academic Data
1. Click on student profile
2. Go to "Academic" tab
3. Fill in:
   - Attendance: 72.5%
   - Marks: 420/600
   - Subject Failures: 2
   - Semester: "Spring 2024"
4. Click "Save"
   - *Note: Risk analysis auto-triggers*

### 3. Add Socioeconomic Data
1. Go to "Socioeconomic" tab
2. Fill in:
   - Family Income: "Low"
   - Parent Education: "Primary"
   - Distance: 8.5 km
   - Health Issues: "No"
   - Electricity: "Yes"
   - Internet: "No"
3. Click "Save"
   - *Note: Schemes auto-recommend*

### 4. View Risk Analysis
1. Go to "Risk" tab
2. See:
   - Risk score and level
   - Dropout probability
   - Key risk factors
   - AI explanation
   - Risk history graph

### 5. Check Recommended Schemes
1. Go to "Schemes" tab
2. See auto-recommended schemes:
   - "Scholarship" (because low income)
   - "Transport" (because 8.5km distance)
   - "Health Support" (if health issues)
3. Click "Apply" to update status

### 6. Record Intervention
1. Go to "Interventions" tab
2. Click "Add Intervention"
3. Fill in:
   - Type: "Counseling Session"
   - Description: "Met with student and parents"
4. Click "Record"

### 7. View Dashboard
1. Click "📊 Dashboard"
2. See:
   - Total students, high-risk count
   - Risk distribution pie chart
   - Real-time statistics

---

## 📊 Sample Data to Test

### Student 1: High Risk
```json
{
  "name": "Priya Sharma",
  "enrollment_id": "STU_2024_001",
  "age": 13,
  "gender": "Female",
  "class_name": "VII",
  "academic_data": {
    "attendance_percentage": 68.0,
    "marks_obtained": 280,
    "marks_total": 600,
    "subject_failures": 3,
    "grade_repetitions": 1,
    "semester": "Spring 2024"
  },
  "socioeconomic_data": {
    "family_income": "Low",
    "parent_education": "Primary",
    "distance_to_school_km": 12.5,
    "health_issues": true,
    "has_electricity": false,
    "has_internet": false,
    "parent_employment": "Labor"
  }
  // Expected Risk: HIGH (75%+)
}
```

### Student 2: Medium Risk
```json
{
  "name": "Arjun Patel",
  "enrollment_id": "STU_2024_002",
  "age": 11,
  "gender": "Male",
  "class_name": "V",
  "academic_data": {
    "attendance_percentage": 78.5,
    "marks_obtained": 420,
    "marks_total": 600,
    "subject_failures": 1,
    "grade_repetitions": 0,
    "semester": "Spring 2024"
  },
  "socioeconomic_data": {
    "family_income": "Medium",
    "parent_education": "Secondary",
    "distance_to_school_km": 6.0,
    "health_issues": false,
    "has_electricity": true,
    "has_internet": true,
    "parent_employment": "Service"
  }
  // Expected Risk: MEDIUM (40-60%)
}
```

### Student 3: Low Risk
```json
{
  "name": "Kavya Singh",
  "enrollment_id": "STU_2024_003",
  "age": 10,
  "gender": "Female",
  "class_name": "IV",
  "academic_data": {
    "attendance_percentage": 94.0,
    "marks_obtained": 540,
    "marks_total": 600,
    "subject_failures": 0,
    "grade_repetitions": 0,
    "semester": "Spring 2024"
  },
  "socioeconomic_data": {
    "family_income": "High",
    "parent_education": "Higher",
    "distance_to_school_km": 2.0,
    "health_issues": false,
    "has_electricity": true,
    "has_internet": true,
    "parent_employment": "Professional"
  }
  // Expected Risk: LOW (<30%)
}
```

---

## 🧪 Testing the API Directly

### Test with cURL

#### 1. Sign Up
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@school.com",
    "password": "password123",
    "name": "John Doe",
    "role": "teacher",
    "school_id": "SCHOOL_001"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@school.com",
    "password": "password123"
  }'
# Save the access_token from response
```

#### 3. Create Student
```bash
curl -X POST http://localhost:5000/api/students \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_id": "STU_001",
    "name": "Rahul Kumar",
    "age": 12,
    "gender": "Male",
    "class_name": "VI"
  }'
```

#### 4. Add Academic Data
```bash
curl -X POST http://localhost:5000/api/students/1/academic \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "attendance_percentage": 72.5,
    "marks_obtained": 420,
    "marks_total": 600,
    "subject_failures": 2,
    "grade_repetitions": 0,
    "semester": "Spring 2024"
  }'
```

#### 5. Get Student Profile with Risk
```bash
curl -X GET http://localhost:5000/api/students/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 6. View Dashboard
```bash
curl -X GET http://localhost:5000/api/dashboard/overview \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎮 Test Scenarios

### Scenario 1: Identify High-Risk Student
```
1. Create student with: 65% attendance, 3 failures, low income
2. System automatically identifies as HIGH RISK
3. SMS alert triggers to teacher
4. Schemes auto-recommended: Scholarship + Transport
5. Create intervention: "Schedule parent meeting"
```

### Scenario 2: Track Intervention
```
1. Create intervention: "Tutoring arranged"
2. Mark as "In Progress"
3. Update to "Completed"
4. System tracks intervention history
5. Re-analyze risk to see improvement
```

### Scenario 3: Scheme Application
```
1. View recommended schemes
2. Click "Apply" on National Scholarship
3. Status changes from "Recommended" to "Applied"
4. Admin approves: Status → "Approved"
5. System confirms benefits activated
```

---

## 🐛 Common Issues & Fixes

### Issue: "Address already in use"
```bash
# Kill existing process
lsof -i :5000  # Find process
kill -9 <PID>  # Kill it

# Or use different port
python edulrew_backend.py --port 5001
```

### Issue: "Module not found"
```bash
# Activate virtual environment
source venv/bin/activate

# Install missing module
pip install -r requirements.txt
```

### Issue: "Connection refused" between frontend & backend
```bash
# Check backend is running
curl http://localhost:5000/api/auth/login

# Update .env
REACT_APP_API_URL=http://localhost:5000/api
```

### Issue: "Database locked"
```bash
# Delete and recreate database
rm edulrew.db

# Restart application
python edulrew_backend.py
```

---

## 📈 Next Steps

### Learn the Features
- [ ] Create 10+ students with varied risk levels
- [ ] Test dashboard filters and charts
- [ ] Practice recording interventions
- [ ] Track scheme applications
- [ ] View risk history graphs

### Configure for Production
- [ ] Change JWT_SECRET_KEY in .env
- [ ] Set up MySQL/PostgreSQL database
- [ ] Enable SMS alerts (Fast2SMS API key)
- [ ] Deploy to AWS/Render/Firebase
- [ ] Set up SSL certificates

### Customize for Your School
- [ ] Add school-specific schemes
- [ ] Customize intervention types
- [ ] Set up teacher accounts
- [ ] Upload existing student data
- [ ] Configure SMS contacts

### Train ML Model
```bash
# Add 50+ students with complete data
# Then trigger training
curl -X POST http://localhost:5000/api/admin/train-model \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 📞 Getting Help

### Documentation
- Full guide: `SETUP_DEPLOYMENT_GUIDE.md`
- API docs: `SETUP_DEPLOYMENT_GUIDE.md#api-documentation`
- Database schema: `DATABASE_ML_DOCUMENTATION.md`

### Logs & Debugging
```bash
# Backend logs
tail -f edulrew.log

# Frontend console (Browser DevTools)
F12 → Console tab

# Database inspection
sqlite3 edulrew.db ".tables"
```

### Testing Tools
- **API Testing**: Postman, Insomnia, or cURL
- **Browser DevTools**: F12 for network/console
- **Database Tool**: SQLite Browser, MySQL Workbench

---

## 💡 Tips for Success

1. **Start Simple**: Create 5 students first, then expand
2. **Test Thoroughly**: Use sample data with different risk levels
3. **Monitor Logs**: Check backend logs for errors
4. **Use Admin Account**: For model training and system setup
5. **Keep Backups**: Regular database backups for production

---

## ✅ Success Checklist

- [x] Python 3.9+ installed
- [x] Node.js 14+ installed
- [x] Repository cloned
- [x] Virtual environment created
- [x] Dependencies installed
- [x] .env file configured
- [x] Backend running on :5000
- [x] Frontend running on :3000
- [x] Logged in successfully
- [x] Created first student
- [x] Risk analysis visible
- [x] Dashboard working
- [x] Ready for production setup!

---

**Enjoy using EduDew! 🌱**

For detailed information, see the full documentation in `SETUP_DEPLOYMENT_GUIDE.md`

---

**Last Updated**: April 2024
**Version**: Quick Start v1.0
