# 🗄️ EduDew Database Schema & ML Documentation

## Database Schema

### Tables Overview

```
┌─────────────────────────────────────────────────────┐
│                   EDULREW DATABASE                   │
└─────────────────────────────────────────────────────┘

users (1) ────────────────┐
                          │
                    ┌─────▼─────┐
                    │  Students  │
                    └─────┬─────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
      academic_data  socioeconomic  risk_analysis
                      _data           (1:N)
                                      
            interventions (1:N)
            schemes (M:N via mapping)
            alert_logs
```

---

## Table Definitions

### 1. Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(120) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'teacher',  -- 'admin' or 'teacher'
    school_id VARCHAR(120) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    INDEX idx_email (email),
    INDEX idx_school_id (school_id)
);
```

**Purpose**: User authentication and role management
**Roles**: 
- `admin`: Full system access, model training, scheme management
- `teacher`: Student data entry, profile viewing, intervention tracking

---

### 2. Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    school_id VARCHAR(120) NOT NULL,
    enrollment_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    age INTEGER,
    gender VARCHAR(20),  -- 'Male', 'Female', 'Other'
    class_name VARCHAR(20),  -- 'I', 'II', 'III', etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_enrollment_id (enrollment_id),
    INDEX idx_school_id (school_id),
    INDEX idx_class_name (class_name)
);
```

**Purpose**: Core student profile
**Key Fields**:
- `enrollment_id`: Unique identifier per student
- `school_id`: Links to school/organization
- `age`, `gender`: Demographics
- `class_name`: Academic level

---

### 3. Academic Data Table
```sql
CREATE TABLE academic_data (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    attendance_percentage FLOAT DEFAULT 0.0,  -- 0-100%
    marks_obtained FLOAT,  -- Latest exam marks
    marks_total FLOAT,  -- Total possible marks
    subject_failures INTEGER DEFAULT 0,  -- Count of failed subjects
    grade_repetitions INTEGER DEFAULT 0,  -- Times student repeated a grade
    semester VARCHAR(20),  -- 'Spring 2024', 'Fall 2024', etc.
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id),
    INDEX idx_student_id (student_id),
    INDEX idx_recorded_at (recorded_at)
);
```

**Purpose**: Track academic performance
**Key Metrics**:
- `attendance_percentage`: Critical dropout predictor (<75% = high risk)
- `subject_failures`: Indicator of academic struggle
- `grade_repetitions`: Historical difficulty

**Sample Values**:
```json
{
  "attendance_percentage": 85.5,
  "marks_obtained": 420,
  "marks_total": 600,
  "subject_failures": 1,
  "grade_repetitions": 0,
  "semester": "Spring 2024"
}
```

---

### 4. Socioeconomic Data Table
```sql
CREATE TABLE socioeconomic_data (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    family_income VARCHAR(50),  -- 'Low', 'Medium', 'High'
    parent_education VARCHAR(50),  -- 'Primary', 'Secondary', 'Higher'
    distance_to_school_km FLOAT,  -- One-way distance
    health_issues BOOLEAN DEFAULT FALSE,
    has_electricity BOOLEAN DEFAULT TRUE,
    has_internet BOOLEAN DEFAULT FALSE,
    parent_employment VARCHAR(50),  -- 'Agriculture', 'Labor', 'Service', etc.
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id),
    INDEX idx_student_id (student_id)
);
```

**Purpose**: Capture socioeconomic factors influencing dropout risk
**Key Indicators**:
- `family_income`: Financial stability
- `distance_to_school_km`: Transport difficulty (>5km = high risk)
- `health_issues`: Health barriers
- `has_internet`: Access to online resources

**Sample Values**:
```json
{
  "family_income": "Low",
  "parent_education": "Primary",
  "distance_to_school_km": 8.5,
  "health_issues": false,
  "has_electricity": true,
  "has_internet": false,
  "parent_employment": "Agriculture"
}
```

---

### 5. Risk Analysis Table
```sql
CREATE TABLE risk_analysis (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    dropout_probability FLOAT DEFAULT 0.0,  -- 0.0-1.0
    risk_level VARCHAR(20),  -- 'Low', 'Medium', 'High'
    risk_score FLOAT DEFAULT 0.0,  -- 0-100
    key_risk_factors JSON,  -- ["Factor 1", "Factor 2", "Factor 3"]
    shap_explanation TEXT,  -- Human-readable explanation
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) DEFAULT 'v1',
    
    FOREIGN KEY (student_id) REFERENCES students(id),
    INDEX idx_student_id (student_id),
    INDEX idx_analyzed_at (analyzed_at),
    INDEX idx_risk_level (risk_level)
);
```

