"""
SkillMatch Pro — Layer 13: Explainability & Audit
Full decision logging with human-readable explanations.
"""
import json
from datetime import datetime
from app.extensions import db
from app.models import (
    Recommendation, RecommendationCandidate, AuditLog
)


class ExplainabilityService:
    """Generates explanations and stores all recommendation data."""

    def __init__(self, project, user_id):
        self.project = project
        self.user_id = user_id

    def create_recommendation_record(self, team_result, scored_per_role,
                                       failed_per_role, synergy, skill_gaps,
                                       pareto_alternatives, sensitivity,
                                       monte_carlo, weights_snapshot,
                                       relaxation_suggestions):
        """
        Store the full recommendation run in the database.
        Every decision is logged for auditability.
        """
        rec = Recommendation(
            project_id=self.project.id,
            run_timestamp=datetime.utcnow(),
            status='generated',
            parameters_snapshot=json.dumps(weights_snapshot, default=str),
            team_synergy_score=synergy.get('synergy_score', 0),
            skill_gap_report=json.dumps(skill_gaps, default=str),
            confidence_score=monte_carlo.get('overall_confidence', 0),
            pareto_alternatives=json.dumps(self._serialize_pareto(pareto_alternatives), default=str),
            sensitivity_report=json.dumps(sensitivity, default=str),
        )
        db.session.add(rec)
        db.session.flush()

        # Store each candidate (selected AND rejected)
        for role_id, scored_list in scored_per_role.items():
            team_data = team_result['team'].get(role_id, {})
            selected_ids = set()
            for s in team_data.get('selected', []):
                selected_ids.add(s['employee'].id)

            for candidate in scored_list:
                emp = candidate['employee']
                is_selected = emp.id in selected_ids

                selection_reasons = []
                if is_selected:
                    selection_reasons = self._build_selection_reasons(candidate)

                rc = RecommendationCandidate(
                    recommendation_id=rec.id,
                    employee_profile_id=emp.id,
                    role_requirement_id=role_id,
                    rank=candidate.get('rank', 0),
                    overall_score=candidate.get('final_score', 0),
                    is_selected=is_selected,
                    score_breakdown=json.dumps(candidate.get('score_breakdown', {})),
                    hard_constraint_pass=True,
                    rejection_reasons=json.dumps([]),
                    selection_reasons=json.dumps(selection_reasons),
                    decay_adjusted_skills=json.dumps(candidate.get('decay_details', {}), default=str),
                    career_alignment_score=candidate.get('career_alignment_score', 0),
                    workload_fairness_penalty=candidate.get('fairness_penalty', 0),
                    topsis_closeness=candidate.get('topsis_closeness', 0),
                )
                db.session.add(rc)

        # Store rejected candidates (failed hard constraints)
        for role_id, failed_list in failed_per_role.items():
            for emp, reasons in failed_list:
                rc = RecommendationCandidate(
                    recommendation_id=rec.id,
                    employee_profile_id=emp.id,
                    role_requirement_id=role_id,
                    rank=0,
                    overall_score=0,
                    is_selected=False,
                    score_breakdown=json.dumps({}),
                    hard_constraint_pass=False,
                    rejection_reasons=json.dumps(reasons),
                    selection_reasons=json.dumps([]),
                    decay_adjusted_skills=json.dumps({}),
                    career_alignment_score=0,
                    workload_fairness_penalty=0,
                    topsis_closeness=0,
                )
                db.session.add(rc)

        # Audit log
        log = AuditLog(
            user_id=self.user_id,
            action='run_recommendation_engine',
            entity_type='recommendation',
            entity_id=rec.id,
            details=json.dumps({
                'project_id': self.project.id,
                'project_name': self.project.name,
                'roles_count': len(scored_per_role),
                'total_candidates_scored': sum(len(v) for v in scored_per_role.values()),
                'total_rejected': sum(len(v) for v in failed_per_role.values()),
                'confidence': monte_carlo.get('overall_confidence', 0),
                'synergy': synergy.get('synergy_score', 0),
            })
        )
        db.session.add(log)
        db.session.commit()

        return rec

    def _build_selection_reasons(self, candidate):
        """Build human-readable reasons why a candidate was selected."""
        reasons = []
        breakdown = candidate.get('score_breakdown', {})

        # Sort criteria by score descending
        sorted_criteria = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)

        for criterion, score in sorted_criteria[:4]:
            label = criterion.replace('_', ' ').title()
            pct = int(score * 100)
            if pct >= 80:
                reasons.append(f'Excellent {label} ({pct}%)')
            elif pct >= 60:
                reasons.append(f'Strong {label} ({pct}%)')
            elif pct >= 40:
                reasons.append(f'Adequate {label} ({pct}%)')

        if candidate.get('career_alignment_score', 0) >= 0.7:
            reasons.append('Role aligns with career goals')

        if candidate.get('fairness_penalty', 0) < 0.05:
            reasons.append('Good workload balance — not overallocated')

        return reasons

    def _serialize_pareto(self, alternatives):
        """Serialize pareto alternatives for JSON storage."""
        serialized = []
        for alt in alternatives:
            team_summary = {}
            for role_id, data in alt.get('team', {}).items():
                team_summary[str(role_id)] = {
                    'role': data['role'].role_title,
                    'filled': data['filled'],
                    'needed': data['needed'],
                    'selected': [
                        {'name': c['employee'].user.full_name, 'score': c['final_score']}
                        for c in data['selected']
                    ]
                }
            serialized.append({
                'label': alt['label'],
                'description': alt['description'],
                'avg_score': alt['avg_score'],
                'total_assigned': alt['total_assigned'],
                'team': team_summary
            })
        return serialized

    @staticmethod
    def get_recommendation_details(recommendation_id):
        """Load full recommendation details for display."""
        rec = Recommendation.query.get(recommendation_id)
        if not rec:
            return None

        candidates = RecommendationCandidate.query.filter_by(
            recommendation_id=rec.id
        ).all()

        # Group by role
        by_role = {}
        for c in candidates:
            role_id = c.role_requirement_id
            if role_id not in by_role:
                by_role[role_id] = {'passed': [], 'failed': []}
            if c.hard_constraint_pass:
                by_role[role_id]['passed'].append(c)
            else:
                by_role[role_id]['failed'].append(c)

        # Sort passed by rank
        for role_id in by_role:
            by_role[role_id]['passed'].sort(key=lambda x: x.rank)

        return {
            'recommendation': rec,
            'by_role': by_role,
            'pareto': json.loads(rec.pareto_alternatives) if rec.pareto_alternatives else [],
            'sensitivity': json.loads(rec.sensitivity_report) if rec.sensitivity_report else {},
            'skill_gaps': json.loads(rec.skill_gap_report) if rec.skill_gap_report else {},
            'parameters': json.loads(rec.parameters_snapshot) if rec.parameters_snapshot else {},
        }
