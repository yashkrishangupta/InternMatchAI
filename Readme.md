# AI Internship Matching System

## Overview

This is a Flask-based web application that uses AI-powered algorithms to match students with internship opportunities. The system implements intelligent matching using TF-IDF vectorization and cosine similarity to analyze skills compatibility, location preferences, and other criteria. It features separate registration and dashboard systems for students and companies, with comprehensive profile management and automated match generation. The platform also incorporates affirmative action policies to ensure fair representation across different social categories and geographic regions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development with PostgreSQL support via environment configuration
- **Models**: Three main entities - Student, Company, and Internship with a Match relationship table
- **Authentication**: Session-based authentication using Werkzeug password hashing
- **Deployment**: WSGI-ready with ProxyFix middleware for production deployment

### AI Matching Engine
- **Algorithm**: Custom matching engine using scikit-learn
- **Text Processing**: TF-IDF vectorization for skills analysis
- **Similarity Calculation**: Cosine similarity for skills matching
- **Scoring System**: Multi-factor scoring including skills compatibility, location preferences, and academic qualifications
- **Preprocessing**: Standardized text processing and skill normalization

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask
- **CSS Framework**: Bootstrap with dark theme customization
- **JavaScript**: Vanilla JavaScript for form validation and UI enhancements
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Data Model Design
- **Student Profiles**: Comprehensive academic information, skills tracking, location preferences, and affirmative action data
- **Company Profiles**: Industry sectors, company size, location, and contact information
- **Internship Listings**: Detailed role descriptions, requirements, location, duration, and stipend information
- **Match Records**: Stores computed compatibility scores and matching criteria

### Authentication & Authorization
- **User Types**: Separate authentication flows for students and companies
- **Session Management**: Flask session handling with secure secret keys
- **Password Security**: Werkzeug password hashing for secure credential storage
- **Access Control**: Role-based access to different dashboard functionalities

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: Database ORM and connection management
- **Werkzeug**: WSGI utilities and password hashing

### AI & Data Processing Libraries
- **scikit-learn**: Machine learning algorithms for TF-IDF and cosine similarity
- **NumPy**: Numerical computing for array operations
- **Pandas**: Data manipulation and analysis

### Frontend Libraries
- **Bootstrap**: CSS framework for responsive design and components
- **Font Awesome**: Icon library for UI elements
- **Custom CSS**: Application-specific styling and dark theme customization

### Database Configuration
- **SQLite**: Default development database
- **PostgreSQL**: Production database support via DATABASE_URL environment variable
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability
