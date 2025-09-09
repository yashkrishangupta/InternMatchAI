# AI Internship Matching System

A sophisticated Flask-based web application that uses artificial intelligence to intelligently match students with government internship opportunities. The system employs machine learning algorithms including TF-IDF vectorization and cosine similarity to analyze skill compatibility, location preferences, and academic qualifications while incorporating affirmative action policies for fair representation.

## Features

### For Students
- **Smart Profile Management**: Comprehensive profile system tracking academic information, skills, location preferences, and affirmative action data
- **AI-Powered Matching**: Advanced matching engine that analyzes skills compatibility, location preferences, academic qualifications, and sector interests
- **Application Management**: Submit applications with cover letters, portfolio URLs, and additional notes
- **Match Discovery**: View personalized internship matches ranked by compatibility score
- **Google OAuth Integration**: Seamless registration and login using Google accounts
- **Progress Tracking**: Profile completeness calculator to guide profile optimization

### For Departments/Organizations
- **Internship Management**: Create, edit, and manage internship listings with detailed requirements
- **Application Review**: Review and process student applications with department notes
- **Quota Management**: Set affirmative action quotas for different categories (SC/ST/OBC/Rural)
- **Profile Management**: Comprehensive department profiles with ministry information and contact details

### For Administrators
- **Department Management**: Create and manage department accounts
- **System Oversight**: Monitor platform usage and manage user accounts
- **Analytics Dashboard**: View system-wide statistics and matching performance

## Technology Stack

### Backend
- **Flask 3.1.2**: Modern Python web framework with latest features
- **SQLAlchemy 2.0+**: Advanced ORM with modern async support
- **Flask-SQLAlchemy**: Flask integration for database operations
- **Flask-Migrate**: Database migration management
- **Werkzeug**: WSGI utilities and secure password hashing
- **PostgreSQL**: Production database (with SQLite fallback for development)

### AI/Machine Learning
- **scikit-learn**: Machine learning algorithms for matching engine
- **TF-IDF Vectorization**: Text analysis for skills matching
- **Cosine Similarity**: Mathematical similarity calculations
- **NumPy**: Numerical computing for array operations
- **Pandas**: Data manipulation and analysis

### Frontend
- **Jinja2**: Template engine with Flask integration
- **Bootstrap**: Responsive CSS framework with dark theme
- **Custom CSS**: Application-specific styling
- **Vanilla JavaScript**: Form validation and UI enhancements

### Authentication & Security
- **Google OAuth 2.0**: Secure authentication using Google accounts
- **Session Management**: Flask session handling with secure secret keys
- **Password Hashing**: Werkzeug secure password storage
- **CSRF Protection**: Built-in security features

## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, uses SQLite by default)

### Quick Start
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```
4. Open your browser to `http://localhost:5000`

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (optional)
- `SESSION_SECRET`: Secret key for Flask sessions (defaults to dev key)
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (optional)
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret (optional)

## Database Schema

### Core Models
- **Student**: Complete academic profiles with skills, preferences, and affirmative action data
- **Department**: Government departments and organizations offering internships
- **Admin**: System administrators with user management capabilities
- **Internship**: Detailed internship listings with requirements and quotas
- **Match**: AI-generated compatibility scores between students and internships
- **Application**: Student applications to internships with tracking

### Key Features
- **Profile Completeness**: Automatic calculation of profile completion percentage
- **Matching Scores**: Multi-factor scoring including skills, location, academic, and affirmative action factors
- **Application Tracking**: Complete lifecycle from submission to decision
- **Quota Management**: Support for various affirmative action categories

## AI Matching Algorithm

### Scoring Components
1. **Skills Matching (35%)**: TF-IDF vectorization and cosine similarity for technical and soft skills
2. **Academic Compatibility (25%)**: CGPA requirements, course relevance, and year of study
3. **Location Preferences (20%)**: Preferred locations, current location, and remote work options
4. **Sector Interests (15%)**: Interest alignment with internship sectors
5. **Affirmative Action (5%)**: Bonuses for underrepresented categories and rural areas

### Features
- **Dynamic Thresholds**: Only matches above 30% compatibility are generated
- **Weighted Scoring**: Balanced algorithm considering multiple factors
- **Quota Awareness**: Considers available positions and affirmative action quotas
- **Continuous Learning**: Algorithm can be fine-tuned based on application success rates

## Security Features

- **Secure Authentication**: Password hashing with Werkzeug
- **Session Management**: Secure Flask sessions with CSRF protection
- **OAuth Integration**: Google OAuth 2.0 for enhanced security
- **Input Validation**: Comprehensive form validation and sanitization
- **Access Control**: Role-based access to different system areas

## Production Deployment

The application is configured for production deployment using:
- **Gunicorn**: WSGI server for production
- **ProxyFix**: Middleware for reverse proxy deployment
- **Environment Configuration**: Production-ready settings
- **Database Pooling**: Connection pooling for reliability

### Production Command
```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port app:app
```

## API Endpoints

### Authentication
- `GET /` - Landing page with registration options
- `POST /login` - User authentication
- `GET /logout` - User logout
- `GET /auth/google` - Google OAuth initiation
- `GET /oauth2callback` - Google OAuth callback

### Student Features
- `GET /student/dashboard` - Student dashboard
- `GET /student/profile` - View profile
- `POST /complete_student_profile` - Update profile
- `GET /student/generate-matches` - Generate AI matches
- `GET /student/matches` - View matches
- `POST /student/apply/<id>` - Apply to internship
- `GET /student/applications` - View applications

### Department Features
- `GET /department/dashboard` - Department dashboard
- `GET /department/profile` - View profile
- `POST /internship/create` - Create internship
- `POST /internship/edit/<id>` - Edit internship
- `POST /internship/delete/<id>` - Delete internship

## Development

### Local Development
1. Ensure Python 3.11+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`
4. Access at: `http://localhost:5000`

### Database Migrations
```bash
flask db init
flask db migrate -m "Migration message"
flask db upgrade
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is developed for government internship programs and follows applicable government software licensing guidelines.

## Support

For technical support or feature requests, please contact the development team or create an issue in the repository.
