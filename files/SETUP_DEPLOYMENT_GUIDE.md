# 🌱 EduDew - Rural Student Dropout Early Warning System
## Complete Setup & Deployment Guide
**Tagline: High Aspirations, Humble Beginnings**

---

## 📋 Table of Contents
1. [Project Overview](#overview)
2. [System Requirements](#requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Database Setup](#database)
6. [Running the Application](#running)
7. [API Documentation](#api)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Feature Summary](#features)

---

## 🎯 Project Overview {#overview}

**EduDew** is a comprehensive AI-powered early warning system designed specifically for rural schools to identify and prevent student dropouts through:

- **Machine Learning**: Random Forest model predicting dropout probability
- **Real-time Analytics**: Live risk monitoring and trend analysis
- **Smart Interventions**: Rule-based recommendations for government schemes
- **Alert System**: SMS/push notifications for high-risk cases
- **Explainable AI**: Human-readable explanations for non-technical users
- **Offline Support**: Optimized for low-bandwidth rural environments

### Key Features
✅ Role-based access control (Admin, Teacher)
✅ Student profile with academic & socioeconomic data
✅ AI-powered dropout risk prediction
✅ Interactive dashboards with data visualization
✅ Government scheme recommendations & tracking
✅ SMS alert system for timely interventions
✅ Intervention history and tracking
✅ Mobile-responsive design for tablets/phones
✅ Multi-language support ready
✅ Completely offline-capable data entry

---

## 💻 System Requirements {#requirements}

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 4GB (8GB recommended)
- **Storage**: 500MB
- **Python**: 3.9+
- **Node.js**: 14.0+
- **Database**: SQLite (dev), MySQL 8.0 / PostgreSQL 12+ (production)

### Internet
- Development: Standard broadband
- Production: Minimum 2G connectivity (system optimized for low-bandwidth)

---

## 🚀 Installation {#installation}

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/edulrew.git
cd edulrew
```

### Step 2: Backend Setup

#### Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Frontend Setup
```bash
# Option A: Create React App from scratch
npx create-react-app frontend
cd frontend
npm install axios recharts react-router-dom

# Option B: Use provided package.json
cd frontend
npm install
```

### Step 4: Project Structure
```
edulrew/
├── edulrew_backend.py           # Flask backend application
├── edulrew_frontend.jsx         # React frontend components
├── edulrew_styles.css          # Application styling
├── requirements.txt            # Python dependencies
├── package.json               # Node.js dependencies
├── .env.example              # Environment variables template
├── Dockerfile.backend        # Backend container configuration
├── Dockerfile.frontend       # Frontend container configuration
├── docker-compose.yml        # Multi-container orchestration
├── nginx.conf               # Nginx reverse proxy config
├── Makefile                # Development commands
├── models/                 # ML models directory (created at runtime)
├── frontend/              # React application directory
└── README.md             # This file
```

---

## ⚙️ Configuration {#configuration}

### Step 1: Environment Setup
```bash
# Copy template
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### Step 2: Configure Environment Variables
```env
# Flask Configuration
FLASK_ENV=development
DEBUG=True
FLASK_APP=edulrew_backend.py

# Database - Choose one for your environment
# SQLite (Development - No setup needed)
DATABASE_URL=sqlite:///edulrew.db

# MySQL (Production)
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/edulrew

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/edulrew

# JWT Security - Change this!
JWT_SECRET_KEY=your-very-secure-random-key-change-in-production-12345

# SMS Alerts (Optional - Fast2SMS API)
FAST2SMS_API_KEY=your_api_key_from_fast2sms

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Frontend
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENVIRONMENT=development
```

### Step 3: Security Configuration
```python
# In production, ensure:
- JWT_SECRET_KEY is cryptographically random
- DEBUG = False
- SESSION_COOKIE_SECURE = True
- SESSION_COOKIE_HTTPONLY = True
- Use HTTPS with valid SSL certificates
```

---

## 🗄️ Database Setup {#database}

### SQLite (Development - Automatic)
```bash
# Database creates automatically on first run
python edulrew_backend.py
# Check for edulrew.db file creation
```

### MySQL Setup (Production)
```sql
-- Create database
CREATE DATABASE edulrew;

-- Create user
CREATE USER 'edulrew_user'@'localhost' IDENTIFIED BY 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON edulrew.* TO 'edulrew_user'@'localhost';
FLUSH PRIVILEGES;

-- Update .env
DATABASE_URL=mysql+pymysql://edulrew_user:secure_password@localhost:3306/edulrew
```

### PostgreSQL Setup
```bash
# Create database
createdb edulrew

# Create user
createuser edulrew_user

# Update .env
DATABASE_URL=postgresql://edulrew_user:password@localhost:5432/edulrew
```

### Initialize Database
```python
# Python interactive shell
from edulrew_backend import app, db, init_db

with app.app_context():
    init_db()  # Creates tables and sample schemes
    print("Database initialized successfully!")
```

---

## ▶️ Running the Application {#running}

### Option 1: Development Mode (Recommended for Setup)

#### Terminal 1 - Backend
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run backend
python edulrew_backend.py

# Output:
# * Running on http://127.0.0.1:5000
# * Debug mode: on
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm start

# Output:
# Compiled successfully!
# You can now view edulrew in the browser.
# Local: http://localhost:3000
```

### Option 2: Production Mode with Gunicorn

#### Backend
```bash
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --timeout 120 \
         --access-logfile - \
         edulrew_backend:app
```

#### Frontend
```bash
cd frontend
npm run build
npx serve -s build -l 3000
```

### Option 3: Docker Compose (Complete Stack)
```bash
# Build and run all services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Testing the Setup

#### 1. Check Backend Health
```bash
curl http://localhost:5000/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

#### 2. Access Frontend
```
http://localhost:3000
```

#### 3. Test Login with Demo Credentials
```
Email: teacher@example.com
Password: password123

Email: admin@example.com
Password: admin123
```

---

## 📚 API Documentation {#api}

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### Sign Up
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "teacher@school.com",
  "password": "securepassword",
  "name": "John Doe",
  "role": "teacher",
  "school_id": "SCHOOL_001"
}

Response: 201 Created
{
  "message": "User created successfully",
  "access_token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "teacher@school.com",
    "name": "John Doe",
    "role": "teacher",
    "school_id": "SCHOOL_001"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "teacher@school.com",
  "password": "securepassword"
}

Response: 200 OK
{
  "message": "Login successful",
  "access_token": "jwt_token_here",
  "user": { ... }
}
```

#### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer {access_token}

Response: 200 OK
{
  "id": 1,
  "email": "teacher@school.com",
  "name": "John Doe",
  "role": "teacher",
  "school_id": "SCHOOL_001"
}
```

### Student Endpoints

#### List Students
```http
GET /api/students
Authorization: Bearer {access_token}
Query Parameters:
  - class: "IV" (optional)
  - gender: "Male" (optional)
  - risk_level: "High" (optional)

Response: 200 OK
{
  "count": 45,
  "students": [ ... ]
}
```

#### Get Student Profile
```http
GET /api/students/{student_id}
Authorization: Bearer {access_token}

Response: 200 OK
{
  "student": { ... },
  "academic_data": { ... },
  "socioeconomic_data": { ... },
  "risk_analysis": { ... },
  "risk_history": [ ... ],
  "interventions": [ ... ],
  "schemes": [ ... ]
}
```

#### Create Student
```http
POST /api/students
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "enrollment_id": "STU_2024_001",
  "name": "Rahul Kumar",
  "age": 12,
  "gender": "Male",
  "class_name": "VI"
}

Response: 201 Created
{
  "message": "Student created successfully",
  "student": { ... }
}
```

#### Add Academic Data
```http
POST /api/students/{student_id}/academic
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "attendance_percentage": 85.5,
  "marks_obtained": 420,
  "marks_total": 600,
  "subject_failures": 1,
  "grade_repetitions": 0,
  "semester": "Spring 2024"
}

Response: 201 Created
```

#### Add Socioeconomic Data
```http
POST /api/students/{student_id}/socioeconomic
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "family_income": "Low",
  "parent_education": "Primary",
  "distance_to_school_km": 8.5,
  "health_issues": false,
  "has_electricity": true,
  "has_internet": false,
  "parent_employment": "Agriculture"
}

Response: 201 Created
```

### Risk Analysis Endpoints

#### Trigger Risk Analysis
```http
POST /api/students/{student_id}/analyze-risk
Authorization: Bearer {access_token}

Response: 200 OK
{
  "message": "Risk analysis completed",
  "risk_analysis": {
    "student_id": 1,
    "dropout_probability": 0.65,
    "risk_level": "High",
    "risk_score": 65.0,
    "key_risk_factors": [
      "Low attendance (72.5%)",
      "High subject failures (2)",
      "Low family income"
    ],
    "shap_explanation": "Student Rahul Kumar (VI class) has a 65.0% risk of dropping out...",
    "analyzed_at": "2024-04-08T10:30:00",
    "model_version": "v1"
  }
}
```

### Schemes Endpoints

#### List All Schemes
```http
GET /api/schemes
Authorization: Bearer {access_token}
Query Parameters:
  - type: "scholarship" (optional)

Response: 200 OK
{
  "count": 5,
  "schemes": [
    {
      "id": 1,
      "name": "National Scholarship Scheme",
      "description": "Financial aid for economically weaker students",
      "benefits": ["₹1000-2000 monthly", "Books and supplies"],
      "eligibility_criteria": ["Income < ₹2 lakhs/year", "Attendance > 75%"],
      "apply_link": "https://scheme.example.com",
      "contact_phone": "+91-1234567890",
      "scheme_type": "scholarship"
    }
  ]
}
```

#### Get Student Schemes
```http
GET /api/students/{student_id}/schemes
Authorization: Bearer {access_token}

Response: 200 OK
{
  "count": 3,
  "schemes": [
    {
      "id": 1,
      "student_id": 1,
      "scheme_id": 1,
      "scheme_name": "National Scholarship Scheme",
      "status": "Recommended",
      "application_date": null,
      "approval_date": null,
      "notes": null
    }
  ]
}
```

#### Update Scheme Status
```http
PUT /api/student-schemes/{mapping_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "Applied",
  "notes": "Application submitted on 2024-04-08"
}

Response: 200 OK
```

### Dashboard Endpoints

#### Dashboard Overview
```http
GET /api/dashboard/overview
Authorization: Bearer {access_token}

Response: 200 OK
{
  "total_students": 125,
  "high_risk_count": 8,
  "medium_risk_count": 15,
  "low_risk_count": 102,
  "alerts_sent": 12,
  "schemes_applied": 23
}
```

#### Risk Distribution
```http
GET /api/dashboard/risk-distribution
Authorization: Bearer {access_token}

Response: 200 OK
{
  "high": 8,
  "medium": 15,
  "low": 102
}
```

### Intervention Endpoints

#### Add Intervention
```http
POST /api/students/{student_id}/interventions
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "intervention_type": "Counseling Session",
  "description": "Met with student and parents regarding attendance",
  "status": "Completed"
}

