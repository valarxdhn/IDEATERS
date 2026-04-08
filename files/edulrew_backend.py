"""
EduDew - AI Rural Student Dropout Early Warning System
Backend Application (Flask)
Tagline: High Aspirations, Humble Beginnings
"""

from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
import os
import joblib
import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import requests
import logging
from enum import Enum

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///edulrew.db')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ENUMS & CONSTANTS ====================
class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

# ==================== DATABASE MODELS ====================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.TEACHER)
    school_id = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'school_id': self.school_id,
        }


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.String(120), nullable=False, index=True)
    enrollment_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    class_name = db.Column(db.String(20), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    academic_data = db.relationship('AcademicData', backref='student', lazy=True, cascade='all, delete-orphan')
    socioeconomic_data = db.relationship('SocioeconomicData', backref='student', lazy=True, cascade='all, delete-orphan')
    risk_analysis = db.relationship('RiskAnalysis', backref='student', lazy=True, cascade='all, delete-orphan')
    interventions = db.relationship('Intervention', backref='student', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'school_id': self.school_id,
            'enrollment_id': self.enrollment_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'class_name': self.class_name,
        }
        if include_relations:
            data['academic_data'] = [a.to_dict() for a in self.academic_data]
            data['socioeconomic_data'] = [s.to_dict() for s in self.socioeconomic_data]
            data['risk_analysis'] = [r.to_dict() for r in self.risk_analysis]
        return data


class AcademicData(db.Model):
    __tablename__ = 'academic_data'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    attendance_percentage = db.Column(db.Float, default=0.0)
    marks_obtained = db.Column(db.Float)
    marks_total = db.Column(db.Float)
    subject_failures = db.Column(db.Integer, default=0)
    grade_repetitions = db.Column(db.Integer, default=0)
    semester = db.Column(db.String(20))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'attendance_percentage': self.attendance_percentage,
            'marks_obtained': self.marks_obtained,
            'marks_total': self.marks_total,
            'subject_failures': self.subject_failures,
            'grade_repetitions': self.grade_repetitions,
            'semester': self.semester,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }


class SocioeconomicData(db.Model):
    __tablename__ = 'socioeconomic_data'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    family_income = db.Column(db.String(50))  # Low, Medium, High
    parent_education = db.Column(db.String(50))  # Primary, Secondary, Higher
    distance_to_school_km = db.Column(db.Float)
    health_issues = db.Column(db.Boolean, default=False)
    has_electricity = db.Column(db.Boolean, default=True)
    has_internet = db.Column(db.Boolean, default=False)
    parent_employment = db.Column(db.String(50))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'family_income': self.family_income,
            'parent_education': self.parent_education,
            'distance_to_school_km': self.distance_to_school_km,
            'health_issues': self.health_issues,
            'has_electricity': self.has_electricity,
            'has_internet': self.has_internet,
            'parent_employment': self.parent_employment,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }


class RiskAnalysis(db.Model):
    __tablename__ = 'risk_analysis'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    dropout_probability = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default=RiskLevel.LOW)  # Low, Medium, High
    risk_score = db.Column(db.Float, default=0.0)
    key_risk_factors = db.Column(db.JSON)  # JSON list of main risk factors
    shap_explanation = db.Column(db.Text)  # Human-readable explanation
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_version = db.Column(db.String(50), default='v1')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'dropout_probability': round(self.dropout_probability, 4),
            'risk_level': self.risk_level,
            'risk_score': round(self.risk_score, 4),
            'key_risk_factors': self.key_risk_factors,
            'shap_explanation': self.shap_explanation,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
            'model_version': self.model_version,
        }


class Scheme(db.Model):
    __tablename__ = 'schemes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    benefits = db.Column(db.JSON)
    eligibility_criteria = db.Column(db.JSON)
    apply_link = db.Column(db.String(500))
    contact_phone = db.Column(db.String(20))
    scheme_type = db.Column(db.String(50))  # scholarship, transport, meal, health, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'benefits': self.benefits,
            'eligibility_criteria': self.eligibility_criteria,
            'apply_link': self.apply_link,
            'contact_phone': self.contact_phone,
            'scheme_type': self.scheme_type,
        }