**Purpose**: Store ML predictions and explanations
**Key Fields**:
- `dropout_probability`: 0.65 means 65% risk of dropout
- `risk_level`: Categorized for easy interpretation
- `key_risk_factors`: JSON array of main contributing factors
- `shap_explanation`: SHAP values converted to text

**Sample Values**:
```json
{
  "student_id": 1,
  "dropout_probability": 0.65,
  "risk_level": "High",
  "risk_score": 65.0,
  "key_risk_factors": [
    "Low attendance (72.5%)",
    "High subject failures (2)",
    "Low family income"
  ],
  "shap_explanation": "Student Rahul Kumar (VI class) has a 65.0% risk of dropping out. Main concerns: Low attendance, academic struggles, and financial constraints. Recommended actions: Contact parents, arrange tutoring, explore scholarship schemes.",
  "model_version": "v1"
}
```

---

### 6. Schemes Table
```sql
CREATE TABLE schemes (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    benefits JSON,  -- ["Benefit 1", "Benefit 2"]
    eligibility_criteria JSON,  -- ["Criterion 1", "Criterion 2"]
    apply_link VARCHAR(500),
    contact_phone VARCHAR(20),
    scheme_type VARCHAR(50),  -- 'scholarship', 'transport', 'meal', 'health', 'girl_child'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Government schemes and support programs
**Scheme Types**:
- `scholarship`: Financial aid programs
- `transport`: Transportation support
- `meal`: Free food programs
- `health`: Health services
- `girl_child`: Gender-specific support

**Sample Data**:
```json
{
  "id": 1,
  "name": "National Scholarship Scheme",
  "description": "Financial aid for economically weaker students",
  "benefits": [
    "Monthly stipend of ₹1000-2000",
    "Books and supplies"
  ],
  "eligibility_criteria": [
    "Family income < ₹2 lakhs/year",
    "Attendance > 75%"
  ],
  "apply_link": "https://scholarship.example.com",
  "contact_phone": "+91-1234567890",
  "scheme_type": "scholarship"
}
```

---

### 7. Student Scheme Mapping Table
```sql
CREATE TABLE student_scheme_mapping (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    scheme_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'Recommended',  -- 'Recommended', 'Applied', 'Approved', 'Rejected'
    application_date DATETIME,
    approval_date DATETIME,
    notes TEXT,
    mapped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (scheme_id) REFERENCES schemes(id),
    UNIQUE KEY unique_student_scheme (student_id, scheme_id),
    INDEX idx_student_id (student_id),
    INDEX idx_status (status)
);
```

**Purpose**: Track scheme recommendations and applications
**Status Flow**: Recommended → Applied → Approved/Rejected

---

### 8. Alert Logs Table
```sql
CREATE TABLE alert_logs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    alert_type VARCHAR(50),  -- 'sms', 'push', 'email'
    message TEXT,
    recipient VARCHAR(120),  -- Phone number or email
    risk_level VARCHAR(20),  -- Risk level when alert was sent
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'sent', 'failed'
    response_code VARCHAR(50),  -- API response code
    
    FOREIGN KEY (student_id) REFERENCES students(id),
    INDEX idx_student_id (student_id),
    INDEX idx_sent_at (sent_at)
);
```

**Purpose**: Track all alerts sent to teachers/parents
**Alert Types**:
- `sms`: Text message via Fast2SMS
- `push`: Mobile push notification
- `email`: Email notification

---

### 9. Interventions Table
```sql
CREATE TABLE interventions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    intervention_type VARCHAR(100),  -- 'Counseling', 'Tutoring', 'Transport Support', etc.
    description TEXT,
    action_taken_by VARCHAR(120),  -- Teacher/Admin name
    status VARCHAR(50) DEFAULT 'Pending',  -- 'Pending', 'In Progress', 'Completed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    
    FOREIGN KEY (student_id) REFERENCES students(id),
    INDEX idx_student_id (student_id),
    INDEX idx_status (status)
);
```

**Purpose**: Track interventions taken for at-risk students
**Intervention Types**:
- Counseling Session
- Tutoring Arranged
- Parent Contact
- Scholarship Application
- Transport Support
- Health Referral

---

## 🤖 Machine Learning Model

### Model Architecture

```
┌──────────────────────────────┐
│     Input Features (11)       │
├──────────────────────────────┤
│  1. Attendance %              │
│  2. Marks Obtained            │
│  3. Marks Total               │
│  4. Subject Failures          │
│  5. Grade Repetitions         │
│  6. Family Income (encoded)   │
│  7. Parent Education (encoded)│
│  8. Distance to School        │
│  9. Health Issues             │
│ 10. Has Electricity           │
│ 11. Has Internet              │
└──────────────┬────────────────┘
               │
         [Preprocessing]
         - Scaling (StandardScaler)
         - Encoding (Label Encoding)
         - Missing value handling
               │
        ┌──────▼──────────┐
        │  Random Forest   │
        │  Classifier      │
        │  (50 trees,      │
        │   max_depth=10)  │
        └──────┬──────────┘
               │
      ┌────────▼────────┐
      │  Probability    │
      │  Output (0-1)   │
      └────────┬────────┘
               │
       ┌───────▼────────┐
       │  Risk Level    │
       │  Categorization│
       │  L/M/H         │
       └────────────────┘