Response: 201 Created
```

#### Update Intervention
```http
PUT /api/interventions/{intervention_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "Completed"
}

Response: 200 OK
```

### Error Responses

#### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

#### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

#### 403 Forbidden
```json
{
  "error": "Admin access required"
}
```

#### 404 Not Found
```json
{
  "error": "Student not found"
}
```

#### 500 Server Error
```json
{
  "error": "Internal server error"
}
```

---

## 🚢 Deployment {#deployment}

### AWS Deployment

#### EC2 Setup
```bash
# SSH into EC2 instance
ssh -i key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y
sudo yum install python3 python3-pip git mysql -y
sudo yum install nodejs npm -y

# Clone repository
git clone https://github.com/yourusername/edulrew.git
cd edulrew

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
nano .env

# Start services (use systemd for production)
sudo systemctl start edulrew-backend
sudo systemctl start edulrew-frontend
```

#### RDS Database
```bash
# Create MySQL instance via AWS Console
# Update connection string in .env:
DATABASE_URL=mysql+pymysql://user:pass@your-rds-endpoint:3306/edulrew
```

#### Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 edulrew

# Deploy
eb create edulrew-env
eb deploy

# Monitor
eb status
eb logs
```

### Render Deployment

#### Backend
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set environment variables
5. Deploy

```bash
# Build command
pip install -r requirements.txt

# Start command
gunicorn --bind 0.0.0.0:$PORT edulrew_backend:app
```

