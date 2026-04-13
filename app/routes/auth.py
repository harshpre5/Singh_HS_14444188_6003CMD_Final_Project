from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, AuditLog
import json

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active_user:
                flash('Your account has been deactivated. Contact admin.', 'danger')
                return render_template('auth/login.html')

            login_user(user)

            log = AuditLog(user_id=user.id, action='login', entity_type='user',
                          entity_id=user.id, ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()

            flash(f'Welcome back, {user.first_name}!', 'success')
            return _redirect_by_role(user)
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if not all([email, first_name, last_name, password]):
            errors.append('All fields are required.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html')

        import random
        colors = ['#6366F1', '#8B5CF6', '#EC4899', '#EF4444', '#F97316',
                  '#22C55E', '#14B8A6', '#06B6D4', '#3B82F6']

        user = User(
            email=email, first_name=first_name, last_name=last_name,
            role='employee', is_approved=False,
            avatar_color=random.choice(colors)
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        log = AuditLog(user_id=user.id, action='register', entity_type='user',
                      entity_id=user.id, ip_address=request.remote_addr,
                      details=json.dumps({"status": "pending_approval"}))
        db.session.add(log)
        db.session.commit()

        flash('Account created! Awaiting manager approval.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log = AuditLog(user_id=current_user.id, action='logout', entity_type='user',
                  entity_id=current_user.id, ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/pending')
@login_required
def pending():
    if current_user.is_approved:
        return _redirect_by_role(current_user)
    return render_template('auth/pending.html')


def _redirect_by_role(user):
    if user.role == 'superuser':
        return redirect(url_for('superuser.dashboard'))
    elif user.role == 'manager':
        return redirect(url_for('manager.dashboard'))
    else:
        if not user.is_approved:
            return redirect(url_for('auth.pending'))
        return redirect(url_for('employee.dashboard'))
