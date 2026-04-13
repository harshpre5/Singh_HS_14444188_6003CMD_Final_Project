from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import (
    EmployeeProfile, EmployeeSkill, EmployeeCertification,
    Availability, ProjectHistory, Skill, SkillCategory
)
from app.utils.helpers import role_required, approval_required
from datetime import datetime

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')


@employee_bp.route('/dashboard')
@login_required
@role_required('employee')
@approval_required
def dashboard():
    profile = EmployeeProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('employee/dashboard.html', profile=profile)


@employee_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('employee')
@approval_required
def profile():
    profile = EmployeeProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        if not profile:
            profile = EmployeeProfile(user_id=current_user.id)
            db.session.add(profile)

        profile.department = request.form.get('department', '')
        profile.job_title = request.form.get('job_title', '')
        profile.years_of_experience = float(request.form.get('years_of_experience', 0))
        profile.hourly_rate = float(request.form.get('hourly_rate', 0))
        profile.bio = request.form.get('bio', '')
        profile.phone = request.form.get('phone', '')
        profile.location = request.form.get('location', '')
        profile.career_goal = request.form.get('career_goal', '')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('employee.profile'))

    return render_template('employee/profile.html', profile=profile)


@employee_bp.route('/skills', methods=['GET', 'POST'])
@login_required
@role_required('employee')
@approval_required
def skills():
    profile = EmployeeProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('employee.profile'))

    categories = SkillCategory.query.all()
    all_skills = Skill.query.order_by(Skill.name).all()
    my_skills = EmployeeSkill.query.filter_by(employee_profile_id=profile.id).all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_skill':
            skill_id = int(request.form.get('skill_id'))
            proficiency = int(request.form.get('proficiency', 5))
            years_used = float(request.form.get('years_used', 0))
            is_primary = request.form.get('is_primary') == 'on'

            existing = EmployeeSkill.query.filter_by(
                employee_profile_id=profile.id, skill_id=skill_id
            ).first()
            if existing:
                flash('You already have this skill listed.', 'warning')
            else:
                es = EmployeeSkill(
                    employee_profile_id=profile.id,
                    skill_id=skill_id,
                    proficiency=proficiency,
                    years_used=years_used,
                    last_used_date=datetime.today().date(),
                    is_primary=is_primary
                )
                db.session.add(es)
                db.session.commit()
                flash('Skill added!', 'success')

        elif action == 'remove_skill':
            skill_entry_id = int(request.form.get('skill_entry_id'))
            entry = EmployeeSkill.query.get(skill_entry_id)
            if entry and entry.employee_profile_id == profile.id:
                db.session.delete(entry)
                db.session.commit()
                flash('Skill removed.', 'info')

        elif action == 'update_skill':
            skill_entry_id = int(request.form.get('skill_entry_id'))
            entry = EmployeeSkill.query.get(skill_entry_id)
            if entry and entry.employee_profile_id == profile.id:
                entry.proficiency = int(request.form.get('proficiency', entry.proficiency))
                entry.years_used = float(request.form.get('years_used', entry.years_used))
                entry.last_used_date = datetime.today().date()
                entry.is_primary = request.form.get('is_primary') == 'on'
                db.session.commit()
                flash('Skill updated!', 'success')

        return redirect(url_for('employee.skills'))

    return render_template('employee/skills.html',
                          profile=profile, categories=categories,
                          all_skills=all_skills, my_skills=my_skills)


@employee_bp.route('/availability', methods=['GET', 'POST'])
@login_required
@role_required('employee')
@approval_required
def availability():
    profile = EmployeeProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('employee.profile'))

    avail = Availability.query.filter_by(employee_profile_id=profile.id).first()

    if request.method == 'POST':
        if not avail:
            avail = Availability(employee_profile_id=profile.id)
            db.session.add(avail)

        avail.status = request.form.get('status', 'available')
        avail.reason = request.form.get('reason', '')
        avail.current_project_name = request.form.get('current_project_name', '')
        avail.hours_per_week_available = float(request.form.get('hours_per_week_available', 40))
        avail.notes = request.form.get('notes', '')

        avail_from = request.form.get('available_from')
        avail_until = request.form.get('available_until')
        if avail_from:
            avail.available_from = datetime.strptime(avail_from, '%Y-%m-%d').date()
        if avail_until:
            avail.available_until = datetime.strptime(avail_until, '%Y-%m-%d').date()

        # Update workload on profile too
        profile.current_workload = float(request.form.get('current_workload', profile.current_workload))

        db.session.commit()
        flash('Availability updated!', 'success')
        return redirect(url_for('employee.availability'))

    return render_template('employee/availability.html', profile=profile, avail=avail)


@employee_bp.route('/certifications', methods=['GET', 'POST'])
@login_required
@role_required('employee')
@approval_required
def certifications():
    profile = EmployeeProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('employee.profile'))

    certs = EmployeeCertification.query.filter_by(employee_profile_id=profile.id).all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            cert = EmployeeCertification(
                employee_profile_id=profile.id,
                name=request.form.get('name'),
                issuing_body=request.form.get('issuing_body'),
                credential_id=request.form.get('credential_id')
            )
            d = request.form.get('date_obtained')
            if d:
                cert.date_obtained = datetime.strptime(d, '%Y-%m-%d').date()
            e = request.form.get('expiry_date')
            if e:
                cert.expiry_date = datetime.strptime(e, '%Y-%m-%d').date()
            db.session.add(cert)
            db.session.commit()
            flash('Certification added!', 'success')

        elif action == 'remove':
            cert_id = int(request.form.get('cert_id'))
            cert = EmployeeCertification.query.get(cert_id)
            if cert and cert.employee_profile_id == profile.id:
                db.session.delete(cert)
                db.session.commit()
                flash('Certification removed.', 'info')

        return redirect(url_for('employee.certifications'))

    return render_template('employee/certifications.html', profile=profile, certs=certs)


@employee_bp.route('/insights')
@login_required
@role_required('employee')
@approval_required
def insights():
    """Show employee how they've been scored in recommendations."""
    profile = EmployeeProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('employee.profile'))

    from app.models import RecommendationCandidate, Recommendation, Project, RoleRequirement
    import json

    entries = RecommendationCandidate.query.filter_by(
        employee_profile_id=profile.id
    ).order_by(RecommendationCandidate.created_at.desc()).all()

    results = []
    for entry in entries:
        rec = Recommendation.query.get(entry.recommendation_id)
        project = Project.query.get(rec.project_id) if rec else None
        role = RoleRequirement.query.get(entry.role_requirement_id)
        breakdown = json.loads(entry.score_breakdown) if entry.score_breakdown else {}
        rejection = json.loads(entry.rejection_reasons) if entry.rejection_reasons else []
        selection = json.loads(entry.selection_reasons) if entry.selection_reasons else []

        results.append({
            'entry': entry,
            'project': project,
            'role': role,
            'breakdown': breakdown,
            'rejection': rejection,
            'selection': selection,
            'date': rec.run_timestamp if rec else None
        })

    return render_template('employee/insights.html', profile=profile, results=results)