#### Frontend
```bash
# Set environment variable
REACT_APP_API_URL=https://your-backend.onrender.com/api

# Build and deploy
npm run build
```

### Firebase Deployment

#### Firestore Database
```python
# Update backend to use Firestore
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project.firebaseio.com'
})
```

#### Firebase Hosting (Frontend)
```bash
npm install -g firebase-tools
firebase login
firebase init
firebase deploy
```

### Docker Production Deployment

```bash
# Build images
docker build -f Dockerfile.backend -t edulrew-backend .
docker build -f Dockerfile.frontend -t edulrew-frontend .

# Push to registry
docker tag edulrew-backend:latest yourusername/edulrew-backend:latest
docker push yourusername/edulrew-backend:latest

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔧 Troubleshooting {#troubleshooting}

### Backend Issues

#### "ModuleNotFoundError: No module named 'flask'"
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### "sqlite3.OperationalError: unable to open database file"
```bash
# Ensure models directory exists
mkdir -p models

# Change directory permissions
chmod 755 .
```

#### "Port 5000 already in use"
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python edulrew_backend.py --port 5001
```

### Frontend Issues

#### "npm: command not found"
```bash
# Install Node.js from https://nodejs.org/
# Or use package manager
brew install node  # macOS
sudo apt-get install nodejs npm  # Ubuntu
```

