from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import Student, Company, Internship, Match, Application
from matching_engine import InternshipMatchingEngine
from oauth import create_google_flow, handle_google_login, get_google_user_info
import logging

matching_engine = InternshipMatchingEngine()

@app.route('/')
def index():
    """Home page with registration options"""
    return render_template('index.html')

@app.route('/profile')
def profile():
    if session.get('user_type') != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    student = Student.query.get(session.get('user_id'))
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('index'))

    completeness_score, missing_fields = student.calculate_profile_completeness()

    # if completeness_score < 100:
    #     flash('Please complete your profile to access all features.', 'info')
    #     # Redirect to the same "complete profile" form, prefilled
    #     return redirect(url_for('complete_student_profile'))

    # Profile complete → show profile view
    return render_template(
        'student_profile_view.html',
        student=student,
        completeness_score=completeness_score,
        missing_fields=missing_fields
    )



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
                return render_template('complete_student_profile.html')
            
            # Check if email exists
            if Student.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('complete_student_profile.html')
            
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
            
            flash('Profile completion successful!', 'success')
            return redirect(url_for('student_dashboard'))
            
        except Exception as e:
            logging.error(f"Error in student registration: {e}")
            flash('Registration failed. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('complete_student_profile.html')

@app.route('/complete_student_profile', methods=['GET', 'POST'])
def complete_student_profile():
    """Complete or edit student profile - works for both Google OAuth and regular users"""
    if session.get('user_type') != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    student = Student.query.get(session.get('user_id'))
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Update student profile with form data
            student.name = request.form.get('name') or student.name
            student.phone = request.form.get('phone') or student.phone
            student.institution = request.form.get('institution') or student.institution
            student.course = request.form.get('course') or student.course
            
            # Handle numeric fields properly
            year_str = request.form.get('year_of_study')
            if year_str and year_str.isdigit():
                student.year_of_study = int(year_str)
                
            cgpa_str = request.form.get('cgpa')
            if cgpa_str:
                try:
                    student.cgpa = float(cgpa_str)
                except ValueError:
                    pass
                    
            prev_internships_str = request.form.get('previous_internships')
            if prev_internships_str and prev_internships_str.isdigit():
                student.previous_internships = int(prev_internships_str)
            
            # Update text fields
            student.technical_skills = request.form.get('technical_skills') or student.technical_skills
            student.soft_skills = request.form.get('soft_skills') or student.soft_skills
            student.sector_interests = request.form.get('sector_interests') or student.sector_interests
            student.current_location = request.form.get('current_location') or student.current_location
            student.preferred_locations = request.form.get('preferred_locations') or student.preferred_locations
            student.social_category = request.form.get('social_category') or student.social_category
            student.district_type = request.form.get('district_type') or student.district_type
            student.home_district = request.form.get('home_district') or student.home_district
            
            # Handle checkbox
            student.pm_scheme_participant = bool(request.form.get('pm_scheme_participant'))

            db.session.commit()
            flash("Profile updated successfully!", "success")
            
            # If user came from Google OAuth and essential fields are now filled, go to dashboard
            if session.get('google_auth') and student.institution and student.course:
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('profile'))

        except Exception as e:
            logging.error(f"Error updating student profile: {e}")
            flash("Failed to update profile. Please try again.", "error")
            db.session.rollback()

    return render_template('complete_student_profile.html', student=student, is_editing=True)


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

