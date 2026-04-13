from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import (
    User, EmployeeProfile, EmployeeSkill, Project, Skill, SkillCategory,
    JobRole, AuditLog, Recommendation, RecommendationCandidate, Allocation,
    Availability, RoleRequirement
)
from app.utils.helpers import role_required
from sqlalchemy import func, case
import json

superuser_bp = Blueprint('superuser', __name__, url_prefix='/superuser')


@superuser_bp.route('/dashboard')
@login_required
@role_required('superuser')
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_employees': User.query.filter_by(role='employee', is_approved=True).count(),
        'total_managers': User.query.filter_by(role='manager').count(),
        'pending_approvals': User.query.filter_by(is_approved=False).count(),
        'total_projects': Project.query.count(),
        'active_projects': Project.query.filter_by(status='in_progress').count(),
        'total_skills': Skill.query.count(),
        'total_job_roles': JobRole.query.count(),
        'total_recommendations': Recommendation.query.count(),
        'total_allocations': Allocation.query.count(),
    }
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(20).all()
    recent_recs = Recommendation.query.order_by(Recommendation.created_at.desc()).limit(5).all()
    return render_template('superuser/dashboard.html', stats=stats,
                          recent_logs=recent_logs, recent_recs=recent_recs)


@superuser_bp.route('/users')
@login_required
@role_required('superuser')
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('superuser/users.html', users=all_users)


@superuser_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@role_required('superuser')
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate yourself.', 'danger')
    else:
        user.is_active_user = not user.is_active_user
        db.session.commit()
        status = 'activated' if user.is_active_user else 'deactivated'
        flash(f'{user.full_name} has been {status}.', 'success')
    return redirect(url_for('superuser.users'))


@superuser_bp.route('/user/<int:user_id>/change-role', methods=['POST'])
@login_required
@role_required('superuser')
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role in ['employee', 'manager', 'superuser']:
        user.role = new_role
        user.is_approved = True
        db.session.commit()
        flash(f'{user.full_name} role changed to {new_role}.', 'success')
    return redirect(url_for('superuser.users'))


@superuser_bp.route('/skills')
@login_required
@role_required('superuser')
def skills_taxonomy():
    categories = SkillCategory.query.all()
    return render_template('superuser/skills.html', categories=categories)


@superuser_bp.route('/audit')
@login_required
@role_required('superuser')
def audit_logs():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('superuser/audit.html', logs=logs)


@superuser_bp.route('/analytics')
@login_required
@role_required('superuser')
def analytics():
    # Department distribution
    dept_counts = db.session.query(
        EmployeeProfile.department, func.count(EmployeeProfile.id)
    ).group_by(EmployeeProfile.department).all()

    # Workload stats
    workload_avg = db.session.query(func.avg(EmployeeProfile.current_workload)).scalar() or 0
    workload_dist = db.session.query(
        case(
            (EmployeeProfile.current_workload == 0, 'Free (0%)'),
            (EmployeeProfile.current_workload <= 30, 'Light (1-30%)'),
            (EmployeeProfile.current_workload <= 60, 'Moderate (31-60%)'),
            (EmployeeProfile.current_workload <= 80, 'Heavy (61-80%)'),
            else_='Overloaded (81-100%)'
        ).label('band'),
        func.count(EmployeeProfile.id)
    ).group_by('band').all()

    # Availability breakdown
    avail_dist = db.session.query(
        Availability.status, func.count(Availability.id)
    ).group_by(Availability.status).all()

    # Top skills (most common)
    top_skills = db.session.query(
        Skill.name, func.count(EmployeeSkill.id).label('cnt')
    ).join(EmployeeSkill, Skill.id == EmployeeSkill.skill_id
    ).group_by(Skill.name).order_by(func.count(EmployeeSkill.id).desc()).limit(20).all()

    # Experience distribution
    exp_dist = db.session.query(
        case(
            (EmployeeProfile.years_of_experience < 2, '0-2 yrs'),
            (EmployeeProfile.years_of_experience < 5, '2-5 yrs'),
            (EmployeeProfile.years_of_experience < 10, '5-10 yrs'),
            (EmployeeProfile.years_of_experience < 15, '10-15 yrs'),
            else_='15+ yrs'
        ).label('band'),
        func.count(EmployeeProfile.id)
    ).group_by('band').all()

    # Location distribution
    loc_dist = db.session.query(
        EmployeeProfile.location, func.count(EmployeeProfile.id)
    ).group_by(EmployeeProfile.location).order_by(func.count(EmployeeProfile.id).desc()).all()

    # Avg rating
    avg_rating = db.session.query(func.avg(EmployeeProfile.average_project_rating)).scalar() or 0

    # Recommendation stats
    rec_count = Recommendation.query.count()
    avg_confidence = db.session.query(func.avg(Recommendation.confidence_score)).scalar() or 0

    return render_template('superuser/analytics.html',
                          dept_counts=dept_counts,
                          workload_avg=round(workload_avg, 1),
                          workload_dist=workload_dist,
                          avail_dist=avail_dist,
                          top_skills=top_skills,
                          exp_dist=exp_dist,
                          loc_dist=loc_dist,
                          avg_rating=round(avg_rating, 1),
                          rec_count=rec_count,
                          avg_confidence=round(avg_confidence * 100, 1) if avg_confidence else 0)


@superuser_bp.route('/projects')
@login_required
@role_required('superuser')
def all_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('superuser/projects.html', projects=projects)


@superuser_bp.route('/comparison')
@login_required
@role_required('superuser', 'manager')
def llm_comparison():
    """LLM comparison methodology page."""
    return render_template('superuser/comparison.html')
