from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import Student, Company, Internship, Match, Application
from matching_engine import InternshipMatchingEngine
import logging

matching_engine = InternshipMatchingEngine()

@app.route('/')
def index():
    """Home page with registration options"""
    return render_template('index.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    """Student registration"""
    if request.method == 'POST':
        try:
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            phone = request.form.get('phone')
            institution = request.form.get('institution')
            course = request.form.get('course')
            year_of_study = request.form.get('year_of_study', type=int)
            cgpa = request.form.get('cgpa', type=float)
            
            # Skills and interests
            technical_skills = request.form.get('technical_skills')
            soft_skills = request.form.get('soft_skills')
            sector_interests = request.form.get('sector_interests')
            
            # Location
            preferred_locations = request.form.get('preferred_locations')
            current_location = request.form.get('current_location')
            
            # Affirmative action data
            social_category = request.form.get('social_category')
            district_type = request.form.get('district_type')
            home_district = request.form.get('home_district')
            
            # Previous participation
            previous_internships = request.form.get('previous_internships', type=int, default=0)
            pm_scheme_participant = request.form.get('pm_scheme_participant') == 'on'
            
            # Validate required fields
            if not all([email, password, name, institution, course]):
                flash('Please fill all required fields', 'error')
                return render_template('student_register.html')
            
            # Check if email exists
            if Student.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('student_register.html')
            
            # Create new student
            student = Student(
                email=email,
                name=name,
                phone=phone,
                institution=institution,
                course=course,
                year_of_study=year_of_study,
                cgpa=cgpa,
                technical_skills=technical_skills,
                soft_skills=soft_skills,
                sector_interests=sector_interests,
                preferred_locations=preferred_locations,
                current_location=current_location,
                social_category=social_category,
                district_type=district_type,
                home_district=home_district,
                previous_internships=previous_internships,
                pm_scheme_participant=pm_scheme_participant
            )
            student.set_password(password)
            
            db.session.add(student)
            db.session.commit()
            
            session['user_type'] = 'student'
            session['user_id'] = student.id
            
            flash('Registration successful!', 'success')
            return redirect(url_for('student_dashboard'))
            
        except Exception as e:
            logging.error(f"Error in student registration: {e}")
            flash('Registration failed. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('student_register.html')

@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    """Company registration"""
    if request.method == 'POST':
        try:
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            industry_sector = request.form.get('industry_sector')
            company_size = request.form.get('company_size')
            location = request.form.get('location')
            description = request.form.get('description')
            contact_person = request.form.get('contact_person')
            contact_phone = request.form.get('contact_phone')
            
            # Validate required fields
            if not all([email, password, name, industry_sector]):
                flash('Please fill all required fields', 'error')
                return render_template('company_register.html')
            
            # Check if email exists
            if Company.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('company_register.html')
            
            # Create new company
            company = Company(
                email=email,
                name=name,
                industry_sector=industry_sector,
                company_size=company_size,
                location=location,
                description=description,
                contact_person=contact_person,
                contact_phone=contact_phone
            )
            company.set_password(password)
            
            db.session.add(company)
            db.session.commit()
            
            session['user_type'] = 'company'
            session['user_id'] = company.id
            
            flash('Registration successful!', 'success')
            return redirect(url_for('company_dashboard'))
            
        except Exception as e:
            logging.error(f"Error in company registration: {e}")
            flash('Registration failed. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('company_register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login for both students and companies"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        if user_type == 'student':
            user = Student.query.filter_by(email=email).first()
        elif user_type == 'company':
            user = Company.query.filter_by(email=email).first()
        else:
            flash('Invalid user type', 'error')
            return redirect(url_for('index'))
        
        if user and user.check_password(password):
            session['user_type'] = user_type
            session['user_id'] = user.id
            
            if user_type == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('company_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard"""
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    student = Student.query.get(session['user_id'])
    if not student:
        return redirect(url_for('index'))
    
    # Get recent matches
    matches = Match.query.filter_by(student_id=student.id)\
                        .order_by(Match.overall_score.desc())\
                        .limit(10).all()
    
    return render_template('student_dashboard.html', student=student, matches=matches)

@app.route('/company/dashboard')
def company_dashboard():
    """Company dashboard"""
    if session.get('user_type') != 'company':
        return redirect(url_for('index'))
    
    company = Company.query.get(session['user_id'])
    if not company:
        return redirect(url_for('index'))
    
    # Get company's internships
    internships = Internship.query.filter_by(company_id=company.id).all()
    
    return render_template('company_dashboard.html', company=company, internships=internships)

@app.route('/internship/create', methods=['GET', 'POST'])
def create_internship():
    """Create new internship"""
    if session.get('user_type') != 'company':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            description = request.form.get('description')
            sector = request.form.get('sector')
            location = request.form.get('location')
            required_skills = request.form.get('required_skills')
            preferred_course = request.form.get('preferred_course')
            min_cgpa = request.form.get('min_cgpa', type=float)
            year_of_study_requirement = request.form.get('year_of_study_requirement')
            total_positions = request.form.get('total_positions', type=int)
            duration_months = request.form.get('duration_months', type=int)
            stipend = request.form.get('stipend', type=float)
            
            # Affirmative action quotas
            rural_quota = request.form.get('rural_quota', type=int, default=0)
            sc_quota = request.form.get('sc_quota', type=int, default=0)
            st_quota = request.form.get('st_quota', type=int, default=0)
            obc_quota = request.form.get('obc_quota', type=int, default=0)
            
            # Validate required fields
            if not all([title, description, sector, total_positions]):
                flash('Please fill all required fields', 'error')
                return render_template('create_internship.html')
            
            # Create new internship
            internship = Internship(
                company_id=session['user_id'],
                title=title,
                description=description,
                sector=sector,
                location=location,
                required_skills=required_skills,
                preferred_course=preferred_course,
                min_cgpa=min_cgpa,
                year_of_study_requirement=year_of_study_requirement,
                total_positions=total_positions,
                duration_months=duration_months,
                stipend=stipend,
                rural_quota=rural_quota,
                sc_quota=sc_quota,
                st_quota=st_quota,
                obc_quota=obc_quota
            )
            
            db.session.add(internship)
            db.session.commit()
            
            flash('Internship created successfully!', 'success')
            return redirect(url_for('company_dashboard'))
            
        except Exception as e:
            logging.error(f"Error creating internship: {e}")
            flash('Failed to create internship. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('create_internship.html')

@app.route('/student/generate-matches')
def generate_matches():
    """Generate matches for current student"""
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    try:
        student_id = session['user_id']
        matches = matching_engine.generate_matches_for_student(student_id)
        
        flash(f'Generated {len(matches)} new matches!', 'success')
        return redirect(url_for('view_matches'))
        
    except Exception as e:
        logging.error(f"Error generating matches: {e}")
        flash('Failed to generate matches. Please try again.', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/student/matches')
def view_matches():
    """View all matches for current student"""
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    student_id = session['user_id']
    matches = Match.query.filter_by(student_id=student_id)\
                        .order_by(Match.overall_score.desc()).all()
    
    return render_template('matches.html', matches=matches)

@app.route('/admin/generate-all-matches')
def generate_all_matches():
    """Admin function to generate matches for all students"""
    try:
        total_matches = matching_engine.generate_all_matches()
        flash(f'Generated {total_matches} total matches!', 'success')
        
    except Exception as e:
        logging.error(f"Error generating all matches: {e}")
        flash('Failed to generate matches. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/student/apply/<int:internship_id>', methods=['POST'])
def apply_internship(internship_id):
    """Apply to an internship"""
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    try:
        student_id = session['user_id']
        
        # Check if already applied
        existing_application = Application.query.filter_by(
            student_id=student_id, 
            internship_id=internship_id
        ).first()
        
        if existing_application:
            flash('You have already applied to this internship', 'warning')
            return redirect(url_for('view_matches'))
        
        # Get form data
        cover_letter = request.form.get('cover_letter', '')
        portfolio_url = request.form.get('portfolio_url', '')
        additional_notes = request.form.get('additional_notes', '')
        
        # Create application
        application = Application(
            student_id=student_id,
            internship_id=internship_id,
            cover_letter=cover_letter,
            portfolio_url=portfolio_url,
            additional_notes=additional_notes
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('view_applications'))
        
    except Exception as e:
        logging.error(f"Error applying to internship: {e}")
        flash('Failed to submit application. Please try again.', 'error')
        db.session.rollback()
        return redirect(url_for('view_matches'))

@app.route('/student/applications')
def view_applications():
    """View all applications for current student"""
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    student_id = session['user_id']
    applications = Application.query.filter_by(student_id=student_id)\
                                  .order_by(Application.applied_at.desc()).all()
    
    return render_template('applications.html', applications=applications)

@app.route('/internship/<int:internship_id>')
def view_internship(internship_id):
    """View internship details"""
    internship = Internship.query.get_or_404(internship_id)
    return render_template('internship_details.html', internship=internship)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
