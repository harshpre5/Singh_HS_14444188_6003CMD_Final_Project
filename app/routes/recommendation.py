"""
SkillMatch Pro — Recommendation Routes
Constraint configuration, engine execution, results viewing,
manual selection, and project finalisation.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import (
    EmployeeProfile, Project, RoleRequirement, RoleConstraint,
    ScoringWeight, Recommendation, RecommendationCandidate, Skill, SkillCategory,
    Allocation, AuditLog
)
from app.services.constraint_engine import ConstraintEngine
from app.services.scoring_engine import ScoringEngine
from app.services.team_builder import TeamBuilder
from app.services.topsis_engine import AdvancedAnalysis
from app.services.explainability import ExplainabilityService
from app.utils.helpers import role_required
import json
from datetime import datetime

recommendation_bp = Blueprint('recommendation', __name__, url_prefix='/recommendation')


# ==================== CONSTRAINT CONFIGURATION ====================

@recommendation_bp.route('/role/<int:role_id>/constraints', methods=['GET', 'POST'])
@login_required
@role_required('manager', 'superuser')
def configure_constraints(role_id):
    role = RoleRequirement.query.get_or_404(role_id)
    project = Project.query.get_or_404(role.project_id)
    constraints = RoleConstraint.query.filter_by(role_requirement_id=role.id).all()
    skills = Skill.query.order_by(Skill.name).all()
    categories = SkillCategory.query.all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_constraint':
            c = RoleConstraint(
                role_requirement_id=role.id,
                constraint_type=request.form.get('constraint_type'),
                parameter_name=request.form.get('parameter_name', ''),
                parameter_value=request.form.get('parameter_value', ''),
                is_active=True
            )
            db.session.add(c)
            db.session.commit()
            flash('Constraint added!', 'success')

        elif action == 'remove_constraint':
            cid = int(request.form.get('constraint_id'))
            c = RoleConstraint.query.get(cid)
            if c and c.role_requirement_id == role.id:
                db.session.delete(c)
                db.session.commit()
                flash('Constraint removed.', 'info')

        elif action == 'toggle_constraint':
            cid = int(request.form.get('constraint_id'))
            c = RoleConstraint.query.get(cid)
            if c and c.role_requirement_id == role.id:
                c.is_active = not c.is_active
                db.session.commit()

        return redirect(url_for('recommendation.configure_constraints', role_id=role.id))

    constraint_types = [
        {'value': 'mandatory_skill', 'label': 'Must Have Skill', 'needs_skill': True, 'needs_value': False},
        {'value': 'min_proficiency', 'label': 'Minimum Proficiency', 'needs_skill': True, 'needs_value': True, 'value_label': 'Min Level (1-10)'},
        {'value': 'min_experience', 'label': 'Minimum Experience (Years)', 'needs_skill': False, 'needs_value': True, 'value_label': 'Min Years'},
        {'value': 'max_workload', 'label': 'Max Workload (%)', 'needs_skill': False, 'needs_value': True, 'value_label': 'Max %'},
        {'value': 'availability_overlap', 'label': 'Must Be Available', 'needs_skill': False, 'needs_value': False},
        {'value': 'required_certification', 'label': 'Required Certification', 'needs_skill': False, 'needs_value': False, 'has_text': True, 'text_label': 'Certification Name'},
        {'value': 'budget_cap', 'label': 'Max Hourly Rate (£)', 'needs_skill': False, 'needs_value': True, 'value_label': 'Max Rate'},
        {'value': 'min_project_rating', 'label': 'Min Project Rating', 'needs_skill': False, 'needs_value': True, 'value_label': 'Min Rating (1-5)'},
        {'value': 'location_required', 'label': 'Location Required', 'needs_skill': False, 'needs_value': True, 'value_label': 'Location'},
    ]

    return render_template('manager/constraints.html',
                          role=role, project=project, constraints=constraints,
                          skills=skills, categories=categories,
                          constraint_types=constraint_types)


@recommendation_bp.route('/role/<int:role_id>/weights', methods=['GET', 'POST'])
@login_required
@role_required('manager', 'superuser')
def configure_weights(role_id):
    role = RoleRequirement.query.get_or_404(role_id)
    project = Project.query.get_or_404(role.project_id)
    weights = ScoringWeight.query.filter_by(role_requirement_id=role.id).all()

    if not weights:
        defaults = {
            'skill_match': 0.25, 'experience': 0.15, 'availability': 0.15,
            'cost_efficiency': 0.10, 'project_success': 0.10,
            'versatility': 0.05, 'career_alignment': 0.10,
            'certification_relevance': 0.10
        }
        for criterion, weight in defaults.items():
            sw = ScoringWeight(role_requirement_id=role.id, criterion=criterion, weight=weight)
            db.session.add(sw)
        db.session.commit()
        weights = ScoringWeight.query.filter_by(role_requirement_id=role.id).all()

    if request.method == 'POST':
        for w in weights:
            val = request.form.get(f'weight_{w.criterion}')
            if val:
                w.weight = float(val) / 100.0
        db.session.commit()
        flash('Scoring weights updated!', 'success')
        return redirect(url_for('recommendation.configure_weights', role_id=role.id))

    criteria_labels = {
        'skill_match': {'label': 'Skill Match', 'icon': 'fa-code', 'desc': 'How well employee skills match requirements'},
        'experience': {'label': 'Experience', 'icon': 'fa-clock', 'desc': 'Years of professional experience'},
        'availability': {'label': 'Availability', 'icon': 'fa-calendar-check', 'desc': 'Current availability and hours'},
        'cost_efficiency': {'label': 'Cost Efficiency', 'icon': 'fa-pound-sign', 'desc': 'Hourly rate within budget'},
        'project_success': {'label': 'Project Success', 'icon': 'fa-star', 'desc': 'Average performance rating on past projects'},
        'versatility': {'label': 'Versatility', 'icon': 'fa-random', 'desc': 'Breadth of skills across domains'},
        'career_alignment': {'label': 'Career Alignment', 'icon': 'fa-bullseye', 'desc': 'Role matches employee career goals'},
        'certification_relevance': {'label': 'Certifications', 'icon': 'fa-certificate', 'desc': 'Relevant professional certifications'},
    }

    return render_template('manager/weights.html',
                          role=role, project=project, weights=weights,
                          criteria_labels=criteria_labels)


# ==================== RUN ENGINE ====================

@recommendation_bp.route('/project/<int:project_id>/run', methods=['POST'])
@login_required
@role_required('manager', 'superuser')
def run_engine(project_id):
    project = Project.query.get_or_404(project_id)
    roles = RoleRequirement.query.filter_by(project_id=project.id).all()

    if not roles:
        flash('Add at least one role requirement before running the engine.', 'warning')
        return redirect(url_for('manager.edit_project', project_id=project.id))

    all_employees = EmployeeProfile.query.join(
        EmployeeProfile.user
    ).filter(
        EmployeeProfile.user.has(role='employee', is_approved=True, is_active_user=True)
    ).all()

    if not all_employees:
        flash('No approved employees found in the system.', 'warning')
        return redirect(url_for('manager.edit_project', project_id=project.id))

    # LAYER 1: Hard Constraint Filtering
    passed_per_role = {}
    failed_per_role = {}
    relaxation_per_role = {}

    for role in roles:
        engine = ConstraintEngine(role, project)
        passed, failed = engine.filter_candidates(all_employees)
        passed_per_role[role.id] = passed
        failed_per_role[role.id] = failed
        if not passed:
            suggestions = engine.suggest_relaxations(failed)
            relaxation_per_role[role.id] = suggestions

    # LAYERS 2,4,5,6: Scoring
    scored_per_role = {}
    weights_snapshot = {}

    for role in roles:
        candidates = passed_per_role.get(role.id, [])
        if not candidates:
            scored_per_role[role.id] = []
            continue
        scoring = ScoringEngine(role, project)
        scored = scoring.score_candidates(candidates, len(all_employees))
        scored_per_role[role.id] = scored
        weights_snapshot[str(role.id)] = scoring.weights

    # LAYER 7: Team Assembly
    builder = TeamBuilder(project)
    team_result = builder.assemble_team(scored_per_role)

    # LAYER 8: Synergy
    synergy = builder.calculate_synergy(team_result)

    # LAYER 9: Skill Gaps
    skill_gaps = builder.detect_skill_gaps(team_result)

    # LAYERS 10,11,12: Advanced Analysis
    analysis = AdvancedAnalysis(project, roles)
    pareto = analysis.generate_pareto_alternatives(passed_per_role, team_result)
    base_weights = weights_snapshot.get(str(roles[0].id), ScoringEngine.DEFAULT_WEIGHTS)
    sensitivity = analysis.run_sensitivity_analysis(passed_per_role, base_weights)
    monte_carlo = analysis.run_monte_carlo(passed_per_role, base_weights, iterations=200)

    # LAYER 13: Store & Explain
    explainer = ExplainabilityService(project, current_user.id)
    rec = explainer.create_recommendation_record(
        team_result=team_result,
        scored_per_role=scored_per_role,
        failed_per_role=failed_per_role,
        synergy=synergy,
        skill_gaps=skill_gaps,
        pareto_alternatives=pareto,
        sensitivity=sensitivity,
        monte_carlo=monte_carlo,
        weights_snapshot=weights_snapshot,
        relaxation_suggestions=relaxation_per_role,
    )

    project.status = 'in_progress'
    db.session.commit()

    flash('Recommendation engine completed! Review and select your team below.', 'success')
    return redirect(url_for('recommendation.view_results', recommendation_id=rec.id))


# ==================== VIEW RESULTS ====================

@recommendation_bp.route('/results/<int:recommendation_id>')
@login_required
@role_required('manager', 'superuser')
def view_results(recommendation_id):
    details = ExplainabilityService.get_recommendation_details(recommendation_id)
    if not details:
        flash('Recommendation not found.', 'danger')
        return redirect(url_for('manager.dashboard'))

    rec = details['recommendation']
    project = Project.query.get(rec.project_id)
    roles = RoleRequirement.query.filter_by(project_id=project.id).all()

    return render_template('manager/results.html',
                          rec=rec, project=project, roles=roles,
                          by_role=details['by_role'],
                          pareto=details['pareto'],
                          sensitivity=details['sensitivity'],
                          skill_gaps=details['skill_gaps'],
                          params=details['parameters'])


# ==================== TOGGLE CANDIDATE SELECTION ====================

@recommendation_bp.route('/toggle_select/<int:candidate_id>', methods=['POST'])
@login_required
@role_required('manager', 'superuser')
def toggle_selection(candidate_id):
    candidate = RecommendationCandidate.query.get_or_404(candidate_id)
    rec = Recommendation.query.get(candidate.recommendation_id)

    if not candidate.hard_constraint_pass:
        flash('Cannot select a candidate who failed hard constraints.', 'danger')
        return redirect(url_for('recommendation.view_results', recommendation_id=rec.id))

    # Toggle selection
    candidate.is_selected = not candidate.is_selected
    candidate.is_manually_overridden = True
    db.session.commit()

    status = 'selected' if candidate.is_selected else 'deselected'
    flash(f'{candidate.employee_profile.user.full_name} has been {status}.', 'success')
    return redirect(url_for('recommendation.view_results', recommendation_id=rec.id))


# ==================== FINALISE PROJECT ====================

@recommendation_bp.route('/finalise/<int:recommendation_id>', methods=['POST'])
@login_required
@role_required('manager', 'superuser')
def finalise_project(recommendation_id):
    rec = Recommendation.query.get_or_404(recommendation_id)
    project = Project.query.get_or_404(rec.project_id)

    # Get all selected candidates
    selected = RecommendationCandidate.query.filter_by(
        recommendation_id=rec.id, is_selected=True
    ).all()

    if not selected:
        flash('Please select at least one team member before finalising.', 'warning')
        return redirect(url_for('recommendation.view_results', recommendation_id=rec.id))

    # Check for double assignments
    emp_ids = [c.employee_profile_id for c in selected]
    if len(emp_ids) != len(set(emp_ids)):
        flash('Error: An employee is selected for multiple roles. Please fix before finalising.', 'danger')
        return redirect(url_for('recommendation.view_results', recommendation_id=rec.id))

    # Create allocations for each selected candidate
    for candidate in selected:
        existing = Allocation.query.filter_by(
            employee_profile_id=candidate.employee_profile_id,
            project_id=project.id
        ).first()
        if not existing:
            alloc = Allocation(
                employee_profile_id=candidate.employee_profile_id,
                project_id=project.id,
                role_requirement_id=candidate.role_requirement_id,
                recommendation_id=rec.id,
                status='allocated',
                start_date=project.start_date,
                end_date=project.end_date
            )
            db.session.add(alloc)

    # Update statuses
    rec.status = 'approved'
    project.status = 'completed'

    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        action='finalise_project',
        entity_type='project',
        entity_id=project.id,
        details=json.dumps({
            'recommendation_id': rec.id,
            'team_size': len(selected),
            'members': [c.employee_profile.user.full_name for c in selected]
        }),
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    flash(f'Project "{project.name}" finalised with {len(selected)} team members!', 'success')
    return redirect(url_for('recommendation.view_finalised', project_id=project.id))


# ==================== VIEW FINALISED PROJECT ====================

@recommendation_bp.route('/finalised/<int:project_id>')
@login_required
@role_required('manager', 'superuser')
def view_finalised(project_id):
    project = Project.query.get_or_404(project_id)
    roles = RoleRequirement.query.filter_by(project_id=project.id).all()
    allocations = Allocation.query.filter_by(project_id=project.id).all()

    # Get the latest recommendation
    rec = Recommendation.query.filter_by(
        project_id=project.id, status='approved'
    ).order_by(Recommendation.created_at.desc()).first()

    # Group allocations by role
    team_by_role = {}
    for alloc in allocations:
        role_id = alloc.role_requirement_id
        if role_id not in team_by_role:
            role = RoleRequirement.query.get(role_id)
            team_by_role[role_id] = {'role': role, 'members': []}
        team_by_role[role_id]['members'].append(alloc)

    return render_template('manager/finalised.html',
                          project=project, roles=roles, rec=rec,
                          team_by_role=team_by_role,
                          total_allocated=len(allocations))


# ==================== CANDIDATE DETAIL ====================

@recommendation_bp.route('/candidate/<int:candidate_id>')
@login_required
@role_required('manager', 'superuser')
def candidate_detail(candidate_id):
    candidate = RecommendationCandidate.query.get_or_404(candidate_id)
    rec = Recommendation.query.get(candidate.recommendation_id)
    project = Project.query.get(rec.project_id)

    breakdown = json.loads(candidate.score_breakdown) if candidate.score_breakdown else {}
    rejection = json.loads(candidate.rejection_reasons) if candidate.rejection_reasons else []
    selection = json.loads(candidate.selection_reasons) if candidate.selection_reasons else []
    decay = json.loads(candidate.decay_adjusted_skills) if candidate.decay_adjusted_skills else {}

    return render_template('manager/candidate_detail.html',
                          candidate=candidate, rec=rec, project=project,
                          breakdown=breakdown, rejection=rejection,
                          selection=selection, decay=decay)


# ==================== API ====================

@recommendation_bp.route('/api/skills')
@login_required
def api_skills():
    q = request.args.get('q', '')
    cat_id = request.args.get('category', None)
    query = Skill.query
    if q:
        query = query.filter(Skill.name.ilike(f'%{q}%'))
    if cat_id:
        query = query.filter_by(category_id=int(cat_id))
    skills = query.order_by(Skill.name).limit(50).all()
    return jsonify([{'id': s.id, 'name': s.name, 'category': s.category.name} for s in skills])