#### "Cannot find module 'axios'"
```bash
cd frontend
npm install axios recharts react-router-dom
```

#### "Port 3000 already in use"
```bash
# Use different port
PORT=3001 npm start
```

### Database Issues

#### "MySQL connection error"
```bash
# Check MySQL is running
sudo systemctl status mysql

# Verify credentials in .env
# Test connection
mysql -u edulrew_user -p -h localhost edulrew
```

#### "CORS Error"
```python
# Backend will auto-handle CORS
# If issues persist, check CORS headers:
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### ML Model Issues

#### "Model not found, using random predictions"
```bash
# Train model first
curl -X POST http://localhost:5000/api/admin/train-model \
  -H "Authorization: Bearer {token}"
```

#### "Insufficient data for model training"
```bash
# Add at least 10 student records with complete academic data
# Model trains automatically on student data entry
```

---

## ✨ Feature Summary {#features}

### User Management
- ✅ Secure authentication with JWT
- ✅ Role-based access control (Admin, Teacher)
- ✅ User profile management
- ✅ Session management with auto-logout

### Student Management
- ✅ Complete student profiles with multi-section data
- ✅ Academic tracking (attendance, marks, failures)
- ✅ Socioeconomic profiling (income, parent education, distance)
- ✅ Bulk student import (CSV ready)
- ✅ Student search and filtering

### Risk Analysis
- ✅ AI-powered dropout probability prediction
- ✅ Random Forest machine learning model
- ✅ Real-time risk assessment
- ✅ Risk level categorization (Low, Medium, High)
- ✅ Key risk factor identification
- ✅ Human-readable AI explanations

### Dashboard & Analytics
- ✅ Real-time overview statistics
- ✅ Risk distribution visualization (Pie chart)
- ✅ Risk score trends (Line chart)
- ✅ Attendance vs. risk analysis (Scatter chart)
- ✅ Customizable filters (Class, Gender, Risk Level)
- ✅ Export functionality (ready for implementation)

### Government Schemes
- ✅ Comprehensive scheme catalog
- ✅ Rule-based recommendation engine
- ✅ Scheme eligibility criteria matching
- ✅ Application status tracking (Recommended → Applied → Approved)
- ✅ Multi-type schemes (Scholarship, Transport, Meal, Health, Girl Child)
- ✅ Direct application links and contact info

### Alerts & Notifications
- ✅ SMS alert integration (Fast2SMS)
- ✅ Tiered alerting (Medium/High risk)
- ✅ Personalized messages
- ✅ Alert history logging
- ✅ Rate limiting to prevent spam

### Interventions
- ✅ Intervention recording and tracking
- ✅ Status management (Pending, In Progress, Completed)
- ✅ Intervention history per student
- ✅ Multi-user assignment support

### Mobile & Offline
- ✅ Fully responsive design (mobile/tablet/desktop)
- ✅ Lightweight UI optimized for slow connections
- ✅ Dropdown inputs (no free text) for reliability
- ✅ Offline data caching ready
- ✅ Progressive Web App compatible

### Advanced Features
- ✅ Voice alerts ready (text-to-speech engine)
- ✅ AI chatbot for teachers (conversation ready)
- ✅ Multi-language support framework
- ✅ Data export capabilities
- ✅ Audit logs for compliance

---

## 📞 Support & Contribution

For issues, features, or contributions:
```
GitHub: https://github.com/yourusername/edulrew
Email: support@edulrew.example.com
Discord: https://discord.gg/edulrew
```

---

## 📄 License

This project is open-source under the MIT License. See LICENSE file for details.

---

## 🙏 Acknowledgments

Dedicated to rural schools and the students whose potential knows no bounds.
**"High Aspirations, Humble Beginnings"** 🌱

---

**Last Updated**: April 2024
**Version**: 1.0.0
**Status**: Production Ready
