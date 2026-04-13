"""
SkillMatch Pro — Layers 2, 4, 5, 6: Scoring Engine
Layer 2: Skill Decay Adjustment
Layer 4: TOPSIS Multi-Criteria Scoring
Layer 5: Workload Fairness Penalty
Layer 6: Career Growth Alignment

Uses manager-defined weights from ScoringWeight table.
"""
import math
import json
from datetime import date
from app.models import (
    EmployeeProfile, EmployeeSkill, EmployeeCertification,
    Availability, ProjectHistory, Skill, ScoringWeight, Allocation
)


class ScoringEngine:
    """Scores candidates using TOPSIS with skill decay, fairness, and career alignment."""

    # Default weights if manager hasn't configured them
    DEFAULT_WEIGHTS = {
        'skill_match': 0.25,
        'experience': 0.15,
        'availability': 0.15,
        'cost_efficiency': 0.10,
        'project_success': 0.10,
        'versatility': 0.05,
        'career_alignment': 0.10,
        'certification_relevance': 0.10,
    }

    DECAY_HALF_LIFE_MONTHS = 24  # skill drops to 50% after 2 years of non-use

    def __init__(self, role_requirement, project):
        self.role_requirement = role_requirement
        self.project = project
        self.weights = self._load_weights()

    def _load_weights(self):
        """Load manager-defined weights from database."""
        db_weights = ScoringWeight.query.filter_by(
            role_requirement_id=self.role_requirement.id
        ).all()

        weights = dict(self.DEFAULT_WEIGHTS)
        for sw in db_weights:
            weights[sw.criterion] = sw.weight

        # Normalise so weights sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        return weights

    def score_candidates(self, passed_candidates, all_employees_count=None):
        """
        Score a list of (employee, constraint_details) tuples.
        Returns list of scored dicts sorted by final score descending.
        """
        if not passed_candidates:
            return []

        # Extract required skill names from constraints
        from app.models import RoleConstraint
        constraints = RoleConstraint.query.filter_by(
            role_requirement_id=self.role_requirement.id, is_active=True
        ).all()

        required_skills = []
        required_certs = []
        for c in constraints:
            if c.constraint_type in ('mandatory_skill', 'min_proficiency'):
                if c.parameter_name and c.parameter_name not in required_skills:
                    required_skills.append(c.parameter_name)
            if c.constraint_type == 'required_certification':
                if c.parameter_name:
                    required_certs.append(c.parameter_name)

        # Build raw score matrix
        raw_scores = []
        for emp, details in passed_candidates:
            scores = {
                'employee': emp,
                'skill_match': self._calc_skill_match(emp, required_skills),
                'experience': self._calc_experience_score(emp),
                'availability': self._calc_availability_score(emp),
                'cost_efficiency': self._calc_cost_efficiency(emp),
                'project_success': self._calc_project_success(emp),
                'versatility': self._calc_versatility(emp),
                'career_alignment': self._calc_career_alignment(emp),
                'certification_relevance': self._calc_certification_score(emp, required_certs),
                'decay_details': self._get_decay_details(emp, required_skills),
                'workload_fairness_penalty': self._calc_workload_fairness(emp),
            }
            raw_scores.append(scores)

        # Apply TOPSIS
        criteria = list(self.DEFAULT_WEIGHTS.keys())
        topsis_results = self._apply_topsis(raw_scores, criteria)

        return topsis_results

    # ==================== LAYER 2: SKILL DECAY ====================

    def _calc_skill_decay(self, last_used_date):
        """
        Exponential decay: score = e^(-lambda * months_since_used)
        Half-life = 24 months: lambda = ln(2) / 24
        """
        if not last_used_date:
            return 0.5  # Unknown, moderate penalty

        today = date.today()
        months_since = (today.year - last_used_date.year) * 12 + (today.month - last_used_date.month)
        months_since = max(0, months_since)

        decay_lambda = math.log(2) / self.DECAY_HALF_LIFE_MONTHS
        decay_factor = math.exp(-decay_lambda * months_since)
        return round(decay_factor, 4)

    def _get_decay_details(self, emp, required_skills):
        """Get decay-adjusted proficiency for each required skill."""
        details = {}
        for skill_name in required_skills:
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                continue
            es = EmployeeSkill.query.filter_by(
                employee_profile_id=emp.id, skill_id=skill.id
            ).first()
            if es:
                decay = self._calc_skill_decay(es.last_used_date)
                adjusted = round(es.proficiency * decay, 2)
                details[skill_name] = {
                    'raw_proficiency': es.proficiency,
                    'decay_factor': decay,
                    'adjusted_proficiency': adjusted,
                    'last_used': str(es.last_used_date) if es.last_used_date else None,
                    'years_used': es.years_used
                }
        return details

    # ==================== CRITERION CALCULATORS ====================

    def _calc_skill_match(self, emp, required_skills):
        """Layer 2 integrated: Skill match with decay adjustment. Score 0-1."""
        if not required_skills:
            return 0.5

        total_score = 0
        for skill_name in required_skills:
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                continue
            es = EmployeeSkill.query.filter_by(
                employee_profile_id=emp.id, skill_id=skill.id
            ).first()
            if es:
                decay = self._calc_skill_decay(es.last_used_date)
                adjusted = (es.proficiency / 10.0) * decay
                total_score += adjusted
            # If skill not found, contributes 0

        return round(total_score / len(required_skills), 4) if required_skills else 0

    def _calc_experience_score(self, emp):
        """Normalised experience. 15+ years = max score."""
        return round(min(emp.years_of_experience / 15.0, 1.0), 4)

    def _calc_availability_score(self, emp):
        """Score based on hours available and status."""
        avail = Availability.query.filter_by(employee_profile_id=emp.id).first()
        if not avail:
            return 0.8  # No data, assume mostly available

        status_scores = {
            'available': 1.0,
            'partially_busy': 0.6,
            'fully_busy': 0.1,
            'on_leave': 0.0
        }
        status_score = status_scores.get(avail.status, 0.5)
        hours_score = min(avail.hours_per_week_available / 40.0, 1.0)
        return round((status_score * 0.6 + hours_score * 0.4), 4)

    def _calc_cost_efficiency(self, emp):
        """Lower rate = higher score. Inverted normalisation against £200 cap."""
        if emp.hourly_rate <= 0:
            return 1.0
        return round(max(0, 1.0 - (emp.hourly_rate / 200.0)), 4)

    def _calc_project_success(self, emp):
        """Based on average project rating (1-5 scale)."""
        if emp.average_project_rating <= 0:
            return 0.5
        return round(emp.average_project_rating / 5.0, 4)

    def _calc_versatility(self, emp):
        """Number of skills / 15 (capped). More skills = more versatile."""
        skill_count = EmployeeSkill.query.filter_by(employee_profile_id=emp.id).count()
        return round(min(skill_count / 15.0, 1.0), 4)

    def _calc_career_alignment(self, emp):
        """
        Layer 6: Career Growth Alignment.
        Checks if role title appears in employee's career goal text.
        """
        if not emp.career_goal:
            return 0.3  # No goal set

        goal_lower = emp.career_goal.lower()
        role_title = self.role_requirement.role_title.lower()

        # Check for keyword overlap
        role_words = set(role_title.split())
        goal_words = set(goal_lower.split())
        common = role_words & goal_words
        # Remove common stop words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'for', 'in', 'to', 'of', 'with'}
        meaningful = common - stop_words

        if len(meaningful) >= 2:
            return 1.0
        elif len(meaningful) == 1:
            return 0.7

        # Also check for broader keyword matches
        career_keywords = ['lead', 'senior', 'architect', 'manager', 'engineer',
                          'developer', 'analyst', 'scientist', 'designer', 'security',
                          'frontend', 'backend', 'fullstack', 'data', 'cloud', 'devops',
                          'product', 'marketing', 'sales', 'finance']
        for kw in career_keywords:
            if kw in role_title and kw in goal_lower:
                return 0.8

        return 0.3

    def _calc_certification_score(self, emp, required_certs):
        """Score based on how many required certs the employee has."""
        if not required_certs:
            return 0.5  # Neutral if no certs required

        certs = EmployeeCertification.query.filter_by(employee_profile_id=emp.id).all()
        cert_names = [c.name.lower() for c in certs]

        matches = 0
        for req in required_certs:
            for cn in cert_names:
                if req.lower() in cn:
                    matches += 1
                    break

        return round(matches / len(required_certs), 4) if required_certs else 0.5

    # ==================== LAYER 5: WORKLOAD FAIRNESS ====================

    def _calc_workload_fairness(self, emp):
        """
        Penalty for overused employees. Based on:
        - Number of recent allocations
        - Current workload percentage
        Returns a penalty value 0-0.2 (subtracted from final score)
        """
        recent_allocs = Allocation.query.filter_by(
            employee_profile_id=emp.id
        ).filter(Allocation.status.in_(['allocated', 'active'])).count()

        alloc_penalty = min(recent_allocs * 0.03, 0.12)
        workload_penalty = (emp.current_workload / 100.0) * 0.08
        return round(alloc_penalty + workload_penalty, 4)

    # ==================== LAYER 4: TOPSIS ====================

    def _apply_topsis(self, raw_scores, criteria):
        """
        TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
        1. Build decision matrix
        2. Normalise
        3. Apply weights
        4. Find ideal best & worst
        5. Calculate distance to ideal
        6. Calculate closeness coefficient
        """
        n = len(raw_scores)
        if n == 0:
            return []

        m = len(criteria)

        # Step 1: Build decision matrix
        matrix = []
        for s in raw_scores:
            row = [s[c] for c in criteria]
            matrix.append(row)

        # Step 2: Normalise (vector normalisation)
        norm_matrix = []
        for j in range(m):
            col_sum_sq = sum(matrix[i][j] ** 2 for i in range(n))
            col_norm = math.sqrt(col_sum_sq) if col_sum_sq > 0 else 1
            for i in range(n):
                if len(norm_matrix) <= i:
                    norm_matrix.append([])
                norm_matrix[i].append(matrix[i][j] / col_norm)

        # Step 3: Weighted normalised matrix
        weight_list = [self.weights.get(c, 0.1) for c in criteria]
        weighted = []
        for i in range(n):
            row = [norm_matrix[i][j] * weight_list[j] for j in range(m)]
            weighted.append(row)

        # Step 4: Ideal best (max) and ideal worst (min) — all criteria are benefit
        ideal_best = [max(weighted[i][j] for i in range(n)) for j in range(m)]
        ideal_worst = [min(weighted[i][j] for i in range(n)) for j in range(m)]

        # Step 5: Distance to ideal best and worst
        results = []
        for i in range(n):
            d_best = math.sqrt(sum((weighted[i][j] - ideal_best[j]) ** 2 for j in range(m)))
            d_worst = math.sqrt(sum((weighted[i][j] - ideal_worst[j]) ** 2 for j in range(m)))

            # Step 6: Closeness coefficient
            closeness = d_worst / (d_best + d_worst) if (d_best + d_worst) > 0 else 0

            # Apply workload fairness penalty (Layer 5)
            penalty = raw_scores[i]['workload_fairness_penalty']
            adjusted_closeness = max(0, closeness - penalty)

            results.append({
                'employee': raw_scores[i]['employee'],
                'topsis_closeness': round(closeness, 4),
                'fairness_penalty': round(penalty, 4),
                'final_score': round(adjusted_closeness, 4),
                'score_breakdown': {c: round(raw_scores[i][c], 4) for c in criteria},
                'decay_details': raw_scores[i]['decay_details'],
                'career_alignment_score': round(raw_scores[i]['career_alignment'], 4),
            })

        # Sort by final score descending
        results.sort(key=lambda x: x['final_score'], reverse=True)

        # Add rank
        for idx, r in enumerate(results):
            r['rank'] = idx + 1

        return results
