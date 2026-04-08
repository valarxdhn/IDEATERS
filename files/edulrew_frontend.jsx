"""
EduDew Frontend - React Application
Full-stack application for Rural Student Dropout Early Warning System
"""

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter
} from 'recharts';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

// ==================== CONTEXT & UTILITIES ====================
const AuthContext = React.createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchProfile();
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/profile`);
      setUser(response.data);
    } catch (error) {
      console.error('Profile fetch error:', error);
      logout();
    }
  };

  const login = async (email, password) => {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, { email, password });
    setToken(response.data.access_token);
    localStorage.setItem('token', response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const signup = async (email, password, name, role, school_id) => {
    const response = await axios.post(`${API_BASE_URL}/auth/signup`, {
      email, password, name, role, school_id
    });
    setToken(response.data.access_token);
    localStorage.setItem('token', response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => React.useContext(AuthContext);

// ==================== PROTECTED ROUTE ====================
const ProtectedRoute = ({ children }) => {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" />;
};

// ==================== LOGIN PAGE ====================
const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [role, setRole] = useState('teacher');
  const [schoolId, setSchoolId] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, signup } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await signup(email, password, name, role, schoolId);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="brand-name">🌱 EduDew</h1>
          <p className="brand-tagline">High Aspirations, Humble Beginnings</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}

          {!isLogin && (
            <>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required={!isLogin}
                  placeholder="Your full name"
                />
              </div>
              <div className="form-group">
                <label>School ID</label>
                <input
                  type="text"
                  value={schoolId}
                  onChange={(e) => setSchoolId(e.target.value)}
                  required={!isLogin}
                  placeholder="School identifier"
                />
              </div>
              <div className="form-group">
                <label>Role</label>
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="teacher">Teacher</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </>
          )}

          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your@email.com"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Processing...' : isLogin ? 'Sign In' : 'Create Account'}
          </button>

          <div className="auth-toggle">
            <p>
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="toggle-link"
              >
                {isLogin ? 'Sign Up' : 'Sign In'}
              </button>
            </p>
          </div>
        </form>

        <div className="demo-credentials">
          <p><strong>Demo Login:</strong></p>
          <p>Email: teacher@example.com | Password: password123</p>
          <p>Email: admin@example.com | Password: admin123</p>
        </div>
      </div>
    </div>
  );
};

// ==================== DASHBOARD ====================
const Dashboard = () => {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [selectedClass, setSelectedClass] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [overviewRes, riskRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/dashboard/overview`),
        axios.get(`${API_BASE_URL}/dashboard/risk-distribution`)
      ]);
      setOverview(overviewRes.data);
      setRiskData(riskRes.data);
    } catch (error) {
      console.error('Dashboard fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;

  const riskDistribution = [
    { name: 'Low Risk', value: riskData?.low || 0, fill: '#10b981' },
    { name: 'Medium Risk', value: riskData?.medium || 0, fill: '#f59e0b' },
    { name: 'High Risk', value: riskData?.high || 0, fill: '#ef4444' }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome, {user?.name}! 👋</h1>
        <p>EduDew - Dropout Early Warning System</p>
      </div>

      <div className="overview-cards">
        <Card
          title="Total Students"
          value={overview?.total_students || 0}
          icon="👥"
          color="blue"
        />
        <Card
          title="High Risk Students"
          value={overview?.high_risk_count || 0}
          icon="🚨"
          color="red"
        />
        <Card
          title="Medium Risk Students"
          value={overview?.medium_risk_count || 0}
          icon="⚠️"
          color="yellow"
        />
        <Card
          title="Alerts Sent"
          value={overview?.alerts_sent || 0}
          icon="📬"
          color="purple"
        />
        <Card
          title="Schemes Applied"
          value={overview?.schemes_applied || 0}
          icon="📋"
          color="green"
        />
      </div>

      <div className="dashboard-charts">
        <div className="chart-container">
          <h3>Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Risk Breakdown</h3>
          <div className="risk-breakdown">
            <div className="risk-item">
              <div className="risk-color low"></div>
              <span>Low: {riskData?.low || 0}</span>
            </div>
            <div className="risk-item">
              <div className="risk-color medium"></div>
              <span>Medium: {riskData?.medium || 0}</span>
            </div>
            <div className="risk-item">
              <div className="risk-color high"></div>
              <span>High: {riskData?.high || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== CARD COMPONENT ====================
const Card = ({ title, value, icon, color }) => {
  const colorClasses = {
    blue: 'card-blue',
    red: 'card-red',
    yellow: 'card-yellow',
    purple: 'card-purple',
    green: 'card-green'
  };

  return (
    <div className={`overview-card ${colorClasses[color]}`}>
      <div className="card-icon">{icon}</div>
      <div className="card-content">
        <p className="card-title">{title}</p>
        <p className="card-value">{value}</p>
      </div>
    </div>
  );
};

// ==================== STUDENT PROFILE PAGE ====================
const StudentProfile = ({ studentId }) => {
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchStudentProfile();
  }, [studentId]);

  const fetchStudentProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/students/${studentId}`);
      setStudent(response.data);
    } catch (error) {
      console.error('Profile fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading student profile...</div>;
  if (!student) return <div className="error">Student not found</div>;

  const risk = student.risk_analysis;

  return (
    <div className="student-profile">
      <div className="profile-header">
        <div className="student-card">
          <div className={`risk-badge ${risk?.risk_level.toLowerCase()}`}>
            {risk?.risk_level || 'No Data'}
          </div>
          <h2>{student.student.name}</h2>
          <p>Class: {student.student.class_name} | Gender: {student.student.gender}</p>
          <p>Enrollment ID: {student.student.enrollment_id}</p>
        </div>
      </div>

      <div className="tabs">
        {['overview', 'academic', 'socioeconomic', 'risk', 'schemes', 'interventions'].map(tab => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Age:</span>
                <span className="value">{student.student.age} years</span>
              </div>
              <div className="info-item">
                <span className="label">Enrollment ID:</span>
                <span className="value">{student.student.enrollment_id}</span>
              </div>
              <div className="info-item">
                <span className="label">School ID:</span>
                <span className="value">{student.student.school_id}</span>
              </div>
            </div>

            {risk && (
              <div className="risk-card">
                <h3>Risk Analysis</h3>
                <div className="risk-details">
                  <div className="risk-metric">
                    <span className="metric-label">Dropout Probability</span>
                    <span className="metric-value">{(risk.dropout_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="risk-metric">
                    <span className="metric-label">Risk Score</span>
                    <span className="metric-value">{risk.risk_score.toFixed(1)}</span>
                  </div>
                  <div className="risk-metric">
                    <span className="metric-label">Last Analyzed</span>
                    <span className="metric-value">{new Date(risk.analyzed_at).toLocaleDateString()}</span>
                  </div>
                </div>

                {risk.key_risk_factors && (
                  <div className="risk-factors">
                    <h4>Key Risk Factors</h4>
                    <ul>
                      {risk.key_risk_factors.map((factor, idx) => (
                        <li key={idx}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {risk.shap_explanation && (
                  <div className="ai-explanation">
                    <h4>AI Explanation</h4>
                    <p>{risk.shap_explanation}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'academic' && student.academic_data && (
          <div className="academic-section">
            <h3>Academic Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Attendance:</span>
                <span className="value">{student.academic_data.attendance_percentage}%</span>
              </div>
              <div className="info-item">
                <span className="label">Marks:</span>
                <span className="value">{student.academic_data.marks_obtained}/{student.academic_data.marks_total}</span>
              </div>
              <div className="info-item">
                <span className="label">Subject Failures:</span>
                <span className="value">{student.academic_data.subject_failures}</span>
              </div>
              <div className="info-item">
                <span className="label">Grade Repetitions:</span>
                <span className="value">{student.academic_data.grade_repetitions}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'socioeconomic' && student.socioeconomic_data && (
          <div className="socioeconomic-section">
            <h3>Socioeconomic Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Family Income:</span>
                <span className="value">{student.socioeconomic_data.family_income}</span>
              </div>
              <div className="info-item">
                <span className="label">Parent Education:</span>
                <span className="value">{student.socioeconomic_data.parent_education}</span>
              </div>
              <div className="info-item">
                <span className="label">Distance to School:</span>
                <span className="value">{student.socioeconomic_data.distance_to_school_km} km</span>
              </div>
              <div className="info-item">
                <span className="label">Health Issues:</span>
                <span className="value">{student.socioeconomic_data.health_issues ? 'Yes' : 'No'}</span>
              </div>
              <div className="info-item">
                <span className="label">Electricity:</span>
                <span className="value">{student.socioeconomic_data.has_electricity ? 'Yes' : 'No'}</span>
              </div>
              <div className="info-item">
                <span className="label">Internet:</span>
                <span className="value">{student.socioeconomic_data.has_internet ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'risk' && student.risk_history && (
          <div className="risk-chart-section">
            <h3>Risk Score History</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={student.risk_history}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="analyzed_at"
                  tickFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip
                  formatter={(value) => value.toFixed(2)}
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="risk_score"
                  stroke="#ef4444"
                  name="Risk Score"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'schemes' && (
          <div className="schemes-section">
            <h3>Recommended Schemes</h3>
            {student.schemes && student.schemes.length > 0 ? (
              <div className="schemes-grid">
                {student.schemes.map(scheme => (
                  <div key={scheme.id} className="scheme-card">
                    <div className={`scheme-status ${scheme.status.toLowerCase()}`}>
                      {scheme.status}
                    </div>
                    <h4>{scheme.scheme_name}</h4>
                    <p>{scheme.notes || 'No notes'}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">No schemes assigned</p>
            )}
          </div>
        )}

        {activeTab === 'interventions' && (
          <div className="interventions-section">
            <h3>Action History</h3>
            {student.interventions && student.interventions.length > 0 ? (
              <div className="interventions-list">
                {student.interventions.map(intervention => (
                  <div key={intervention.id} className="intervention-item">
                    <div className={`intervention-status ${intervention.status.toLowerCase()}`}>
                      {intervention.status}
                    </div>
                    <div className="intervention-content">
                      <h4>{intervention.intervention_type}</h4>
                      <p>{intervention.description}</p>
                      <small>By: {intervention.action_taken_by}</small>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">No interventions recorded</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== STUDENTS LIST PAGE ====================
const StudentsList = () => {
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    class: '',
    gender: '',
    riskLevel: ''
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchStudents();
  }, [filters]);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.class) params.class = filters.class;
      if (filters.gender) params.gender = filters.gender;
      if (filters.riskLevel) params.risk_level = filters.riskLevel;

      const response = await axios.get(`${API_BASE_URL}/students`, { params });
      setStudents(response.data.students || []);
      applyFilters(response.data.students || []);
    } catch (error) {
      console.error('Students fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = (studentList) => {
    let filtered = studentList;

    if (searchTerm) {
      filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.enrollment_id.includes(searchTerm)
      );
    }

    setFilteredStudents(filtered);
  };

  useEffect(() => {
    applyFilters(students);
  }, [searchTerm]);

  if (selectedStudent) {
    return (
      <div className="page-container">
        <button className="btn-back" onClick={() => setSelectedStudent(null)}>
          ← Back to List
        </button>
        <StudentProfile studentId={selectedStudent} />
      </div>
    );
  }

  return (
    <div className="students-list-container">
      <h1>👥 Students</h1>

      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by name or enrollment ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-controls">
          <select value={filters.class} onChange={(e) => setFilters({ ...filters, class: e.target.value })}>
            <option value="">All Classes</option>
            <option value="I">Class I</option>
            <option value="II">Class II</option>
            <option value="III">Class III</option>
            <option value="IV">Class IV</option>
            <option value="V">Class V</option>
            <option value="VI">Class VI</option>
            <option value="VII">Class VII</option>
            <option value="VIII">Class VIII</option>
          </select>

          <select value={filters.gender} onChange={(e) => setFilters({ ...filters, gender: e.target.value })}>
            <option value="">All Genders</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>

          <select value={filters.riskLevel} onChange={(e) => setFilters({ ...filters, riskLevel: e.target.value })}>
            <option value="">All Risk Levels</option>
            <option value="Low">Low Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="High">High Risk</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading students...</div>
      ) : filteredStudents.length > 0 ? (
        <div className="students-table-container">
          <table className="students-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Enrollment ID</th>
                <th>Class</th>
                <th>Gender</th>
                <th>Risk Level</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map(student => (
                <tr key={student.id}>
                  <td>{student.name}</td>
                  <td>{student.enrollment_id}</td>
                  <td>{student.class_name}</td>
                  <td>{student.gender}</td>
                  <td>
                    <span className={`risk-badge ${student.latest_risk?.risk_level?.toLowerCase() || 'none'}`}>
                      {student.latest_risk?.risk_level || 'No Data'}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn-view"
                      onClick={() => setSelectedStudent(student.id)}
                    >
                      View Profile
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="no-data">No students found matching your criteria</div>
      )}
    </div>
  );
};

// ==================== SCHEMES PAGE ====================
const SchemesPage = () => {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSchemes();
  }, []);

  const fetchSchemes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/schemes`);
      setSchemes(response.data.schemes || []);
    } catch (error) {
      console.error('Schemes fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const schemeTypeIcons = {
    'scholarship': '📚',
    'transport': '🚌',
    'meal': '🍽️',
    'health': '🏥',
    'girl_child': '👧'
  };

  if (loading) return <div className="loading">Loading schemes...</div>;

  return (
    <div className="schemes-page-container">
      <h1>📋 Government Schemes & Support</h1>
      <p className="page-subtitle">Available assistance programs for rural students</p>

      <div className="schemes-grid-display">
        {schemes.map(scheme => (
          <div key={scheme.id} className="scheme-card-full">
            <div className="scheme-header">
              <span className="scheme-icon">{schemeTypeIcons[scheme.scheme_type] || '💡'}</span>
              <h3>{scheme.name}</h3>
            </div>

            <p className="scheme-description">{scheme.description}</p>

            {scheme.benefits && (
              <div className="scheme-section">
                <h4>Benefits</h4>
                <ul>
                  {scheme.benefits.map((benefit, idx) => (
                    <li key={idx}>{benefit}</li>
                  ))}
                </ul>
              </div>
            )}

            {scheme.eligibility_criteria && (
              <div className="scheme-section">
                <h4>Eligibility Criteria</h4>
                <ul>
                  {scheme.eligibility_criteria.map((criteria, idx) => (
                    <li key={idx}>{criteria}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="scheme-footer">
              {scheme.contact_phone && (
                <p className="contact-info">📞 {scheme.contact_phone}</p>
              )}
              {scheme.apply_link && (
                <a href={scheme.apply_link} className="btn-apply" target="_blank" rel="noopener noreferrer">
                  Apply Now
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ==================== MAIN APP COMPONENT ====================
export default function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const { user, logout } = useAuth();

  if (!user && currentPage !== 'login') {
    setCurrentPage('login');
  }

  return (
    <div className="app">
      {user && (
        <nav className="navbar">
          <div className="navbar-brand">
            <span className="brand-icon">🌱</span>
            <span className="brand-text">EduDew</span>
          </div>

          <div className="nav-menu">
            <button
              className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              📊 Dashboard
            </button>
            <button
              className={`nav-link ${currentPage === 'students' ? 'active' : ''}`}
              onClick={() => setCurrentPage('students')}
            >
              👥 Students
            </button>
            <button
              className={`nav-link ${currentPage === 'schemes' ? 'active' : ''}`}
              onClick={() => setCurrentPage('schemes')}
            >
              📋 Schemes
            </button>
          </div>

          <div className="navbar-right">
            <span className="user-info">{user.name} ({user.role})</span>
            <button className="btn-logout" onClick={() => { logout(); setCurrentPage('login'); }}>
              Logout
            </button>
          </div>
        </nav>
      )}

      <main className="main-content">
        {currentPage === 'login' ? (
          <LoginPage />
        ) : currentPage === 'dashboard' ? (
          <Dashboard />
        ) : currentPage === 'students' ? (
          <StudentsList />
        ) : currentPage === 'schemes' ? (
          <SchemesPage />
        ) : null}
      </main>
    </div>
  );
}

// ==================== ROOT RENDER ====================
export function AppWithProvider() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}
