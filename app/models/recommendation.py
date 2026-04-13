from datetime import datetime
from app.extensions import db


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    run_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default='generated')  # generated, reviewed, approved, rejected
    parameters_snapshot = db.Column(db.Text)  # JSON of all weights/constraints used
    team_synergy_score = db.Column(db.Float)
    skill_gap_report = db.Column(db.Text)  # JSON
    confidence_score = db.Column(db.Float)  # Monte Carlo confidence
    pareto_alternatives = db.Column(db.Text)  # JSON of alternative teams
    sensitivity_report = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    candidates = db.relationship('RecommendationCandidate', backref='recommendation', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Recommendation {self.id} for Project {self.project_id}>'


class RecommendationCandidate(db.Model):
    __tablename__ = 'recommendation_candidates'

    id = db.Column(db.Integer, primary_key=True)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('recommendations.id'), nullable=False)
    employee_profile_id = db.Column(db.Integer, db.ForeignKey('employee_profiles.id'), nullable=False)
    role_requirement_id = db.Column(db.Integer, db.ForeignKey('role_requirements.id'), nullable=False)
    rank = db.Column(db.Integer)
    overall_score = db.Column(db.Float)
    is_selected = db.Column(db.Boolean, default=False)
    is_manually_overridden = db.Column(db.Boolean, default=False)

    # Score breakdown (JSON for full detail)
    score_breakdown = db.Column(db.Text)  # JSON: {skill_match: 0.9, experience: 0.7, ...}
    hard_constraint_pass = db.Column(db.Boolean, default=True)
    rejection_reasons = db.Column(db.Text)  # JSON list of reasons
    selection_reasons = db.Column(db.Text)  # JSON list of reasons
    decay_adjusted_skills = db.Column(db.Text)  # JSON showing decay impact
    career_alignment_score = db.Column(db.Float)
    workload_fairness_penalty = db.Column(db.Float, default=0)
    topsis_closeness = db.Column(db.Float)  # TOPSIS closeness coefficient

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee_profile = db.relationship('EmployeeProfile', backref='recommendation_entries')
    role_requirement = db.relationship('RoleRequirement', backref='recommendation_candidates')


class Allocation(db.Model):
    __tablename__ = 'allocations'

    id = db.Column(db.Integer, primary_key=True)
    employee_profile_id = db.Column(db.Integer, db.ForeignKey('employee_profiles.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    role_requirement_id = db.Column(db.Integer, db.ForeignKey('role_requirements.id'), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('recommendations.id'))
    status = db.Column(db.String(30), default='allocated')  # allocated, active, completed, released
    allocated_workload = db.Column(db.Float, default=0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', backref='allocations')
    role_requirement = db.relationship('RoleRequirement', backref='allocations')
