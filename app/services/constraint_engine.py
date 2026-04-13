"""
SkillMatch Pro — Layer 1: Hard Constraint Filter
+ Layer 3: Constraint Relaxation Suggestions

Dynamically reads manager-defined constraints from the database.
Nothing is hardcoded — all constraints come from RoleConstraint table.
"""
import json
from datetime import date, timedelta
from app.models import (
    EmployeeProfile, EmployeeSkill, EmployeeCertification,
    Availability, Skill, RoleConstraint
)


class ConstraintEngine:
    """Applies hard constraints to filter candidates. Returns pass/fail + reasons."""

    # Map constraint_type to handler method
    CONSTRAINT_HANDLERS = {
        'mandatory_skill': '_check_mandatory_skill',
        'min_proficiency': '_check_min_proficiency',
        'min_experience': '_check_min_experience',
        'max_workload': '_check_max_workload',
        'availability_overlap': '_check_availability_overlap',
        'required_certification': '_check_required_certification',
        'budget_cap': '_check_budget_cap',
        'min_project_rating': '_check_min_project_rating',
        'max_current_projects': '_check_max_current_projects',
        'location_required': '_check_location',
    }

    def __init__(self, role_requirement, project):
        self.role_requirement = role_requirement
        self.project = project
        self.constraints = RoleConstraint.query.filter_by(
            role_requirement_id=role_requirement.id,
            is_active=True
        ).all()

    def filter_candidates(self, employees):
        """
        Filter a list of EmployeeProfile objects through all hard constraints.
        Returns:
            passed: list of (employee, details_dict)
            failed: list of (employee, rejection_reasons_list)
        """
        passed = []
        failed = []

        for emp in employees:
            rejection_reasons = []
            constraint_details = {}

            for constraint in self.constraints:
                handler_name = self.CONSTRAINT_HANDLERS.get(constraint.constraint_type)
                if not handler_name:
                    continue

                handler = getattr(self, handler_name)
                result = handler(emp, constraint)

                if not result['passed']:
                    rejection_reasons.append(result['reason'])
                constraint_details[constraint.constraint_type] = result

            if rejection_reasons:
                failed.append((emp, rejection_reasons))
            else:
                passed.append((emp, constraint_details))

        return passed, failed

    def suggest_relaxations(self, failed_candidates):
        """
        Layer 3: If zero candidates pass, suggest which constraint to relax.
        Returns list of suggestions: {constraint, current_value, suggested_value, unlocks_count}
        """
        suggestions = []

        for constraint in self.constraints:
            # Count how many failed candidates would pass if we relax this one
            unlocked = 0
            for emp, reasons in failed_candidates:
                # Check if this constraint is the ONLY reason they failed
                handler_name = self.CONSTRAINT_HANDLERS.get(constraint.constraint_type)
                if not handler_name:
                    continue
                handler = getattr(self, handler_name)
                result = handler(emp, constraint)
                if not result['passed']:
                    # This constraint blocks them
                    other_reasons = [r for r in reasons if r != result.get('reason', '')]
                    if len(other_reasons) == 0:
                        # This is their only blocker
                        unlocked += 1

            if unlocked > 0:
                suggestion = self._build_relaxation_suggestion(constraint, unlocked)
                if suggestion:
                    suggestions.append(suggestion)

        suggestions.sort(key=lambda x: x['unlocks_count'], reverse=True)
        return suggestions

    def _build_relaxation_suggestion(self, constraint, unlocked):
        """Build a human-readable relaxation suggestion."""
        ctype = constraint.constraint_type
        value = constraint.parameter_value

        if ctype == 'min_proficiency':
            try:
                current = int(value)
                suggested = max(1, current - 2)
                return {
                    'constraint_type': ctype,
                    'parameter_name': constraint.parameter_name,
                    'current_value': str(current),
                    'suggested_value': str(suggested),
                    'unlocks_count': unlocked,
                    'description': f"Lower minimum proficiency for '{constraint.parameter_name}' from {current} to {suggested}"
                }
            except (ValueError, TypeError):
                return None
        elif ctype == 'min_experience':
            try:
                current = float(value)
                suggested = max(0, current - 2)
                return {
                    'constraint_type': ctype,
                    'parameter_name': constraint.parameter_name,
                    'current_value': str(current),
                    'suggested_value': str(suggested),
                    'unlocks_count': unlocked,
                    'description': f"Lower minimum experience from {current} to {suggested} years"
                }
            except (ValueError, TypeError):
                return None
        elif ctype == 'max_workload':
            try:
                current = float(value)
                suggested = min(100, current + 15)
                return {
                    'constraint_type': ctype,
                    'parameter_name': constraint.parameter_name,
                    'current_value': str(current),
                    'suggested_value': str(suggested),
                    'unlocks_count': unlocked,
                    'description': f"Raise maximum workload cap from {current}% to {suggested}%"
                }
            except (ValueError, TypeError):
                return None
        elif ctype == 'mandatory_skill':
            return {
                'constraint_type': ctype,
                'parameter_name': constraint.parameter_name,
                'current_value': 'Required',
                'suggested_value': 'Remove requirement',
                'unlocks_count': unlocked,
                'description': f"Remove mandatory requirement for skill '{constraint.parameter_name}'"
            }
        elif ctype == 'required_certification':
            return {
                'constraint_type': ctype,
                'parameter_name': constraint.parameter_name,
                'current_value': 'Required',
                'suggested_value': 'Make optional',
                'unlocks_count': unlocked,
                'description': f"Make certification '{constraint.parameter_name}' optional instead of required"
            }

        return None

    # ==================== CONSTRAINT HANDLERS ====================

    def _check_mandatory_skill(self, emp, constraint):
        """Employee must have the specified skill (any level)."""
        skill_name = constraint.parameter_name
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            return {'passed': True, 'reason': '', 'detail': f'Skill {skill_name} not found in system'}

        has_skill = EmployeeSkill.query.filter_by(
            employee_profile_id=emp.id, skill_id=skill.id
        ).first()

        if has_skill:
            return {'passed': True, 'reason': '', 'detail': f'Has {skill_name} at level {has_skill.proficiency}'}
        return {
            'passed': False,
            'reason': f'Missing mandatory skill: {skill_name}',
            'detail': f'Does not have skill: {skill_name}'
        }

    def _check_min_proficiency(self, emp, constraint):
        """Employee must have skill at minimum proficiency level."""
        skill_name = constraint.parameter_name
        min_level = int(constraint.parameter_value)
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            return {'passed': True, 'reason': '', 'detail': 'Skill not found'}

        emp_skill = EmployeeSkill.query.filter_by(
            employee_profile_id=emp.id, skill_id=skill.id
        ).first()

        if not emp_skill:
            return {
                'passed': False,
                'reason': f'Missing skill {skill_name} (need level {min_level}+)',
                'detail': f'Does not have {skill_name}'
            }
        if emp_skill.proficiency >= min_level:
            return {'passed': True, 'reason': '', 'detail': f'{skill_name} at {emp_skill.proficiency}/{min_level}'}
        return {
            'passed': False,
            'reason': f'{skill_name} proficiency {emp_skill.proficiency} < required {min_level}',
            'detail': f'{skill_name}: {emp_skill.proficiency}/{min_level}'
        }

    def _check_min_experience(self, emp, constraint):
        """Employee must have minimum years of experience."""
        min_years = float(constraint.parameter_value)
        if emp.years_of_experience >= min_years:
            return {'passed': True, 'reason': '', 'detail': f'{emp.years_of_experience} >= {min_years} years'}
        return {
            'passed': False,
            'reason': f'Experience {emp.years_of_experience} yrs < required {min_years} yrs',
            'detail': f'{emp.years_of_experience}/{min_years} years'
        }

    def _check_max_workload(self, emp, constraint):
        """Employee's current workload must not exceed the cap."""
        max_wl = float(constraint.parameter_value)
        if emp.current_workload <= max_wl:
            return {'passed': True, 'reason': '', 'detail': f'Workload {emp.current_workload}% <= {max_wl}%'}
        return {
            'passed': False,
            'reason': f'Workload {emp.current_workload}% exceeds cap of {max_wl}%',
            'detail': f'{emp.current_workload}%/{max_wl}%'
        }

    def _check_availability_overlap(self, emp, constraint):
        """Employee must be available (not fully_busy or on_leave)."""
        avail = Availability.query.filter_by(employee_profile_id=emp.id).first()
        if not avail:
            return {'passed': True, 'reason': '', 'detail': 'No availability set (assumed available)'}

        blocked = ['fully_busy', 'on_leave']
        required = constraint.parameter_value or 'not_blocked'

        if required == 'available_only' and avail.status != 'available':
            return {
                'passed': False,
                'reason': f'Status is {avail.status}, must be fully available',
                'detail': f'Status: {avail.status}'
            }

        if avail.status in blocked:
            return {
                'passed': False,
                'reason': f'Employee is {avail.status.replace("_", " ")}',
                'detail': f'Status: {avail.status}'
            }

        return {'passed': True, 'reason': '', 'detail': f'Status: {avail.status}'}

    def _check_required_certification(self, emp, constraint):
        """Employee must hold a specific certification."""
        cert_name = constraint.parameter_name
        has_cert = EmployeeCertification.query.filter_by(
            employee_profile_id=emp.id
        ).filter(EmployeeCertification.name.ilike(f'%{cert_name}%')).first()

        if has_cert:
            return {'passed': True, 'reason': '', 'detail': f'Has: {has_cert.name}'}
        return {
            'passed': False,
            'reason': f'Missing certification: {cert_name}',
            'detail': f'Does not have {cert_name}'
        }

    def _check_budget_cap(self, emp, constraint):
        """Employee hourly rate must be within budget cap."""
        max_rate = float(constraint.parameter_value)
        if emp.hourly_rate <= max_rate:
            return {'passed': True, 'reason': '', 'detail': f'Rate £{emp.hourly_rate} <= £{max_rate}'}
        return {
            'passed': False,
            'reason': f'Hourly rate £{emp.hourly_rate} exceeds cap £{max_rate}',
            'detail': f'£{emp.hourly_rate}/£{max_rate}'
        }

    def _check_min_project_rating(self, emp, constraint):
        """Employee average project rating must meet minimum."""
        min_rating = float(constraint.parameter_value)
        if emp.average_project_rating >= min_rating:
            return {'passed': True, 'reason': '', 'detail': f'Rating {emp.average_project_rating} >= {min_rating}'}
        return {
            'passed': False,
            'reason': f'Project rating {emp.average_project_rating} < required {min_rating}',
            'detail': f'{emp.average_project_rating}/{min_rating}'
        }

    def _check_max_current_projects(self, emp, constraint):
        """Employee must not be on too many active projects."""
        from app.models import Allocation
        max_proj = int(constraint.parameter_value)
        active = Allocation.query.filter_by(
            employee_profile_id=emp.id, status='active'
        ).count()
        if active <= max_proj:
            return {'passed': True, 'reason': '', 'detail': f'{active} active projects <= {max_proj}'}
        return {
            'passed': False,
            'reason': f'On {active} active projects, max is {max_proj}',
            'detail': f'{active}/{max_proj} projects'
        }

    def _check_location(self, emp, constraint):
        """Employee must be in a specific location."""
        required_loc = constraint.parameter_value
        if not required_loc:
            return {'passed': True, 'reason': '', 'detail': 'No location required'}
        if emp.location and required_loc.lower() in emp.location.lower():
            return {'passed': True, 'reason': '', 'detail': f'Location: {emp.location}'}
        return {
            'passed': False,
            'reason': f'Location {emp.location or "unknown"} does not match {required_loc}',
            'detail': f'{emp.location}/{required_loc}'
        }
