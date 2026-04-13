from datetime import datetime
from app.extensions import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(30), default='draft')  # draft, open, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    budget = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    manager = db.relationship('User', backref='managed_projects')
    role_requirements = db.relationship('RoleRequirement', backref='project', cascade='all, delete-orphan', lazy='dynamic')
    recommendations = db.relationship('Recommendation', backref='project', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.name}>'


class RoleRequirement(db.Model):
    __tablename__ = 'role_requirements'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    role_title = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    constraints = db.relationship('RoleConstraint', backref='role_requirement', cascade='all, delete-orphan', lazy='dynamic')
    scoring_weights = db.relationship('ScoringWeight', backref='role_requirement', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<RoleRequirement {self.role_title} x{self.quantity}>'


class RoleConstraint(db.Model):
    """Manager-defined hard constraints per role — NOT hardcoded in Python."""
    __tablename__ = 'role_constraints'

    id = db.Column(db.Integer, primary_key=True)
    role_requirement_id = db.Column(db.Integer, db.ForeignKey('role_requirements.id'), nullable=False)
    constraint_type = db.Column(db.String(50), nullable=False)
    # Types: mandatory_skill, min_proficiency, min_experience, max_workload,
    #        availability_overlap, required_certification, budget_cap
    parameter_name = db.Column(db.String(100))   # e.g. skill name, cert name
    parameter_value = db.Column(db.String(200))   # e.g. "7" for min proficiency
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ScoringWeight(db.Model):
    """Manager-defined soft criteria weights per role."""
    __tablename__ = 'scoring_weights'

    id = db.Column(db.Integer, primary_key=True)
    role_requirement_id = db.Column(db.Integer, db.ForeignKey('role_requirements.id'), nullable=False)
    criterion = db.Column(db.String(50), nullable=False)
    # Criteria: skill_match, experience, availability, cost_efficiency,
    #           project_success, versatility, career_alignment, certification_relevance
    weight = db.Column(db.Float, default=0.1)  # 0.0 to 1.0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
