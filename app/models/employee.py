from datetime import datetime
from app.extensions import db


class EmployeeProfile(db.Model):
    __tablename__ = 'employee_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    department = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    years_of_experience = db.Column(db.Float, default=0)
    hourly_rate = db.Column(db.Float, default=0)
    current_workload = db.Column(db.Float, default=0)  # percentage 0-100
    max_workload = db.Column(db.Float, default=100)
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    career_goal = db.Column(db.Text)
    total_projects_completed = db.Column(db.Integer, default=0)
    average_project_rating = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = db.relationship('EmployeeSkill', backref='employee_profile', cascade='all, delete-orphan', lazy='dynamic')
    availabilities = db.relationship('Availability', backref='employee_profile', cascade='all, delete-orphan', lazy='dynamic')
    project_history = db.relationship('ProjectHistory', backref='employee_profile', cascade='all, delete-orphan', lazy='dynamic')
    certifications = db.relationship('EmployeeCertification', backref='employee_profile', cascade='all, delete-orphan', lazy='dynamic')
    allocations = db.relationship('Allocation', backref='employee_profile', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<EmployeeProfile {self.user_id}>'


class EmployeeSkill(db.Model):
    __tablename__ = 'employee_skills'

    id = db.Column(db.Integer, primary_key=True)
    employee_profile_id = db.Column(db.Integer, db.ForeignKey('employee_profiles.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    proficiency = db.Column(db.Integer, default=1)  # 1-10
    years_used = db.Column(db.Float, default=0)
    last_used_date = db.Column(db.Date)  # for skill decay
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    skill = db.relationship('Skill', backref='employee_skills')

    __table_args__ = (db.UniqueConstraint('employee_profile_id', 'skill_id', name='uq_employee_skill'),)


class EmployeeCertification(db.Model):
    __tablename__ = 'employee_certifications'

    id = db.Column(db.Integer, primary_key=True)
    employee_profile_id = db.Column(db.Integer, db.ForeignKey('employee_profiles.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    issuing_body = db.Column(db.String(200))
    date_obtained = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    credential_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Availability(db.Model):
    __tablename__ = 'availabilities'

    id = db.Column(db.Integer, primary_key=True)
    employee_profile_id = db.Column(db.Integer, db.ForeignKey('employee_profiles.id'), nullable=False)
    status = db.Column(db.String(30), default='available')  # available, partially_busy, fully_busy, on_leave
    reason = db.Column(db.Text)  # why busy — project name, leave, etc
    current_project_name = db.Column(db.String(200))
    hours_per_week_available = db.Column(db.Float, default=40)
    available_from = db.Column(db.Date)  # date when they become free
    available_until = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectHistory(db.Model):
    __tablename__ = 'project_history'

    id = db.Column(db.Integer, primary_key=True)
    employee_profile_id = db.Column(db.Integer, db.ForeignKey('employee_profiles.id'), nullable=False)
    project_name = db.Column(db.String(200), nullable=False)
    role_in_project = db.Column(db.String(100))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    rating = db.Column(db.Float)  # 1-5 performance rating
    collaborated_with = db.Column(db.Text)  # JSON list of user IDs for synergy tracking
    skills_used = db.Column(db.Text)  # JSON list of skill IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
