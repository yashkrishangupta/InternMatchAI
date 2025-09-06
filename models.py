from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)  # Optional for Google auth
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Google OAuth ID
    profile_picture = db.Column(db.String(255), nullable=True)  # Google profile picture
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    
    # Academic Information
    institution = db.Column(db.String(200))
    course = db.Column(db.String(100))
    year_of_study = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    
    # Skills and Interests (stored as comma-separated strings)
    technical_skills = db.Column(db.Text)
    soft_skills = db.Column(db.Text)
    sector_interests = db.Column(db.Text)
    
    # Location Preferences
    preferred_locations = db.Column(db.Text)
    current_location = db.Column(db.String(100))
    
    # Affirmative Action Data
    social_category = db.Column(db.String(50))  # General, OBC, SC, ST
    district_type = db.Column(db.String(50))    # Urban, Rural, Aspirational
    home_district = db.Column(db.String(100))
    
    # Previous Participation
    previous_internships = db.Column(db.Integer, default=0)
    pm_scheme_participant = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    matches = db.relationship('Match', backref='student', lazy=True)
    applications = db.relationship('Application', backref='student', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)  # Optional for Google auth
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Google OAuth ID
    profile_picture = db.Column(db.String(255), nullable=True)  # Google profile picture
    name = db.Column(db.String(200), nullable=False)
    
    # Company Information
    industry_sector = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # Contact Information
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(15))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    internships = db.relationship('Internship', backref='company', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Internship(db.Model):
    __tablename__ = 'internships'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Basic Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    sector = db.Column(db.String(100))
    location = db.Column(db.String(100))
    
    # Requirements
    required_skills = db.Column(db.Text)
    preferred_course = db.Column(db.String(100))
    min_cgpa = db.Column(db.Float)
    year_of_study_requirement = db.Column(db.String(50))
    
    # Capacity and Duration
    total_positions = db.Column(db.Integer, default=1)
    filled_positions = db.Column(db.Integer, default=0)
    duration_months = db.Column(db.Integer)
    stipend = db.Column(db.Float)
    
    # Affirmative Action Quotas
    rural_quota = db.Column(db.Integer, default=0)
    sc_quota = db.Column(db.Integer, default=0)
    st_quota = db.Column(db.Integer, default=0)
    obc_quota = db.Column(db.Integer, default=0)
    
    # Application Status
    is_active = db.Column(db.Boolean, default=True)
    application_deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    matches = db.relationship('Match', backref='internship', lazy=True)
    applications = db.relationship('Application', backref='internship', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    
    # Matching Scores
    overall_score = db.Column(db.Float, nullable=False)
    skills_score = db.Column(db.Float)
    location_score = db.Column(db.Float)
    academic_score = db.Column(db.Float)
    affirmative_action_score = db.Column(db.Float)
    
    # Match Status
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique student-internship pairs
    __table_args__ = (db.UniqueConstraint('student_id', 'internship_id'),)

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    
    # Application Information
    cover_letter = db.Column(db.Text)
    portfolio_url = db.Column(db.String(255))
    additional_notes = db.Column(db.Text)
    
    # Application Status
    status = db.Column(db.String(50), default='pending')  # pending, under_review, shortlisted, accepted, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Company Response
    company_notes = db.Column(db.Text)
    interview_date = db.Column(db.DateTime)
    response_date = db.Column(db.DateTime)
    
    # Ensure unique student-internship applications
    __table_args__ = (db.UniqueConstraint('student_id', 'internship_id'),)
