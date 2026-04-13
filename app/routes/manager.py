from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import (
    User, EmployeeProfile, Project, RoleRequirement,
    RoleConstraint, ScoringWeight, Recommendation, AuditLog
)
from app.utils.helpers import role_required
import json

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')


@manager_bp.route('/dashboard')
@login_required
@role_required('manager', 'superuser')
def dashboard():
    projects = Project.query.filter_by(manager_id=current_user.id).all()
    pending_users = User.query.filter_by(is_approved=False, role='employee').all()
    total_employees = EmployeeProfile.query.count()
    return render_template('manager/dashboard.html',
                          projects=projects, pending_users=pending_users,
                          total_employees=total_employees)


@manager_bp.route('/approve/<int:user_id>', methods=['POST'])
@login_required
@role_required('manager', 'superuser')
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    log = AuditLog(user_id=current_user.id, action='approve_user',
                  entity_type='user', entity_id=user_id,
                  details=json.dumps({"approved_by": current_user.id}),
                  ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    flash(f'{user.full_name} has been approved.', 'success')
    return redirect(url_for('manager.dashboard'))


@manager_bp.route('/reject/<int:user_id>', methods=['POST'])
@login_required
@role_required('manager', 'superuser')
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    log = AuditLog(user_id=current_user.id, action='reject_user',
                  entity_type='user', entity_id=user_id,
                  ip_address=request.remote_addr)
    db.session.add(log)
    db.session.delete(user)
    db.session.commit()
    flash('User registration rejected.', 'info')
    return redirect(url_for('manager.dashboard'))


@manager_bp.route('/employees')
@login_required
@role_required('manager', 'superuser')
def employee_list():
    employees = db.session.query(User, EmployeeProfile).join(
        EmployeeProfile, User.id == EmployeeProfile.user_id
    ).filter(User.role == 'employee', User.is_approved == True).all()
    return render_template('manager/employees.html', employees=employees)


@manager_bp.route('/employee/<int:user_id>')
@login_required
@role_required('manager', 'superuser')
def view_employee(user_id):
    user = User.query.get_or_404(user_id)
    profile = EmployeeProfile.query.filter_by(user_id=user_id).first()
    return render_template('manager/view_employee.html', emp_user=user, profile=profile)


@manager_bp.route('/projects')
@login_required
@role_required('manager', 'superuser')
def projects():
    projects = Project.query.filter_by(manager_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template('manager/projects.html', projects=projects)


@manager_bp.route('/project/new', methods=['GET', 'POST'])
@login_required
@role_required('manager', 'superuser')
def create_project():
    if request.method == 'POST':
        from datetime import datetime
        project = Project(
            name=request.form.get('name'),
            description=request.form.get('description'),
            manager_id=current_user.id,
            priority=request.form.get('priority', 'medium'),
            budget=float(request.form.get('budget', 0)) if request.form.get('budget') else None,
        )
        sd = request.form.get('start_date')
        ed = request.form.get('end_date')
        if sd:
            project.start_date = datetime.strptime(sd, '%Y-%m-%d').date()
        if ed:
            project.end_date = datetime.strptime(ed, '%Y-%m-%d').date()

        db.session.add(project)
        db.session.commit()

        log = AuditLog(user_id=current_user.id, action='create_project',
                      entity_type='project', entity_id=project.id,
                      ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()

        flash('Project created! Now add role requirements.', 'success')
        return redirect(url_for('manager.edit_project', project_id=project.id))

    return render_template('manager/create_project.html')


@manager_bp.route('/project/<int:project_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager', 'superuser')
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    roles = RoleRequirement.query.filter_by(project_id=project_id).all()
    return render_template('manager/edit_project.html', project=project, roles=roles)


@manager_bp.route('/project/<int:project_id>/add_role', methods=['POST'])
@login_required
@role_required('manager', 'superuser')
def add_role(project_id):
    project = Project.query.get_or_404(project_id)
    role = RoleRequirement(
        project_id=project.id,
        role_title=request.form.get('role_title'),
        quantity=int(request.form.get('quantity', 1)),
        description=request.form.get('description', ''),
        priority=request.form.get('priority', 'medium')
    )
    db.session.add(role)
    db.session.commit()

    # Add default scoring weights
    default_weights = {
        'skill_match': 0.25, 'experience': 0.15, 'availability': 0.15,
        'cost_efficiency': 0.10, 'project_success': 0.10,
        'versatility': 0.05, 'career_alignment': 0.10,
        'certification_relevance': 0.10
    }
    for criterion, weight in default_weights.items():
        sw = ScoringWeight(role_requirement_id=role.id, criterion=criterion, weight=weight)
        db.session.add(sw)
    db.session.commit()

    flash(f'Role "{role.role_title}" added with default weights.', 'success')
    return redirect(url_for('manager.edit_project', project_id=project_id))