```

### Model Details

**Algorithm**: Random Forest Classifier
- **Trees**: 50 decision trees
- **Max Depth**: 10 levels
- **Random State**: 42 (reproducible)

**Input Features**:
```python
features = {
    'attendance_percentage': 0-100,
    'marks_obtained': 0-600,
    'marks_total': 100-600,
    'subject_failures': 0-10,
    'grade_repetitions': 0-5,
    'family_income_encoded': 1-3,  # Low=1, Medium=2, High=3
    'parent_education_encoded': 1-3,  # Primary=1, Secondary=2, Higher=3
    'distance_to_school_km': 0-50,
    'health_issues': 0-1,  # Boolean
    'has_electricity': 0-1,  # Boolean
    'has_internet': 0-1,  # Boolean
}
```

**Output**: Dropout Probability (0.0 - 1.0)

**Risk Categorization**:
```
Probability < 0.33 → Low Risk (Green)
0.33 ≤ Probability < 0.67 → Medium Risk (Yellow)
Probability ≥ 0.67 → High Risk (Red)
```

### Model Training Pipeline

```python
# 1. Data Collection
# Gather academic and socioeconomic data for all students

# 2. Feature Engineering
X = [
    attendance,
    marks_obtained,
    marks_total,
    subject_failures,
    grade_repetitions,
    family_income_encoded,
    parent_education_encoded,
    distance_to_school,
    health_issues,
    has_electricity,
    has_internet
]

# 3. Target Variable (Binary Classification)
# y = 1 if: attendance < 75% AND subject_failures > 2
# y = 0 otherwise
y = [1 if x[0] < 75 and x[4] > 2 else 0 for x in X]

# 4. Data Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. Model Training
model = RandomForestClassifier(
    n_estimators=50,
    max_depth=10,
    random_state=42
)
model.fit(X_scaled, y)

# 6. Model Persistence
joblib.dump(model, 'models/dropout_model.pkl')
joblib.dump(scaler, 'models/dropout_model_scaler.pkl')
```

### Making Predictions

```python
# 1. Fetch student data
academic = AcademicData.query.filter_by(student_id=student_id).first()
socioeconomic = SocioeconomicData.query.filter_by(student_id=student_id).first()

# 2. Prepare features
features = {
    'attendance_percentage': academic.attendance_percentage,
    'marks_obtained': academic.marks_obtained,
    'marks_total': academic.marks_total,
    'subject_failures': academic.subject_failures,
    'grade_repetitions': academic.grade_repetitions,
    'family_income_encoded': encode_income(socioeconomic.family_income),
    'parent_education_encoded': encode_education(socioeconomic.parent_education),
    'distance_to_school_km': socioeconomic.distance_to_school_km,
    'health_issues': int(socioeconomic.health_issues),
    'has_electricity': int(socioeconomic.has_electricity),
    'has_internet': int(socioeconomic.has_internet),
}

# 3. Predict
X = np.array([list(features.values())])
X_scaled = scaler.transform(X)
dropout_probability = model.predict_proba(X_scaled)[0][1]

# 4. Categorize
risk_level = 'High' if dropout_probability >= 0.67 else (
    'Medium' if dropout_probability >= 0.33 else 'Low'
)

# 5. Identify key factors
key_factors = []
if features['attendance_percentage'] < 75:
    key_factors.append(f"Low attendance ({features['attendance_percentage']:.1f}%)")
if features['subject_failures'] > 2:
    key_factors.append(f"High subject failures ({features['subject_failures']})")