class StudentSchemeMapping(db.Model):
    __tablename__ = 'student_scheme_mapping'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('schemes.id'), nullable=False, index=True)
    status = db.Column(db.String(50), default='Recommended')  # Recommended, Applied, Approved, Rejected
    application_date = db.Column(db.DateTime)
    approval_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    mapped_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student')
    scheme = db.relationship('Scheme')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'scheme_id': self.scheme_id,
            'scheme_name': self.scheme.name if self.scheme else None,
            'status': self.status,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'notes': self.notes,
        }


class AlertLog(db.Model):
    __tablename__ = 'alert_logs'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    alert_type = db.Column(db.String(50))  # sms, push, email
    message = db.Column(db.Text)
    recipient = db.Column(db.String(120))
    risk_level = db.Column(db.String(20))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_status = db.Column(db.String(50), default='pending')
    response_code = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'recipient': self.recipient,
            'risk_level': self.risk_level,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'sent_status': self.sent_status,
        }


class Intervention(db.Model):
    __tablename__ = 'interventions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    intervention_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    action_taken_by = db.Column(db.String(120))
    status = db.Column(db.String(50), default='Pending')  # Pending, In Progress, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'intervention_type': self.intervention_type,
            'description': self.description,
            'action_taken_by': self.action_taken_by,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


# ==================== ML MODULE ====================
class DropoutPredictionModel:
    """Machine Learning Model for Dropout Prediction"""
    
    def __init__(self, model_path='models/dropout_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_model()

    def load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.model_path.replace('.pkl', '_scaler.pkl'))
                logger.info("Model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load model: {e}. Will train new model.")

    def prepare_features(self, academic, socioeconomic):
        """Prepare features for prediction"""
        features = {
            'attendance_percentage': academic.get('attendance_percentage', 0),
            'marks_obtained': academic.get('marks_obtained', 0),
            'marks_total': academic.get('marks_total', 100),
            'subject_failures': academic.get('subject_failures', 0),
            'grade_repetitions': academic.get('grade_repetitions', 0),
            'family_income_encoded': self._encode_income(socioeconomic.get('family_income')),
            'parent_education_encoded': self._encode_education(socioeconomic.get('parent_education')),
            'distance_to_school_km': socioeconomic.get('distance_to_school_km', 0),
            'health_issues': int(socioeconomic.get('health_issues', False)),
            'has_electricity': int(socioeconomic.get('has_electricity', True)),
            'has_internet': int(socioeconomic.get('has_internet', False)),
        }
        return features

    @staticmethod
    def _encode_income(income):
        mapping = {'Low': 1, 'Medium': 2, 'High': 3}
        return mapping.get(income, 0)

    @staticmethod
    def _encode_education(education):
        mapping = {'Primary': 1, 'Secondary': 2, 'Higher': 3}
        return mapping.get(education, 0)

    def predict(self, features):
        """Make dropout probability prediction"""
        if self.model is None:
            return 0.5, RiskLevel.MEDIUM, []
        
        feature_list = [
            features['attendance_percentage'],
            features['marks_obtained'],
            features['marks_total'],
            features['subject_failures'],
            features['grade_repetitions'],
            features['family_income_encoded'],
            features['parent_education_encoded'],
            features['distance_to_school_km'],
            features['health_issues'],
            features['has_electricity'],
            features['has_internet'],
        ]
        
        X = np.array([feature_list])
        if self.scaler:
            X = self.scaler.transform(X)
        
        dropout_prob = self.model.predict_proba(X)[0][1]
        risk_level = self._categorize_risk(dropout_prob)
        risk_factors = self._identify_risk_factors(features)
        
        return dropout_prob, risk_level, risk_factors

    @staticmethod
    def _categorize_risk(probability):
        """Categorize risk level based on probability"""
        if probability < 0.33:
            return RiskLevel.LOW
        elif probability < 0.67:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    @staticmethod
    def _identify_risk_factors(features):
        """Identify main risk factors"""
        factors = []
        
        if features['attendance_percentage'] < 75:
            factors.append(f"Low attendance ({features['attendance_percentage']:.1f}%)")
        if features['subject_failures'] > 2:
            factors.append(f"High subject failures ({features['subject_failures']})")
        if features['family_income_encoded'] == 1:
            factors.append("Low family income")
        if features['distance_to_school_km'] > 5:
            factors.append(f"High distance from school ({features['distance_to_school_km']:.1f} km)")
        if features['health_issues']:
            factors.append("Health issues affecting attendance")
        
        return factors[:3]  # Top 3 factors

    def train(self):
        """Train model with historical data"""
        try:
            # Fetch all student data
            students = Student.query.all()
            if len(students) < 10:
                logger.warning("Not enough data to train model")
                return False
            
            X, y = [], []
            for student in students:
                if not student.academic_data or not student.socioeconomic_data:
                    continue
                
                academic = student.academic_data[0].to_dict()
                socioeconomic = student.socioeconomic_data[0].to_dict()
                
                features = self.prepare_features(academic, socioeconomic)
                feature_list = [
                    features['attendance_percentage'],
                    features['marks_obtained'],
                    features['marks_total'],
                    features['subject_failures'],
                    features['grade_repetitions'],
                    features['family_income_encoded'],
                    features['parent_education_encoded'],
                    features['distance_to_school_km'],
                    features['health_issues'],
                    features['has_electricity'],
                    features['has_internet'],
                ]
                X.append(feature_list)
            
            if len(X) < 10:
                logger.warning("Not enough valid data to train")
                return False
            
            X = np.array(X)
            # Simple target: high dropout risk if attendance < 75% AND failures > 2
            y = np.array([1 if x[0] < 75 and x[4] > 2 else 0 for x in X])
            
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            self.model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
            self.model.fit(X_scaled, y)
            
            # Save model
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.model_path.replace('.pkl', '_scaler.pkl'))
            
            logger.info("Model trained and saved successfully")
            return True
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False


# Initialize ML model
ml_model = DropoutPredictionModel()

# ==================== AUTHENTICATION ROUTES ====================
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not all([data.get('email'), data.get('password'), data.get('name')]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        user = User(
            email=data['email'],
            name=data['name'],
            role=data.get('role', UserRole.TEACHER),
            school_id=data.get('school_id', 'default'),
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not all([data.get('email'), data.get('password')]):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.verify_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403
        
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== STUDENT ROUTES ====================
@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get all students for the school"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        class_name = request.args.get('class')
        gender = request.args.get('gender')
        risk_level = request.args.get('risk_level')
        
        query = Student.query.filter_by(school_id=user.school_id)
        
        if class_name:
            query = query.filter_by(class_name=class_name)
        if gender:
            query = query.filter_by(gender=gender)
        
        students = query.all()
        
        # Add latest risk analysis
        for student in students:
            latest_risk = RiskAnalysis.query.filter_by(student_id=student.id).order_by(
                RiskAnalysis.analyzed_at.desc()
            ).first()
            student.latest_risk = latest_risk.to_dict() if latest_risk else None
        
        if risk_level:
            students = [s for s in students if s.latest_risk and s.latest_risk['risk_level'] == risk_level]
        
        return jsonify({
            'count': len(students),
            'students': [s.to_dict() for s in students]
        }), 200
    
    except Exception as e:
        logger.error(f"Get students error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_profile(student_id):
    """Get detailed student profile"""
    try:
        student = Student.query.get(student_id)
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        latest_academic = AcademicData.query.filter_by(student_id=student_id).order_by(
            AcademicData.recorded_at.desc()
        ).first()
        
        latest_socioeconomic = SocioeconomicData.query.filter_by(student_id=student_id).order_by(
            SocioeconomicData.recorded_at.desc()
        ).first()
        
        latest_risk = RiskAnalysis.query.filter_by(student_id=student_id).order_by(
            RiskAnalysis.analyzed_at.desc()
        ).first()
        
        risk_history = RiskAnalysis.query.filter_by(student_id=student_id).order_by(
            RiskAnalysis.analyzed_at.asc()
        ).limit(12).all()
        
        interventions = Intervention.query.filter_by(student_id=student_id).order_by(
            Intervention.created_at.desc()
        ).limit(5).all()
        
        schemes = StudentSchemeMapping.query.filter_by(student_id=student_id).all()
        
        return jsonify({
            'student': student.to_dict(),
            'academic_data': latest_academic.to_dict() if latest_academic else None,
            'socioeconomic_data': latest_socioeconomic.to_dict() if latest_socioeconomic else None,
            'risk_analysis': latest_risk.to_dict() if latest_risk else None,
            'risk_history': [r.to_dict() for r in risk_history],
            'interventions': [i.to_dict() for i in interventions],
            'schemes': [s.to_dict() for s in schemes],
        }), 200
    
    except Exception as e:
        logger.error(f"Get student profile error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/students', methods=['POST'])
@jwt_required()
def create_student():
    """Create a new student record"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not all([data.get('name'), data.get('enrollment_id'), data.get('class_name')]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if Student.query.filter_by(enrollment_id=data['enrollment_id']).first():
            return jsonify({'error': 'Enrollment ID already exists'}), 409
        
        student = Student(
            school_id=user.school_id,
            enrollment_id=data['enrollment_id'],
            name=data['name'],
            age=data.get('age'),
            gender=data.get('gender'),
            class_name=data.get('class_name'),
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student created successfully',
            'student': student.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Create student error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<int:student_id>/academic', methods=['POST'])
@jwt_required()
def add_academic_data(student_id):
    """Add or update academic data for a student"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        academic = AcademicData(
            student_id=student_id,
            attendance_percentage=data.get('attendance_percentage', 0),
            marks_obtained=data.get('marks_obtained'),
            marks_total=data.get('marks_total'),
            subject_failures=data.get('subject_failures', 0),
            grade_repetitions=data.get('grade_repetitions', 0),
            semester=data.get('semester'),
        )
        
        db.session.add(academic)
        db.session.commit()
        
        # Trigger risk analysis
        analyze_student_risk(student_id)
        
        return jsonify({
            'message': 'Academic data added successfully',
            'data': academic.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Add academic data error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<int:student_id>/socioeconomic', methods=['POST'])
@jwt_required()
def add_socioeconomic_data(student_id):
    """Add or update socioeconomic data for a student"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        socioeconomic = SocioeconomicData(
            student_id=student_id,
            family_income=data.get('family_income'),
            parent_education=data.get('parent_education'),
            distance_to_school_km=data.get('distance_to_school_km', 0),
            health_issues=data.get('health_issues', False),
            has_electricity=data.get('has_electricity', True),
            has_internet=data.get('has_internet', False),
            parent_employment=data.get('parent_employment'),
        )
        
        db.session.add(socioeconomic)
        db.session.commit()
        
        # Trigger risk analysis
        analyze_student_risk(student_id)
        
        return jsonify({
            'message': 'Socioeconomic data added successfully',
            'data': socioeconomic.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Add socioeconomic data error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== RISK ANALYSIS & ML ROUTES ====================
def analyze_student_risk(student_id):
    """Analyze dropout risk for a student using ML model"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return False
        
        latest_academic = AcademicData.query.filter_by(student_id=student_id).order_by(
            AcademicData.recorded_at.desc()
        ).first()
        
        latest_socioeconomic = SocioeconomicData.query.filter_by(student_id=student_id).order_by(
            SocioeconomicData.recorded_at.desc()
        ).first()
        
        if not latest_academic or not latest_socioeconomic:
            return False
        
        academic_dict = latest_academic.to_dict()
        socioeconomic_dict = latest_socioeconomic.to_dict()
        
        features = ml_model.prepare_features(academic_dict, socioeconomic_dict)
        dropout_prob, risk_level, risk_factors = ml_model.predict(features)
        
        # Generate explanation
        explanation = generate_ai_explanation(student, academic_dict, risk_factors, dropout_prob)
        
        risk_analysis = RiskAnalysis(
            student_id=student_id,
            dropout_probability=dropout_prob,
            risk_level=risk_level,
            risk_score=dropout_prob * 100,
            key_risk_factors=risk_factors,
            shap_explanation=explanation,
        )
        
        db.session.add(risk_analysis)
        db.session.commit()
        
        # Send alert if medium or high risk
        if risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
            send_alert_sms(student, risk_level, explanation)
        
        # Recommend schemes
        recommend_schemes(student_id, socioeconomic_dict)
        
        return True
    
    except Exception as e:
        logger.error(f"Risk analysis error: {e}")
        return False


@app.route('/api/students/<int:student_id>/analyze-risk', methods=['POST'])
@jwt_required()
def trigger_risk_analysis(student_id):
    """Manually trigger risk analysis for a student"""
    try:
        success = analyze_student_risk(student_id)
        
        if success:
            latest_risk = RiskAnalysis.query.filter_by(student_id=student_id).order_by(
                RiskAnalysis.analyzed_at.desc()
            ).first()
            
            return jsonify({
                'message': 'Risk analysis completed',
                'risk_analysis': latest_risk.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Insufficient data for analysis'}), 400
    
    except Exception as e:
        logger.error(f"Trigger risk analysis error: {e}")
        return jsonify({'error': str(e)}), 500


def generate_ai_explanation(student, academic_data, risk_factors, probability):
    """Generate human-readable AI explanation for non-technical users"""
    explanation = f"Student {student.name} ({student.class_name} class) has a {probability*100:.1f}% risk of dropping out.\n\n"
    
    if probability < 0.33:
        explanation += "This student is at LOW RISK. They are performing well academically and have good attendance. Continue monitoring their progress.\n\n"
    elif probability < 0.67:
        explanation += "This student is at MEDIUM RISK. They need attention and support to prevent dropout.\n\n"
    else:
        explanation += "This student is at HIGH RISK of dropping out. Immediate intervention is required.\n\n"
    
    explanation += "Key concerns:\n"
    for i, factor in enumerate(risk_factors, 1):
        explanation += f"{i}. {factor}\n"
    
    explanation += "\nRecommended actions:\n"
    if "Low attendance" in str(risk_factors):
        explanation += "- Contact parents to understand attendance issues\n"
        explanation += "- Provide transportation support if distance is a concern\n"
    if "High subject failures" in str(risk_factors):
        explanation += "- Arrange tutoring sessions\n"
        explanation += "- Provide remedial classes\n"
    if "Low family income" in str(risk_factors):
        explanation += "- Apply for financial assistance schemes\n"
        explanation += "- Explore scholarship opportunities\n"
    
    return explanation


# ==================== SCHEME ROUTES ====================
@app.route('/api/schemes', methods=['GET'])
@jwt_required()
def get_schemes():
    """Get all available schemes"""
    try:
        scheme_type = request.args.get('type')
        
        query = Scheme.query
        if scheme_type:
            query = query.filter_by(scheme_type=scheme_type)
        
        schemes = query.all()
        return jsonify({
            'count': len(schemes),
            'schemes': [s.to_dict() for s in schemes]
        }), 200
    
    except Exception as e:
        logger.error(f"Get schemes error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/schemes', methods=['POST'])
@jwt_required()
def create_scheme():
    """Create a new scheme (Admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        scheme = Scheme(
            name=data.get('name'),
            description=data.get('description'),
            benefits=data.get('benefits'),
            eligibility_criteria=data.get('eligibility_criteria'),
            apply_link=data.get('apply_link'),
            contact_phone=data.get('contact_phone'),
            scheme_type=data.get('scheme_type'),
        )
        
        db.session.add(scheme)
        db.session.commit()
        
        return jsonify({
            'message': 'Scheme created successfully',
            'scheme': scheme.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Create scheme error: {e}")
        return jsonify({'error': str(e)}), 500


def recommend_schemes(student_id, socioeconomic_data):
    """Rule-based recommendation engine for schemes"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return
        
        # Clear existing recommendations
        StudentSchemeMapping.query.filter_by(student_id=student_id, status='Recommended').delete()
        
        schemes = Scheme.query.all()
        
        for scheme in schemes:
            should_recommend = False
            
            if scheme.scheme_type == 'scholarship':
                if socioeconomic_data.get('family_income') == 'Low':
                    should_recommend = True
            
            elif scheme.scheme_type == 'transport':
                if socioeconomic_data.get('distance_to_school_km', 0) > 5:
                    should_recommend = True
            
            elif scheme.scheme_type == 'girl_child':
                if student.gender == 'Female':
                    should_recommend = True
            
            elif scheme.scheme_type == 'health':
                if socioeconomic_data.get('health_issues'):
                    should_recommend = True
            
            elif scheme.scheme_type == 'meal':
                if socioeconomic_data.get('family_income') == 'Low':
                    should_recommend = True
            
            if should_recommend:
                existing = StudentSchemeMapping.query.filter_by(
                    student_id=student_id,
                    scheme_id=scheme.id
                ).first()
                
                if not existing:
                    mapping = StudentSchemeMapping(
                        student_id=student_id,
                        scheme_id=scheme.id,
                        status='Recommended'
                    )
                    db.session.add(mapping)
        
        db.session.commit()
    
    except Exception as e:
        logger.error(f"Scheme recommendation error: {e}")


@app.route('/api/students/<int:student_id>/schemes', methods=['GET'])
@jwt_required()
def get_student_schemes(student_id):
    """Get recommended and applied schemes for a student"""
    try:
        mappings = StudentSchemeMapping.query.filter_by(student_id=student_id).all()
        
        return jsonify({
            'count': len(mappings),
            'schemes': [m.to_dict() for m in mappings]
        }), 200
    
    except Exception as e:
        logger.error(f"Get student schemes error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/student-schemes/<int:mapping_id>', methods=['PUT'])
@jwt_required()
def update_scheme_status(mapping_id):
    """Update status of scheme application"""
    try:
        mapping = StudentSchemeMapping.query.get(mapping_id)
        if not mapping:
            return jsonify({'error': 'Mapping not found'}), 404
        
        data = request.get_json()
        mapping.status = data.get('status', mapping.status)
        
        if mapping.status == 'Applied':
            mapping.application_date = datetime.utcnow()
        elif mapping.status == 'Approved':
            mapping.approval_date = datetime.utcnow()
        
        mapping.notes = data.get('notes', mapping.notes)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Scheme status updated',
            'mapping': mapping.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Update scheme status error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ALERT ROUTES ====================
def send_alert_sms(student, risk_level, explanation):
    """Send SMS alert to school/parents using Fast2SMS API"""
    try:
        # Get teacher phone (from parent or teacher in production)
        # This is a demo implementation
        
        if risk_level == RiskLevel.HIGH:
            message = f"URGENT: {student.name} ({student.class_name}) is at HIGH dropout risk. Please take immediate action. Contact school for details."
        else:
            message = f"ALERT: {student.name} ({student.class_name}) needs attention. Risk level: {risk_level}. Please monitor."
        
        # Fast2SMS API integration (requires API key)
        # api_key = os.getenv('FAST2SMS_API_KEY')
        # if api_key:
        #     response = requests.post(
        #         'https://www.fast2sms.com/dev/bulkV2',
        #         params={'authorization': api_key},
        #         json={
        #             'route': 'v3',
        #             'numbers': teacher_phone,
        #             'message': message
        #         }
        #     )
        
        alert_log = AlertLog(
            student_id=student.id,
            alert_type='sms',
            message=message,
            recipient='teacher_phone',
            risk_level=risk_level,
            sent_status='pending'
        )
        
        db.session.add(alert_log)
        db.session.commit()
        
        logger.info(f"Alert logged for student {student.id}")
    
    except Exception as e:
        logger.error(f"Alert send error: {e}")


@app.route('/api/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get alert logs"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get alerts for students in the school
        student_ids = [s.id for s in Student.query.filter_by(school_id=user.school_id).all()]
        
        alerts = AlertLog.query.filter(AlertLog.student_id.in_(student_ids)).order_by(
            AlertLog.sent_at.desc()
        ).limit(100).all()
        
        return jsonify({
            'count': len(alerts),
            'alerts': [a.to_dict() for a in alerts]
        }), 200
    
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== DASHBOARD ROUTES ====================
@app.route('/api/dashboard/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """Get dashboard overview data"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        students = Student.query.filter_by(school_id=user.school_id).all()
        student_ids = [s.id for s in students]
        
        total_students = len(students)
        
        risk_analyses = RiskAnalysis.query.filter(
            RiskAnalysis.student_id.in_(student_ids)
        ).order_by(RiskAnalysis.analyzed_at.desc()).distinct(
            RiskAnalysis.student_id
        ).all()
        
        high_risk_count = len([r for r in risk_analyses if r.risk_level == RiskLevel.HIGH])
        medium_risk_count = len([r for r in risk_analyses if r.risk_level == RiskLevel.MEDIUM])
        low_risk_count = len([r for r in risk_analyses if r.risk_level == RiskLevel.LOW])
        
        alerts_count = AlertLog.query.filter(
            AlertLog.student_id.in_(student_ids)
        ).count()
        
        schemes_applied = StudentSchemeMapping.query.filter(
            StudentSchemeMapping.student_id.in_(student_ids)
        ).filter(StudentSchemeMapping.status == 'Applied').count()
        
        return jsonify({
            'total_students': total_students,
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': low_risk_count,
            'alerts_sent': alerts_count,
            'schemes_applied': schemes_applied,
        }), 200
    
    except Exception as e:
        logger.error(f"Dashboard overview error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/risk-distribution', methods=['GET'])
@jwt_required()
def get_risk_distribution():
    """Get risk distribution data"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        students = Student.query.filter_by(school_id=user.school_id).all()
        student_ids = [s.id for s in students]
        
        latest_risks = {}
        for student_id in student_ids:
            risk = RiskAnalysis.query.filter_by(student_id=student_id).order_by(
                RiskAnalysis.analyzed_at.desc()
            ).first()
            if risk:
                latest_risks[student_id] = risk.risk_level
        
        high = len([r for r in latest_risks.values() if r == RiskLevel.HIGH])
        medium = len([r for r in latest_risks.values() if r == RiskLevel.MEDIUM])
        low = len([r for r in latest_risks.values() if r == RiskLevel.LOW])
        
        return jsonify({
            'high': high,
            'medium': medium,
            'low': low,
        }), 200
    
    except Exception as e:
        logger.error(f"Risk distribution error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== INTERVENTION ROUTES ====================
@app.route('/api/students/<int:student_id>/interventions', methods=['POST'])
@jwt_required()
def add_intervention(student_id):
    """Add intervention record for a student"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        intervention = Intervention(
            student_id=student_id,
            intervention_type=data.get('intervention_type'),
            description=data.get('description'),
            action_taken_by=user.name,
            status=data.get('status', 'Pending'),
        )
        
        db.session.add(intervention)
        db.session.commit()
        
        return jsonify({
            'message': 'Intervention recorded',
            'intervention': intervention.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Add intervention error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/interventions/<int:intervention_id>', methods=['PUT'])
@jwt_required()
def update_intervention(intervention_id):
    """Update intervention status"""
    try:
        intervention = Intervention.query.get(intervention_id)
        if not intervention:
            return jsonify({'error': 'Intervention not found'}), 404
        
        data = request.get_json()
        intervention.status = data.get('status', intervention.status)
        
        if intervention.status == 'Completed':
            intervention.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Intervention updated',
            'intervention': intervention.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Update intervention error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== TRAINING ROUTES ====================
@app.route('/api/admin/train-model', methods=['POST'])
@jwt_required()
def train_model():
    """Train ML model with latest data (Admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        success = ml_model.train()
        
        if success:
            return jsonify({
                'message': 'Model trained successfully',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({'error': 'Model training failed'}), 500
    
    except Exception as e:
        logger.error(f"Train model error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


# ==================== INITIALIZATION ====================
def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Add sample schemes if not exist
        if Scheme.query.count() == 0:
            schemes = [
                Scheme(
                    name='National Scholarship Scheme',
                    description='Financial aid for economically weaker students',
                    benefits=['Monthly stipend of ₹1000-2000', 'Books and supplies'],
                    eligibility_criteria=['Family income < ₹2 lakhs/year', 'Attendance > 75%'],
                    apply_link='https://scholarship.example.com',
                    contact_phone='+91-1234567890',
                    scheme_type='scholarship'
                ),
                Scheme(
                    name='Girl Child Education Scheme',
                    description='Special support for girl students',
                    benefits=['Monthly allowance', 'Free textbooks', 'Sanitary hygiene products'],
                    eligibility_criteria=['Female student', 'Any economic status'],
                    apply_link='https://girlscheme.example.com',
                    contact_phone='+91-9876543210',
                    scheme_type='girl_child'
                ),
                Scheme(
                    name='Rural Transport Allowance',
                    description='Support for students with long distance commute',
                    benefits=['Monthly transport allowance of ₹500'],
                    eligibility_criteria=['Distance from school > 5 km'],
                    apply_link='https://transport.example.com',
                    contact_phone='+91-1122334455',
                    scheme_type='transport'
                ),
                Scheme(
                    name='Mid-Day Meal Scheme',
                    description='Free nutritious meals at school',
                    benefits=['Daily lunch', 'Breakfast'],
                    eligibility_criteria=['All students'],
                    apply_link='https://meal.example.com',
                    contact_phone='+91-5544332211',
                    scheme_type='meal'
                ),
                Scheme(
                    name='Health Support Programme',
                    description='Healthcare and medical support',
                    benefits=['Free medical checkup', 'Medicine support'],
                    eligibility_criteria=['Health issues', 'Need-based'],
                    apply_link='https://health.example.com',
                    contact_phone='+91-7788990011',
                    scheme_type='health'
                ),
            ]
            
            for scheme in schemes:
                db.session.add(scheme)
            
            db.session.commit()
            logger.info("Sample schemes added")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
