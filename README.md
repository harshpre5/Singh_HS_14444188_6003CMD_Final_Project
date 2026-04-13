# SkillMatch Pro

## Full Feature List

### Authentication & Access
- Login / Register / Logout
- Manager approval required for new employees
- Role-based access control (Employee / Manager / Superuser)
- Pending approval page

### Employee Module (6 pages)
- Dashboard with profile completeness tracker
- Profile editor (department, title, experience, rate, bio, career goals)
- Skills manager (add/remove skills, proficiency 1-10, category filter)
- Availability & schedule (status, current project, reason, hours, dates)
- Certifications manager (add/remove with dates)
- **Recommendation Insights** — see every time you've been evaluated, your scores, selection/rejection reasons

### Manager Module (10 pages)
- Dashboard with pending approvals and project overview
- Project list and creation
- Project editor with role builder
- **Constraint configuration**  10 constraint types per role (mandatory skill, min proficiency, max workload, availability, certification, budget cap, location, etc.)
- **Weight configuration**  interactive sliders with live doughnut chart
- Employee browsing with detailed profiles
- **Full results page**  ranked candidates, Pareto alternatives, sensitivity, Monte Carlo, skill gaps, methodology panel
- **Candidate detail**  radar chart, score bars, skill decay table, selection/rejection reasons
- **LLM Comparison** page

### Superuser Module (7 pages)
- Executive dashboard with recent engine runs
- User management (activate/deactivate, change roles)
- Skills taxonomy viewer (all 500+ skills across 26 categories)
- **Rich analytics** — 6 charts (department, workload, top skills, experience, availability, location)
- Audit logs with pagination
- **All projects monitoring** across managers
- **LLM Comparison** methodology page

### 13-Layer Decision Engine
1. Hard Constraint Filter (10 constraint types)
2. Skill Decay Model (exponential, 24-month half-life)
3. Constraint Relaxation Suggestions
4. TOPSIS Multi-Criteria Scoring
5. Workload Fairness Penalty
6. Career Growth Alignment
7. Multi-Role Team Assembly (conflict-free)
8. Team Synergy Scoring (collaboration history)
9. Skill Gap Detection
10. Pareto Optimal Alternatives (3 teams)
11. Sensitivity Analysis (±20% weight variation)
12. Monte Carlo Confidence (200 iterations)
13. Full Explainability + Audit Logging

### Data
- 500+ skills across 26 categories
- 200+ job roles across 15 departments
- 150 seeded employees with full profiles
- CSV + JSON export for LLM comparison

---

## Setup from Scratch

```bash

cd skillmatch

# 2. Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
flask db init
flask db migrate -m "Initial"
flask db upgrade

# 5. Seed 150 employees + taxonomy
flask seed

# 6. Run
flask run
```

Open http://127.0.0.1:5000

## Test Logins

| Role | Email | Password |
|------|-------|----------|
| Employee | employee@skillmatch.com | password123 |
| Manager | manager@skillmatch.com | password123 |
| Superuser | superuser@skillmatch.com | password123 |

## Full Engine Test (Manager)

1. Login as manager
2. Projects → New Project → "Mobile App Rewrite"
3. Add roles: "Flutter Developer × 2", "Backend Developer × 2"
4. Click **Constraints** on each role → add:
   - Mandatory Skill: Flutter (or Python)
   - Min Proficiency: 5
   - Max Workload: 80%
   - Must Be Available
5. Click **Weights** → adjust sliders or keep defaults
6. Back to project → **Run 13-Layer Recommendation Engine**
7. Explore: ranked candidates, Pareto teams, sensitivity, Monte Carlo confidence
8. Click any candidate → full explainability with radar chart + decay analysis

## File Structure (63 files)

```
skillmatch/
├── run.py
├── requirements.txt
├── .env
├── .gitignore
├── app/
│   ├── __init__.py (app factory)
│   ├── config.py
│   ├── extensions.py
│   ├── models/ (6 files - user, employee, skill, project, recommendation, audit)
│   ├── routes/ (6 files - auth, employee, manager, superuser, recommendation, init)
│   ├── services/ (6 files - constraint, scoring, team_builder, topsis, explainability, init)
│   ├── utils/ (4 files - helpers, constants, seed_data, init)
│   ├── static/css/main.css
│   ├── static/js/main.js
│   └── templates/
│       ├── base.html
│       ├── landing.html
│       ├── auth/ (3 - login, register, pending)
│       ├── employee/ (6 - dashboard, profile, skills, availability, certifications, insights)
│       ├── manager/ (10 - dashboard, projects, create, edit, constraints, weights, employees, view_employee, results, candidate_detail)
│       ├── superuser/ (7 - dashboard, users, skills, analytics, audit, projects, comparison)
│       └── shared/ (3 - 403, 404, 500)
└── exports/ (generated after seeding)
```







