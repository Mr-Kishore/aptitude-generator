# Aptitude Generator

A web application for generating and practicing aptitude test questions.

## Features

- User authentication (login/register)
- Practice aptitude questions
- Track progress and performance
- Responsive design

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aptitude-generator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` as needed

## Running the Application

### Development Mode

```bash
# Set FLASK_APP and FLASK_ENV
set FLASK_APP=wsgi.py
set FLASK_ENV=development

# Run the development server
flask run
```

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
gunicorn wsgi:app
```

## Project Structure

```
aptitude-generator/
├── app/
│   ├── __init__.py       # Application factory
│   ├── auth.py          # Authentication routes
│   ├── main.py          # Main routes
│   ├── db.py            # Database configuration
│   ├── models/          # Database models
│   ├── static/          # Static files (CSS, JS, images)
│   └── templates/       # HTML templates
│       ├── auth/        # Authentication templates
│       ├── errors/      # Error pages
│       └── *.html       # Base templates
├── instance/            # Instance folder for configuration and database
├── tests/               # Test files
├── .env                 # Environment variables
├── .gitignore           # Git ignore file
├── requirements.txt     # Project dependencies
└── wsgi.py             # WSGI entry point
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