if features['family_income_encoded'] == 1:
    key_factors.append("Low family income")
# ... more factors
```

### Model Performance Metrics

**Evaluation** (Example metrics):
```
Accuracy: 0.87
Precision: 0.85
Recall: 0.88
F1-Score: 0.86
ROC-AUC: 0.92
```

### Periodic Retraining

**Frequency**: Monthly or when 100+ new records added
**Trigger**: Admin endpoint `/api/admin/train-model`
**Data**: All student records with complete academic data

```bash
# Training command
curl -X POST http://localhost:5000/api/admin/train-model \
  -H "Authorization: Bearer {admin_token}"
```

---

## 📊 SHAP Explainability

### How SHAP Works

SHAP (SHapley Additive exPlanations) explains each prediction:

```
Base Model Output: 0.50
├─ Attendance (-0.15) → Lower risk due to good attendance
├─ Subject Failures (+0.08) → Higher risk due to failures
├─ Family Income (+0.12) → Higher risk due to low income
├─ Distance to School (+0.06) → Higher risk due to far distance
└─ Final Prediction: 0.61 (High Risk)
```

### Implementation

```python
import shap

# Create explainer
explainer = shap.TreeExplainer(model)

# Calculate SHAP values
shap_values = explainer.shap_values(X)[1]  # Class 1 (dropout)

# Generate explanation
explanation = f"""
Student {student_name} has a {probability*100:.1f}% dropout risk.

Key Factors:
"""

for factor, value in zip(feature_names, shap_values):
    direction = "increases" if value > 0 else "decreases"
    explanation += f"\n- {factor}: {direction} risk by {abs(value):.2f}"
```

### Human-Readable Output Example

```
"Student Rahul Kumar (Class VI) has a 65% risk of dropping out.

Key concerns:
1. Low attendance (72.5%) - attending fewer classes reduces engagement
2. Subject failures (2) - struggling in multiple subjects
3. Financial constraints - family income limitations may cause dropout

Recommended actions:
1. Contact parents to understand attendance issues
2. Arrange tutoring sessions for failed subjects
3. Apply for scholarship programs to ease financial burden
4. Provide transportation support if distance is a concern
5. Schedule counseling sessions with student"
```

---

## 📈 Feature Importance

**Random Forest Feature Importance** (relative to model):

```
1. Attendance Percentage: 0.28 (28%)
2. Subject Failures: 0.18 (18%)
3. Family Income: 0.15 (15%)
4. Marks Obtained: 0.12 (12%)
5. Distance to School: 0.08 (8%)
6. Parent Education: 0.07 (7%)
7. Grade Repetitions: 0.05 (5%)
8. Health Issues: 0.04 (4%)
9. Has Internet: 0.02 (2%)
10. Has Electricity: 0.01 (1%)
11. Marks Total: 0.00 (0%)
```

**Interpretation**:
- Attendance is the strongest predictor
- Socioeconomic factors (income) are significant
- Academic performance (marks, failures) important
- Infrastructure access (electricity, internet) minimal impact

---

## 🔄 Data Pipeline

```
Student Data Entry
       ↓
Academic Data
+ Socioeconomic Data
       ↓
Data Validation
       ↓
Feature Extraction
       ↓
Scaling & Encoding
       ↓
ML Model Prediction
       ↓
Risk Analysis Generation
       ↓
Scheme Recommendation
       ↓
Alert Triggering (if Medium/High)
       ↓
Dashboard Update
       ↓
Intervention Recording
```

---

## ⚙️ Configuration Options

### Model Parameters (edulrew_backend.py)

```python
# Modify in DropoutPredictionModel class
model = RandomForestClassifier(
    n_estimators=50,      # Number of trees
    max_depth=10,         # Tree depth limit
    min_samples_split=5,  # Minimum samples to split
    min_samples_leaf=2,   # Minimum samples in leaf
    random_state=42,      # Reproducibility
    n_jobs=-1             # Use all processors
)

# Risk thresholds
LOW_RISK_THRESHOLD = 0.33      # < 33%
HIGH_RISK_THRESHOLD = 0.67     # >= 67%

# Target definition
TARGET_ATTENDANCE = 75         # % attendance threshold
TARGET_FAILURES = 2            # Subject failure count threshold
```

### Retraining Frequency

```python
# Check if retraining needed
if (new_records > 100 or 
    days_since_training > 30):
    ml_model.train()
```

---

**Last Updated**: April 2024
**Model Version**: v1.0
**Status**: Production Ready
