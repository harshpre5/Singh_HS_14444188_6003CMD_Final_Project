"""
SkillMatch Pro — Layers 7, 8, 9: Team Builder
Layer 7: Multi-Role Team Assembly (conflict-free)
Layer 8: Team Synergy Scoring
Layer 9: Skill Gap Detection
"""
import json
from app.models import (
    EmployeeProfile, EmployeeSkill, ProjectHistory,
    RoleRequirement, RoleConstraint, Skill
)


class TeamBuilder:
    """Assembles the optimal team across all roles, ensuring no conflicts."""

    def __init__(self, project):
        self.project = project
        self.roles = RoleRequirement.query.filter_by(project_id=project.id).all()

    def assemble_team(self, scored_candidates_per_role):
        """
        Layer 7: Multi-Role Team Assembly.
        Input: dict of {role_id: [scored_candidate_dicts]}
        Output: dict of {role_id: [selected_candidates]}, unassigned roles, conflicts resolved

        Algorithm:
        1. Sort roles by priority (critical first) and fewer candidates first
        2. For each role, pick top N candidates not yet assigned
        3. Track assigned employees to prevent conflicts
        """
        assigned_employee_ids = set()
        team = {}
        unassigned_roles = []
        conflict_log = []

        # Sort roles: critical priority first, then fewer candidates (harder to fill first)
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_roles = sorted(self.roles, key=lambda r: (
            priority_order.get(r.priority, 2),
            len(scored_candidates_per_role.get(r.id, []))
        ))

        for role in sorted_roles:
            candidates = scored_candidates_per_role.get(role.id, [])
            needed = role.quantity
            selected = []

            for candidate in candidates:
                if len(selected) >= needed:
                    break
                emp = candidate['employee']
                if emp.id not in assigned_employee_ids:
                    selected.append(candidate)
                    assigned_employee_ids.add(emp.id)
                else:
                    conflict_log.append({
                        'employee_id': emp.id,
                        'employee_name': emp.user.full_name,
                        'requested_role': role.role_title,
                        'reason': 'Already assigned to another role'
                    })

            team[role.id] = {
                'role': role,
                'selected': selected,
                'needed': needed,
                'filled': len(selected),
                'shortfall': max(0, needed - len(selected))
            }

            if len(selected) < needed:
                unassigned_roles.append({
                    'role_id': role.id,
                    'role_title': role.role_title,
                    'needed': needed,
                    'filled': len(selected),
                    'shortfall': needed - len(selected)
                })

        return {
            'team': team,
            'unassigned_roles': unassigned_roles,
            'conflict_log': conflict_log,
            'total_assigned': len(assigned_employee_ids)
        }

    def calculate_synergy(self, team_result):
        """
        Layer 8: Team Synergy Scoring.
        Checks if selected team members have collaborated on past projects.
        Higher overlap = higher synergy score.
        """
        all_selected = []
        for role_id, data in team_result['team'].items():
            for candidate in data['selected']:
                all_selected.append(candidate['employee'])

        if len(all_selected) < 2:
            return {'synergy_score': 0.0, 'collaboration_pairs': [], 'detail': 'Team too small for synergy analysis'}

        # Check project history for collaboration
        collaboration_pairs = []
        synergy_hits = 0
        total_pairs = 0

        for i in range(len(all_selected)):
            for j in range(i + 1, len(all_selected)):
                total_pairs += 1
                emp_a = all_selected[i]
                emp_b = all_selected[j]

                # Check if they collaborated
                history_a = ProjectHistory.query.filter_by(employee_profile_id=emp_a.id).all()
                for ph in history_a:
                    if ph.collaborated_with:
                        try:
                            collabs = json.loads(ph.collaborated_with)
                            if emp_b.user_id in collabs or emp_b.id in collabs:
                                synergy_hits += 1
                                collaboration_pairs.append({
                                    'employee_a': emp_a.user.full_name,
                                    'employee_b': emp_b.user.full_name,
                                    'project': ph.project_name,
                                    'rating': ph.rating
                                })
                                break
                        except (json.JSONDecodeError, TypeError):
                            continue

        synergy_score = round(synergy_hits / total_pairs, 4) if total_pairs > 0 else 0.0

        return {
            'synergy_score': synergy_score,
            'collaboration_pairs': collaboration_pairs,
            'total_pairs_checked': total_pairs,
            'collaborations_found': synergy_hits,
            'detail': f'{synergy_hits} collaboration(s) found among {total_pairs} possible pairs'
        }

    def detect_skill_gaps(self, team_result):
        """
        Layer 9: Skill Gap Detection.
        After team assembly, check if required skills are covered.
        """
        gaps = []

        for role_id, data in team_result['team'].items():
            role = data['role']
            selected = data['selected']

            # Get required skills for this role
            constraints = RoleConstraint.query.filter_by(
                role_requirement_id=role.id, is_active=True
            ).all()

            required_skills = set()
            for c in constraints:
                if c.constraint_type in ('mandatory_skill', 'min_proficiency'):
                    if c.parameter_name:
                        required_skills.add(c.parameter_name)

            # Check which skills the team covers
            team_skills = {}
            for candidate in selected:
                emp = candidate['employee']
                emp_skills = EmployeeSkill.query.filter_by(employee_profile_id=emp.id).all()
                for es in emp_skills:
                    skill_name = es.skill.name
                    if skill_name not in team_skills or es.proficiency > team_skills[skill_name]:
                        team_skills[skill_name] = es.proficiency

            # Identify gaps
            for skill_name in required_skills:
                if skill_name not in team_skills:
                    gaps.append({
                        'role': role.role_title,
                        'skill': skill_name,
                        'status': 'missing',
                        'detail': f'No team member has {skill_name}',
                        'severity': 'high'
                    })
                elif team_skills[skill_name] < 5:
                    gaps.append({
                        'role': role.role_title,
                        'skill': skill_name,
                        'status': 'weak',
                        'detail': f'Best proficiency in {skill_name} is {team_skills[skill_name]}/10',
                        'severity': 'medium'
                    })

        coverage = 1.0
        if gaps:
            high_gaps = len([g for g in gaps if g['severity'] == 'high'])
            med_gaps = len([g for g in gaps if g['severity'] == 'medium'])
            total_req = sum(1 for r in self.roles for c in RoleConstraint.query.filter_by(
                role_requirement_id=r.id, is_active=True
            ).all() if c.constraint_type in ('mandatory_skill', 'min_proficiency'))
            if total_req > 0:
                coverage = max(0, 1.0 - (high_gaps * 0.2 + med_gaps * 0.05))

        return {
            'gaps': gaps,
            'coverage_score': round(coverage, 4),
            'total_gaps': len(gaps),
            'high_severity': len([g for g in gaps if g['severity'] == 'high']),
            'medium_severity': len([g for g in gaps if g['severity'] == 'medium'])
        }
