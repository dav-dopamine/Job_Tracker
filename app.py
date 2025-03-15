import secrets
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Import models and the database instance from models.py (which should also export db)
from models import db, User, JobApplication

# Import the JobApplicationForm we just created
from forms import JobApplicationForm

app = Flask(__name__)  # Initialize the Flask app

# Set a Secret Key for Flask Sessions (used for CSRF and session security)
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generates a random secret key

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Set up Flask-Login for user session management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if user is not authenticated

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define signup form (using Flask-WTF)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Home route: if user is logged in, show dashboard with options; if not, show login/signup options.
@app.route('/')
def home():
    return render_template('home.html')

# Signup route: Create a new user account.
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# Login route: Allow existing users to log in.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            # Redirect to the home (dashboard) page after successful login
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

# Logout route: End the user session.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route to add a new job application.
@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    form = JobApplicationForm()
    if form.validate_on_submit():
        new_application = JobApplication(
            company_name=form.company_name.data,
            position=form.position.data,
            status=form.status.data,
            date_applied=form.date_applied.data,
            user_id=current_user.id  # Associate this job application with the current user
        )
        db.session.add(new_application)
        db.session.commit()
        flash('Job application added!', 'success')
        return redirect(url_for('job_applications'))
    return render_template('job_application_form.html', form=form)

@app.route('/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):  # Change parameter name
    job = JobApplication.query.get_or_404(job_id)  # Fetch job from DB
    form = JobApplicationForm(obj=job)

    if form.validate_on_submit():
        job.company_name = form.company_name.data
        job.position = form.position.data
        job.status = form.status.data
        job.date_applied = form.date_applied.data
        db.session.commit()
        flash('Job application edited!', 'success')
        return redirect(url_for('job_applications'))

    return render_template('edit_job.html', form=form, job=job)

@app.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = JobApplication.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job application deleted!', 'success')
    return redirect(url_for('job_applications'))

# Route to view all job applications for the logged-in user.
@app.route('/job_applications')
@login_required
def job_applications():
    applications = JobApplication.query.filter_by(user_id=current_user.id).all()
    return render_template('applications_list.html', applications=applications)

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates all tables based on the models (User, JobApplication, etc.)
    app.run(host='0.0.0.0', port=5000, debug=True)
