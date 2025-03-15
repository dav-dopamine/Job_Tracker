from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from flask_login import UserMixin
from enum import Enum

class JobStatusEnum(Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"

# defining the user model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Unique user ID
    username = db.Column(db.String(100), unique=True, nullable=False)  # Username must be unique
    email = db.Column(db.String(100), unique=True, nullable=False)  # Email must be unique
    password_hash = db.Column(db.String(128), nullable=False)  # Column for storing the hashed password

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# define a database model/table for storing the job applications
class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Job Application ID (unique)
    company_name = db.Column(db.String(100), nullable=False)  # Company name (required)
    position = db.Column(db.String(100), nullable=False)  # Job position (required)
    status = db.Column(db.String(50), nullable=False, default="Applied")  # Job application status (default = "Applied")
    date_applied = db.Column(db.DateTime, nullable=False)  # Date the job was applied to (required)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link job application to a user
    user = db.relationship('User', backref='applications', lazy=True)  # Relationship with User

    def __repr__(self):
        return f"application {self.company_name} - {self.position}"