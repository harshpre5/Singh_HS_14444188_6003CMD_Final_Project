"""
SkillMatch Pro — Layers 10, 11, 12: Advanced Analysis
Layer 10: Pareto Optimal Alternatives
Layer 11: Sensitivity Analysis
Layer 12: Monte Carlo Confidence Scoring
"""
import math
import random
import copy
from app.services.scoring_engine import ScoringEngine
from app.services.team_builder import TeamBuilder


class AdvancedAnalysis:
    """Pareto alternatives, sensitivity analysis, and Monte Carlo confidence."""

    def __init__(self, project, role_requirements):
        self.project = project
        self.role_requirements = role_requirements

    # ==================== LAYER 10: PARETO OPTIMAL ====================

    def generate_pareto_alternatives(self, passed_per_role, base_team_result):
        """
        Generate 2-3 alternative teams with different optimisation targets:
        - Team A: Optimised for skill match (heaviest weight on skill_match)
        - Team B: Optimised for cost efficiency (heaviest weight on cost_efficiency)
        - Team C: Balanced (equal weights)
        Returns list of alternative team configurations with labels.
        """
        alternatives = []
        weight_profiles = [
            {
                'label': 'Skill-Optimised Team',
                'description': 'Prioritises the highest skill match and technical expertise',
                'icon': 'fa-code',
                'weights': {
                    'skill_match': 0.40, 'experience': 0.20, 'availability': 0.10,
                    'cost_efficiency': 0.05, 'project_success': 0.10,
                    'versatility': 0.05, 'career_alignment': 0.05,
                    'certification_relevance': 0.05
                }
            },
            {
                'label': 'Budget-Optimised Team',
                'description': 'Prioritises cost efficiency while maintaining quality',
                'icon': 'fa-pound-sign',
                'weights': {
                    'skill_match': 0.15, 'experience': 0.10, 'availability': 0.10,
                    'cost_efficiency': 0.35, 'project_success': 0.10,
                    'versatility': 0.05, 'career_alignment': 0.05,
                    'certification_relevance': 0.10
                }
            },
            {
                'label': 'Balanced Team',
                'description': 'Equal weight across all criteria for a well-rounded team',
                'icon': 'fa-balance-scale',
                'weights': {
                    'skill_match': 0.125, 'experience': 0.125, 'availability': 0.125,
                    'cost_efficiency': 0.125, 'project_success': 0.125,
                    'versatility': 0.125, 'career_alignment': 0.125,
                    'certification_relevance': 0.125
                }
            }
        ]

        for profile in weight_profiles:
            scored_per_role = {}
            for role in self.role_requirements:
                candidates = passed_per_role.get(role.id, [])
                if not candidates:
                    scored_per_role[role.id] = []
                    continue

                engine = ScoringEngine(role, self.project)
                engine.weights = profile['weights']
                scored = engine.score_candidates(candidates)
                scored_per_role[role.id] = scored

            builder = TeamBuilder(self.project)
            team_result = builder.assemble_team(scored_per_role)

            # Calculate aggregate score
            total_score = 0
            count = 0
            for role_id, data in team_result['team'].items():
                for c in data['selected']:
                    total_score += c['final_score']
                    count += 1

            alternatives.append({
                'label': profile['label'],
                'description': profile['description'],
                'icon': profile['icon'],
                'weights': profile['weights'],
                'team': team_result['team'],
                'avg_score': round(total_score / count, 4) if count > 0 else 0,
                'total_assigned': team_result['total_assigned'],
                'unassigned': team_result['unassigned_roles']
            })

        return alternatives

    # ==================== LAYER 11: SENSITIVITY ANALYSIS ====================

    def run_sensitivity_analysis(self, passed_per_role, base_weights):
        """
        Vary each weight by ±20% and check if the top-ranked candidate changes.
        Shows how robust the recommendation is.
        Returns: list of sensitivity results per criterion.
        """
        results = []
        criteria = list(base_weights.keys())

        for criterion in criteria:
            variations = []
            original_weight = base_weights[criterion]

            for delta in [-0.20, -0.10, 0.0, +0.10, +0.20]:
                modified_weights = dict(base_weights)
                modified_weights[criterion] = max(0, original_weight + delta)

                # Renormalise
                total = sum(modified_weights.values())
                if total > 0:
                    modified_weights = {k: v / total for k, v in modified_weights.items()}

                # Re-score for each role and get top candidate
                top_per_role = {}
                for role in self.role_requirements:
                    candidates = passed_per_role.get(role.id, [])
                    if not candidates:
                        continue
                    engine = ScoringEngine(role, self.project)
                    engine.weights = modified_weights
                    scored = engine.score_candidates(candidates)
                    if scored:
                        top = scored[0]
                        top_per_role[role.id] = {
                            'name': top['employee'].user.full_name,
                            'score': top['final_score'],
                            'id': top['employee'].id
                        }

                variations.append({
                    'delta': delta,
                    'weight_value': round(original_weight + delta, 3),
                    'top_candidates': top_per_role
                })

            # Check if top candidate changed across variations
            first_tops = variations[0]['top_candidates'] if variations else {}
            changed = False
            for v in variations:
                for role_id, top in v['top_candidates'].items():
                    if role_id in first_tops and top['id'] != first_tops[role_id]['id']:
                        changed = True
                        break

            results.append({
                'criterion': criterion,
                'original_weight': round(original_weight, 3),
                'ranking_changed': changed,
                'stability': 'Stable' if not changed else 'Sensitive',
                'variations': variations
            })

        # Overall stability score
        stable_count = sum(1 for r in results if not r['ranking_changed'])
        stability_score = round(stable_count / len(results), 4) if results else 1.0

        return {
            'criteria_results': results,
            'stability_score': stability_score,
            'stable_criteria': stable_count,
            'sensitive_criteria': len(results) - stable_count,
            'total_criteria': len(results)
        }

    # ==================== LAYER 12: MONTE CARLO ====================

    def run_monte_carlo(self, passed_per_role, base_weights, iterations=200):
        """
        Run scoring N times with small random perturbations to weights.
        If the same candidate stays #1 across most iterations, confidence is high.
        Returns: confidence score per role (0-1) and overall confidence.
        """
        random.seed(42)  # Reproducible
        criteria = list(base_weights.keys())
        role_tallies = {role.id: {} for role in self.role_requirements}

        for _ in range(iterations):
            # Perturb weights randomly (±15%)
            perturbed = {}
            for c in criteria:
                noise = random.uniform(-0.15, 0.15) * base_weights[c]
                perturbed[c] = max(0.01, base_weights[c] + noise)
            total = sum(perturbed.values())
            perturbed = {k: v / total for k, v in perturbed.items()}

            # Score each role
            for role in self.role_requirements:
                candidates = passed_per_role.get(role.id, [])
                if not candidates:
                    continue
                engine = ScoringEngine(role, self.project)
                engine.weights = perturbed
                scored = engine.score_candidates(candidates)
                if scored:
                    top_id = scored[0]['employee'].id
                    role_tallies[role.id][top_id] = role_tallies[role.id].get(top_id, 0) + 1

        # Calculate confidence per role
        role_confidence = {}
        for role in self.role_requirements:
            tallies = role_tallies.get(role.id, {})
            if not tallies:
                role_confidence[role.id] = {
                    'confidence': 0.0,
                    'top_candidate_consistency': 0,
                    'total_iterations': iterations
                }
                continue

            max_count = max(tallies.values())
            top_id = max(tallies, key=tallies.get)
            confidence = round(max_count / iterations, 4)

            # Find the employee name
            from app.models import EmployeeProfile
            emp = EmployeeProfile.query.get(top_id)
            name = emp.user.full_name if emp else f'ID:{top_id}'

            role_confidence[role.id] = {
                'confidence': confidence,
                'most_frequent_top': name,
                'most_frequent_count': max_count,
                'total_iterations': iterations,
                'runner_up_count': sorted(tallies.values(), reverse=True)[1] if len(tallies) > 1 else 0
            }

        # Overall confidence
        confidences = [v['confidence'] for v in role_confidence.values() if v['confidence'] > 0]
        overall = round(sum(confidences) / len(confidences), 4) if confidences else 0.0

        return {
            'overall_confidence': overall,
            'iterations': iterations,
            'role_confidence': role_confidence,
            'interpretation': self._interpret_confidence(overall)
        }

    def _interpret_confidence(self, score):
        if score >= 0.85:
            return 'Very High — Rankings are extremely stable across weight variations'
        elif score >= 0.65:
            return 'High — Rankings are mostly stable with minor variations'
        elif score >= 0.45:
            return 'Moderate — Some sensitivity to weight changes detected'
        elif score >= 0.25:
            return 'Low — Rankings change significantly with small weight adjustments'
        else:
            return 'Very Low — Highly sensitive to weight configuration'