# Google OAuth routes
@app.route('/auth/google')
def google_auth():
    """Initiate Google OAuth"""
    user_type = request.args.get('type', 'student')
    if user_type not in ['student', 'company']:
        flash('Invalid user type', 'error')
        return redirect(url_for('index'))
    
    # Store user type in session for callback
    session['oauth_user_type'] = user_type
    
    flow = create_google_flow()
    if not flow:
        flash('Google authentication is not configured. Please contact administrator.', 'error')
        return redirect(url_for('index'))
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'
    )
    
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth_callback():
    """Handle Google OAuth callback"""
    # Verify state parameter
    if 'oauth_state' not in session or request.args.get('state') != session['oauth_state']:
        flash('Invalid authentication state', 'error')
        return redirect(url_for('index'))
    
    user_type = session.get('oauth_user_type', 'student')
    
    flow = create_google_flow()
    if not flow:
        flash('Authentication configuration error', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get the authorization code and exchange for tokens
        flow.fetch_token(authorization_response=request.url)
        
        # Get user info from Google
        credentials = flow.credentials
        user_info = get_google_user_info(credentials.token)
        
        if not user_info:
            flash('Failed to get user information from Google', 'error')
            return redirect(url_for('index'))
        
        # Handle login/registration
        success, user = handle_google_login(user_info, user_type)
        
        if success:
            session['user_type'] = user_type
            session['user_id'] = user.id
            session['google_auth'] = True  # mark as logged in via Google
        
            # Check if this is a new user or profile is incomplete
            if user_type == "student":
                # Check if essential profile fields are missing
                if not user.institution or not user.course:
                    flash('Welcome! Please complete your profile to get started.', 'info')
                    return redirect(url_for('complete_student_profile'))
            elif user_type == "company":
                # Check if essential profile fields are missing  
                if not user.industry_sector:
                    flash('Welcome! Please complete your company profile to start posting internships.', 'info')
                    return redirect(url_for('complete_company_profile'))
        
            # Profile is complete → go to dashboard
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for(f"{user_type}_dashboard"))

        else:
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('index'))

            
    except Exception as e:
        logging.error(f"OAuth callback error: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('index'))
    
    finally:
        # Clean up session
        session.pop('oauth_state', None)
        session.pop('oauth_user_type', None)

# @app.route('/complete-student-profile', methods=['GET', 'POST'])
# def complete_student_profile():
#     """Complete student profile after Google OAuth"""
#     if session.get('user_type') != 'student' or not session.get('google_auth'):
#         return redirect(url_for('index'))
    
#     student = Student.query.get(session['user_id'])
#     if not student:
#         return redirect(url_for('index'))
    
#     if request.method == 'POST':
#         try:
#             # Update student profile with additional information
#             student.phone = request.form.get('phone')
#             student.institution = request.form.get('institution')
#             student.course = request.form.get('course')
#             student.year_of_study = request.form.get('year_of_study', type=int)
#             student.cgpa = request.form.get('cgpa', type=float)
#             student.technical_skills = request.form.get('technical_skills')
#             student.soft_skills = request.form.get('soft_skills')
#             student.sector_interests = request.form.get('sector_interests')
#             student.preferred_locations = request.form.get('preferred_locations')
#             student.current_location = request.form.get('current_location')
#             student.social_category = request.form.get('social_category')
#             student.district_type = request.form.get('district_type')
#             student.home_district = request.form.get('home_district')
#             student.previous_internships = request.form.get('previous_internships', type=int, default=0)
#             student.pm_scheme_participant = request.form.get('pm_scheme_participant') == 'on'
            
#             db.session.commit()
#             flash('Profile completed successfully!', 'success')
#             return redirect(url_for('student_dashboard'))
            
#         except Exception as e:
#             logging.error(f"Error completing student profile: {e}")
#             flash('Failed to complete profile. Please try again.', 'error')
#             db.session.rollback()
    
#     return render_template('complete_student_profile.html', student=student)

@app.route('/complete-company-profile', methods=['GET', 'POST'])
def complete_company_profile():
    """Complete company profile after Google OAuth"""
    if session.get('user_type') != 'company' or not session.get('google_auth'):
        return redirect(url_for('index'))
    
    company = Company.query.get(session['user_id'])
    if not company:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Update company profile with additional information
            company.industry_sector = request.form.get('industry_sector')
            company.company_size = request.form.get('company_size')
            company.location = request.form.get('location')
            company.description = request.form.get('description')
            company.contact_person = request.form.get('contact_person')
            company.contact_phone = request.form.get('contact_phone')
            
            db.session.commit()
            flash('Profile completed successfully!', 'success')
            return redirect(url_for('company_dashboard'))
            
        except Exception as e:
            logging.error(f"Error completing company profile: {e}")
            flash('Failed to complete profile. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('complete_company_profile.html', company=company)
