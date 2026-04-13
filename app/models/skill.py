from datetime import datetime
from app.extensions import db


class SkillCategory(db.Model):
    __tablename__ = 'skill_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # FontAwesome icon class
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    skills = db.relationship('Skill', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<SkillCategory {self.name}>'


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('skill_categories.id'), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('name', 'category_id', name='uq_skill_category'),)

    def __repr__(self):
        return f'<Skill {self.name}>'


class JobRole(db.Model):
    __tablename__ = 'job_roles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    department = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<JobRole {self.title}>'
