import os
from datetime import datetime
# Flask: Core framework for handling HTTP requests and responses
# render_template: Renders HTML files from the /templates directory and injects dynamic data
# request: Global object containing incoming HTTP request data (form inputs, URLs, methods)
# redirect & url_for: Used to redirect users to different routes by using the function name
# flash: Stores a temporary message in the session to display on the next page load (feedback)
# session: A secure, browser-bound dictionary encrypted with the SECRET_KEY to persist user state
from flask import Flask, render_template, request, redirect, url_for, flash, session

# SQLAlchemy: Object Relational Mapper (ORM) to interact with SQLite using Python classes instead of raw SQL
from flask_sqlalchemy import SQLAlchemy

# Security utilities to avoid storing plain-text passwords in memory or code
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------
# 1. APPLICATION SETUP & CONFIGURATION
# ---------------------------------------------------------

# Instantiate the Flask application
app = Flask(__name__)

# The secret key signs session cookies cryptographically. 
# It prevents malicious users from tempering with session data (like altering 'is_admin').
app.config['SECRET_KEY'] = 'super-secret-key-change-this-in-production'

# Define where the SQLite database file will be stored. 
# 'sqlite:///database.db' creates a file named 'database.db' in the project relative path.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Disable tracking overhead to save system memory and optimize database operations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Bind the SQLAlchemy instance to our Flask application
db = SQLAlchemy(app)

# ---------------------------------------------------------
# 2. DATABASE MODEL (ORM)
# ---------------------------------------------------------

# This class defines the structure of our database table.
# SQLAlchemy converts this Python class into a SQL table automatically.
class DILEntry(db.Model):
    # Primary key uniquely identifies each micro-blog post (1, 2, 3...)
    id = db.Column(db.Integer, primary_key=True)
    
    # Title of the entry, limited to 100 characters, cannot be empty
    title = db.Column(db.String(100), nullable=False)
    
    # Detailed text content of what was learned, cannot be empty
    content = db.Column(db.Text, nullable=False)
    
    # Timestamp. Notice we pass 'datetime.utcnow' (the function itself) without parentheses ().
    # This ensures SQLAlchemy executes the function to get the current time *when the post is created*, 
    # instead of when the app first boots up.
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # String representation of the object, highly useful for debugging in the terminal
    def __repr__(self):
        return f"TIL('{self.title}', '{self.date_posted}')"

# ---------------------------------------------------------
# 3. ADMINISTRATIVE CREDENTIALS
# ---------------------------------------------------------

# Hardcoded credentials for an MVP setup.
ADMIN_USERNAME = "admin"

# We pre-hash the password "password123". The code never stores or reads the raw string directly,
# ensuring that even if an attacker prints the variable, they only see a cryptographic hash.
ADMIN_PASSWORD_HASH = generate_password_hash("password123")

# ---------------------------------------------------------
# 4. REQUEST ROUTING & CONTROLLERS
# ---------------------------------------------------------

@app.route('/')
def index():
    """
    HOMEPAGE ROUTE
    Fetches all entries from the SQLite database.
    .order_by(DILEntry.date_posted.desc()) ensures the newest insights appear at the top.
    """
    entries = DILEntry.query.order_by(DILEntry.date_posted.desc()).all()
    # Pass the entries list into the HTML template to be rendered via Jinja2 loops
    return render_template('index.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    ADMIN LOGIN ROUTE
    Handles both rendering the form (GET) and processing credentials (POST).
    """
    if request.method == 'POST':
        # Safely extract data sent from the HTML input fields via name attributes
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if username matches AND verify the incoming plain text password against our secure hash
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            # Session assignment: This sets an encrypted cookie on the client's browser.
            # As long as 'is_admin' is True, Flask recognizes this client session as the Admin.
            session['is_admin'] = True
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('index'))
        else:
            # If authentication fails, send an error category flash message
            flash('Invalid credentials. Please try again.', 'danger')
            
    # If the request method is GET, simply render the login page interface
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    ADMIN LOGOUT ROUTE
    Clears the admin status from the active session.
    """
    # .pop() removes 'is_admin' from the session dictionary if it exists.
    session.pop('is_admin', None)
    flash('You have logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_entry():
    """
    SECURE DATA INSERTION ROUTE
    Processes the creation of new 'Today I Learned' entries. 
    Restricted entirely to the admin session.
    """
    # SECURITY GATEKEEPER: Ensure the requester actually holds an active admin session.
    # If an outsider tries to manually send a POST request here via tools like Postman, they are blocked!
    if not session.get('is_admin'):
        flash('Unauthorized! Only the admin can add entries.', 'danger')
        return redirect(url_for('index'))
        
    # Capture the form text data
    title = request.form.get('title')
    content = request.form.get('content')
    
    # Server-side validation to ensure fields aren't blank spaces or empty
    if title and title.strip() and content and content.strip():
        # Instantiate a new row object using our SQLAlchemy Model
        new_entry = DILEntry(title=title.strip(), content=content.strip())
        
        # Stage the object creation inside the transaction session
        db.session.add(new_entry)
        # Commit saves the staged changes permanently into the physical database file
        db.session.commit()
        
        flash('New TIL entry added successfully!', 'success')
    else:
        flash('Title and Content fields cannot be empty.', 'danger')
        
    # Redirect back to the index view to display the freshly added post
    return redirect(url_for('index'))

# ---------------------------------------------------------
# 5. INITIALIZATION & APPLICATION RUNNER
# ---------------------------------------------------------

if __name__ == '__main__':
    # Flask requires an application context to interact with extensions like SQLAlchemy.
    # Using 'with app.app_context():' temporarily links the database engine to the application instance.
    with app.app_context():
        # db.create_all() inspects all classes inheriting from db.Model.
        # If 'database.db' doesn't exist, it auto-generates the database file and creates the tables.
        # If it already exists, this command safely skips creation without modifying data.
        db.create_all()  
        
    # Start the local development web server.
    # debug=True allows hot-reloading (auto-restarts code upon changes) and shows detailed interactive error traces.
    app.run(debug=True)