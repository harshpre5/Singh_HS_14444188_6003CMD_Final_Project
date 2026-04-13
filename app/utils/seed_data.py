"""
SkillMatch Pro — Seed Data Generator
Creates: skill taxonomy, job roles, 3 test users, 150 realistic employees
Exports: CSV + JSON for LLM comparison testing
"""
import json
import csv
import os
import random
from datetime import datetime, timedelta, date
from faker import Faker
from app.extensions import db
from app.models import (
    User, EmployeeProfile, EmployeeSkill, EmployeeCertification,
    Availability, ProjectHistory, SkillCategory, Skill, JobRole, AuditLog
)
from app.utils.constants import SKILL_TAXONOMY, JOB_ROLES, CERTIFICATIONS, DEPARTMENTS, LOCATIONS

fake = Faker('en_GB')
Faker.seed(42)
random.seed(42)

AVATAR_COLORS = [
    '#6366F1', '#8B5CF6', '#EC4899', '#EF4444', '#F97316',
    '#EAB308', '#22C55E', '#14B8A6', '#06B6D4', '#3B82F6',
    '#A855F7', '#F43F5E', '#10B981', '#0EA5E9', '#D946EF'
]

CAREER_GOALS = [
    "Transition into a technical lead role within the next 2 years",
    "Develop expertise in cloud architecture and distributed systems",
    "Move into product management combining technical and business skills",
    "Become a specialist in machine learning and AI engineering",
    "Grow into a senior engineering manager leading multiple teams",
    "Deepen data engineering skills and work on large-scale data platforms",
    "Transition from backend to full-stack development",
    "Build expertise in cybersecurity and become a security architect",
    "Develop design leadership skills and lead a design team",
    "Move into a solutions architect role working with enterprise clients",
    "Specialise in DevOps and platform engineering",
    "Grow into a VP of Engineering role in the next 5 years",
    "Focus on mentoring junior developers and building engineering culture",
    "Transition into a data science role from analytics background",
    "Build a strong foundation in frontend technologies and UI/UX",
    "Become an expert in financial technology and payment systems",
    "Develop cross-functional skills spanning marketing and analytics",
    "Move into strategy consulting leveraging technical background",
    "Specialise in healthcare technology and digital health",
    "Focus on sustainability and green technology initiatives"
]

PROJECT_NAMES = [
    "Customer Portal Redesign", "Payment Gateway Integration", "Mobile App v3.0",
    "Data Lake Migration", "CRM System Overhaul", "AI Chatbot Development",
    "Cloud Infrastructure Migration", "E-Commerce Platform Build",
    "HR Analytics Dashboard", "Security Audit & Remediation",
    "Inventory Management System", "Marketing Automation Platform",
    "API Gateway Modernisation", "Employee Onboarding Portal",
    "Real-Time Analytics Engine", "Supply Chain Optimisation",
    "Document Management System", "Customer 360 Platform",
    "Microservices Migration", "DevOps Pipeline Automation",
    "Financial Reporting Platform", "IoT Sensor Dashboard",
    "Content Management System", "Compliance Tracking Tool",
    "Machine Learning Pipeline", "Performance Monitoring System",
    "Vendor Portal Development", "Digital Signature Platform",
    "Knowledge Base System", "Automated Testing Framework"
]


def generate_professional_bio(job_title, department, years_of_experience, skill_names):
    """Generate a realistic English professional bio for seeded employees."""
    cleaned_skills = [skill for skill in (skill_names or []) if skill]

    fallback_skills = [
        "problem solving",
        "cross-functional collaboration",
        "delivery excellence"
    ]

    for skill in fallback_skills:
        if len(cleaned_skills) >= 3:
            break
        if skill not in cleaned_skills:
            cleaned_skills.append(skill)

    skill1, skill2, skill3 = cleaned_skills[:3]
    yoe = max(1, int(round(years_of_experience or 1)))

    templates = [
        "{job_title} in {department} with {yoe}+ years of experience. Strong background in {skill1}, {skill2}, and {skill3}. Focused on delivering reliable, high-quality outcomes in cross-functional teams.",
        "Experienced {job_title} working in {department}. Brings {yoe}+ years of industry experience with strengths in {skill1}, {skill2}, and {skill3}. Known for a practical, collaborative, and results-driven approach.",
        "{job_title} specialising in {department} work, with {yoe}+ years of experience across business-critical projects. Core strengths include {skill1}, {skill2}, and {skill3}, with a strong focus on quality, teamwork, and execution."
    ]

    return random.choice(templates).format(
        job_title=job_title or "Professional",
        department=department or "general operations",
        yoe=yoe,
        skill1=skill1,
        skill2=skill2,
        skill3=skill3
    )


def seed_skills():
    """Seed all skill categories and skills from taxonomy."""
    print("  Seeding skills taxonomy...")
    icon_map = {
        "Programming Languages": "fa-code",
        "Web Frontend": "fa-window-maximize",
        "Web Backend": "fa-server",
        "Mobile Development": "fa-mobile-alt",
        "Databases": "fa-database",
        "Cloud & Infrastructure": "fa-cloud",
        "Data Science & Analytics": "fa-chart-bar",
        "Machine Learning & AI": "fa-brain",
        "Cybersecurity": "fa-shield-alt",
        "DevOps & SRE": "fa-cogs",
        "UI/UX Design": "fa-palette",
        "Graphic Design & Multimedia": "fa-paint-brush",
        "Project Management": "fa-tasks",
        "Marketing": "fa-bullhorn",
        "Sales": "fa-handshake",
        "Finance & Accounting": "fa-pound-sign",
        "Human Resources": "fa-users",
        "Legal": "fa-gavel",
        "Operations & Supply Chain": "fa-truck",
        "Customer Support & Success": "fa-headset",
        "Business Analysis": "fa-search-dollar",
        "Communication & Soft Skills": "fa-comments",
        "Industry-Specific": "fa-industry",
        "Testing & QA": "fa-bug",
        "Data Engineering": "fa-stream",
        "Emerging Technologies": "fa-rocket"
    }

    skill_objects = {}
    for cat_name, skill_list in SKILL_TAXONOMY.items():
        cat = SkillCategory(
            name=cat_name,
            description=f"Skills related to {cat_name.lower()}",
            icon=icon_map.get(cat_name, "fa-star")
        )
        db.session.add(cat)
        db.session.flush()

        for skill_name in skill_list:
            skill = Skill(name=skill_name, category_id=cat.id)
            db.session.add(skill)
            db.session.flush()
            skill_objects[skill_name] = skill

    db.session.commit()
    print(f"    → {len(skill_objects)} skills across {len(SKILL_TAXONOMY)} categories")
    return skill_objects


def seed_job_roles():
    """Seed all job roles safely without crashing on duplicate titles."""
    print("  Seeding job roles...")
    count = 0
    skipped = 0
    seen_titles = set()

    for dept, roles in JOB_ROLES.items():
        for title in roles:
            clean_title = title.strip()

            if clean_title in seen_titles:
                skipped += 1
                print(f"    → Skipping duplicate job role title: {clean_title}")
                continue

            seen_titles.add(clean_title)

            jr = JobRole(title=clean_title, department=dept)
            db.session.add(jr)
            count += 1

    db.session.commit()
    print(f"    → {count} unique job roles across {len(JOB_ROLES)} departments")
    if skipped:
        print(f"    → Skipped {skipped} duplicate role title(s)")


def seed_test_users():
    """Create the 3 core test users."""
    print("  Seeding test users...")
    users = [
        {"email": "employee@skillmatch.com", "first_name": "Alex", "last_name": "Thompson",
         "role": "employee", "is_approved": True},
        {"email": "manager@skillmatch.com", "first_name": "Sarah", "last_name": "Mitchell",
         "role": "manager", "is_approved": True},
        {"email": "superuser@skillmatch.com", "first_name": "James", "last_name": "Anderson",
         "role": "superuser", "is_approved": True},
    ]
    for u in users:
        user = User(
            email=u['email'], first_name=u['first_name'], last_name=u['last_name'],
            role=u['role'], is_approved=u['is_approved'],
            avatar_color=random.choice(AVATAR_COLORS)
        )
        user.set_password('password123')
        db.session.add(user)
    db.session.commit()
    print("    → 3 test users created")


def _pick_skills_for_department(dept, all_skills):
    """Return a weighted random set of skills relevant to a department."""
    dept_skill_map = {
        "Engineering": ["Programming Languages", "Web Frontend", "Web Backend", "Databases",
                        "Cloud & Infrastructure", "DevOps & SRE", "Testing & QA"],
        "Data Science": ["Programming Languages", "Data Science & Analytics", "Machine Learning & AI",
                         "Data Engineering", "Databases"],
        "Product": ["Project Management", "Business Analysis", "Communication & Soft Skills",
                    "Data Science & Analytics"],
        "Design": ["UI/UX Design", "Graphic Design & Multimedia", "Web Frontend"],
        "Marketing": ["Marketing", "Data Science & Analytics", "Communication & Soft Skills"],
        "Sales": ["Sales", "Communication & Soft Skills", "Marketing"],
        "Finance": ["Finance & Accounting", "Data Science & Analytics", "Business Analysis"],
        "Human Resources": ["Human Resources", "Communication & Soft Skills", "Business Analysis"],
        "Operations": ["Operations & Supply Chain", "Project Management", "Business Analysis"],
        "Legal": ["Legal", "Communication & Soft Skills"],
        "Customer Support": ["Customer Support & Success", "Communication & Soft Skills"],
        "IT & Infrastructure": ["Cloud & Infrastructure", "Cybersecurity", "DevOps & SRE", "Databases"],
        "Research & Development": ["Machine Learning & AI", "Programming Languages", "Emerging Technologies"],
        "Quality Assurance": ["Testing & QA", "Programming Languages", "DevOps & SRE"],
        "Business Development": ["Sales", "Marketing", "Communication & Soft Skills", "Business Analysis"],
        "Content & Communications": ["Communication & Soft Skills", "Marketing", "Graphic Design & Multimedia"],
        "Strategy & Consulting": ["Business Analysis", "Communication & Soft Skills", "Finance & Accounting"],
        "Compliance & Risk": ["Legal", "Cybersecurity", "Finance & Accounting"],
        "Administration": ["Communication & Soft Skills", "Project Management", "Human Resources"]
    }

    primary_cats = dept_skill_map.get(dept, ["Communication & Soft Skills"])
    secondary_cats = [c for c in SKILL_TAXONOMY.keys() if c not in primary_cats]

    chosen = []
    for cat in primary_cats:
        pool = SKILL_TAXONOMY.get(cat, [])
        chosen.extend(random.sample(pool, min(random.randint(1, 3), len(pool))))

    for cat in random.sample(secondary_cats, min(2, len(secondary_cats))):
        pool = SKILL_TAXONOMY.get(cat, [])
        if pool:
            chosen.append(random.choice(pool))

    chosen = list(set(chosen))[:random.randint(5, 12)]
    return chosen


def seed_employees(skill_objects, count=150):
    """Generate 150 realistic fake employees."""
    print(f"  Seeding {count} employees...")

    all_job_titles = []
    for roles in JOB_ROLES.values():
        all_job_titles.extend(roles)

    employees_data = []

    for i in range(count):
        dept = random.choice(DEPARTMENTS)
        dept_roles = JOB_ROLES.get(dept, all_job_titles)
        job_title = random.choice(dept_roles) if dept_roles else random.choice(all_job_titles)

        first = fake.first_name()
        last = fake.last_name()
        email = f"{first.lower()}.{last.lower()}{random.randint(1,99)}@skillmatch.com"

        user = User(
            email=email, first_name=first, last_name=last,
            role='employee', is_approved=True,
            avatar_color=random.choice(AVATAR_COLORS)
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()

        yoe = round(random.uniform(0.5, 25), 1)
        workload = random.choice([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        rate = round(random.uniform(25, 200), 2)

        chosen_skills = _pick_skills_for_department(dept, skill_objects)
        generated_bio = generate_professional_bio(job_title, dept, yoe, chosen_skills)

        profile = EmployeeProfile(
            user_id=user.id,
            department=dept,
            job_title=job_title,
            years_of_experience=yoe,
            hourly_rate=rate,
            current_workload=workload,
            max_workload=100,
            bio=generated_bio,
            phone=fake.phone_number(),
            location=random.choice(LOCATIONS),
            career_goal=random.choice(CAREER_GOALS),
            total_projects_completed=random.randint(0, 30),
            average_project_rating=round(random.uniform(2.5, 5.0), 1)
        )
        db.session.add(profile)
        db.session.flush()

        emp_skill_data = []
        for idx, skill_name in enumerate(chosen_skills):
            skill_obj = skill_objects.get(skill_name)
            if not skill_obj:
                continue

            prof = random.randint(1, 10)
            years_used = round(min(random.uniform(0.5, 15), yoe), 1)
            months_ago = random.randint(0, 36)
            last_used = date.today() - timedelta(days=months_ago * 30)

            es = EmployeeSkill(
                employee_profile_id=profile.id,
                skill_id=skill_obj.id,
                proficiency=prof,
                years_used=years_used,
                last_used_date=last_used,
                is_primary=(idx < 3)
            )
            db.session.add(es)
            emp_skill_data.append({
                "skill": skill_name,
                "proficiency": prof,
                "years_used": years_used,
                "last_used": str(last_used)
            })

        emp_cert_data = []
        if random.random() < 0.3:
            for cert_name in random.sample(CERTIFICATIONS, random.randint(1, 3)):
                d_obtained = fake.date_between(start_date='-5y', end_date='today')
                cert = EmployeeCertification(
                    employee_profile_id=profile.id,
                    name=cert_name,
                    issuing_body=cert_name.split('(')[0].strip().split(' ')[0],
                    date_obtained=d_obtained,
                    expiry_date=d_obtained + timedelta(days=random.choice([365, 730, 1095]))
                )
                db.session.add(cert)
                emp_cert_data.append(cert_name)

        statuses = ['available', 'partially_busy', 'fully_busy', 'on_leave']
        weights = [0.3, 0.35, 0.25, 0.1]
        status = random.choices(statuses, weights=weights, k=1)[0]

        hrs = (
            40 if status == 'available'
            else random.choice([5, 10, 15, 20, 25, 30, 35]) if status == 'partially_busy'
            else 0
        )

        avail_from = date.today() + timedelta(days=random.randint(0, 90)) if status != 'available' else date.today()
        reason = ""
        current_proj = ""

        if status in ['partially_busy', 'fully_busy']:
            current_proj = random.choice(PROJECT_NAMES)
            reason = f"Currently working on {current_proj}"
        elif status == 'on_leave':
            reason = random.choice(["Annual leave", "Parental leave", "Sabbatical", "Medical leave"])

        avail = Availability(
            employee_profile_id=profile.id,
            status=status,
            reason=reason,
            current_project_name=current_proj,
            hours_per_week_available=hrs,
            available_from=avail_from,
            notes=""
        )
        db.session.add(avail)

        for _ in range(random.randint(1, 5)):
            start_d = fake.date_between(start_date='-4y', end_date='-3m')
            end_d = start_d + timedelta(days=random.randint(30, 365))

            collab_pool = list(range(1, i + 1))
            collab_count = min(random.randint(1, 4), len(collab_pool))
            collaborators = random.sample(collab_pool, collab_count) if collab_pool else []

            ph = ProjectHistory(
                employee_profile_id=profile.id,
                project_name=random.choice(PROJECT_NAMES),
                role_in_project=job_title,
                description=fake.sentence(),
                start_date=start_d,
                end_date=end_d,
                rating=round(random.uniform(2.5, 5.0), 1),
                collaborated_with=json.dumps(collaborators),
                skills_used=json.dumps([s['skill'] for s in emp_skill_data[:3]])
            )
            db.session.add(ph)

        employees_data.append({
            "id": user.id,
            "name": f"{first} {last}",
            "email": email,
            "department": dept,
            "job_title": job_title,
            "years_of_experience": yoe,
            "hourly_rate": rate,
            "current_workload": workload,
            "location": profile.location,
            "career_goal": profile.career_goal,
            "total_projects_completed": profile.total_projects_completed,
            "average_project_rating": profile.average_project_rating,
            "skills": emp_skill_data,
            "certifications": emp_cert_data,
            "availability_status": status,
            "hours_per_week_available": hrs,
            "available_from": str(avail_from),
            "current_project": current_proj
        })

        if (i + 1) % 25 == 0:
            db.session.commit()
            print(f"    → {i + 1}/{count} employees created")

    db.session.commit()
    print(f"    → All {count} employees created")
    return employees_data


def export_dataset(employees_data):
    """Export the employee dataset as CSV and JSON for LLM comparison."""
    export_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'exports'
    )
    os.makedirs(export_dir, exist_ok=True)

    json_path = os.path.join(export_dir, 'employees_dataset.json')
    with open(json_path, 'w') as f:
        json.dump(employees_data, f, indent=2, default=str)
    print(f"    → JSON exported to {json_path}")

    csv_path = os.path.join(export_dir, 'employees_dataset.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'name', 'email', 'department', 'job_title',
            'years_of_experience', 'hourly_rate', 'current_workload',
            'location', 'career_goal', 'total_projects_completed',
            'average_project_rating', 'skills', 'certifications',
            'availability_status', 'hours_per_week_available',
            'available_from', 'current_project'
        ])

        for emp in employees_data:
            skills_str = "; ".join([
                f"{s['skill']}(lvl:{s['proficiency']},yrs:{s['years_used']},last:{s['last_used']})"
                for s in emp['skills']
            ])
            certs_str = "; ".join(emp['certifications'])

            writer.writerow([
                emp['id'], emp['name'], emp['email'], emp['department'],
                emp['job_title'], emp['years_of_experience'], emp['hourly_rate'],
                emp['current_workload'], emp['location'], emp['career_goal'],
                emp['total_projects_completed'], emp['average_project_rating'],
                skills_str, certs_str, emp['availability_status'],
                emp['hours_per_week_available'], emp['available_from'],
                emp['current_project']
            ])

    print(f"    → CSV exported to {csv_path}")


def seed_all():
    """Main seed function — run everything."""
    print("\n🌱 SkillMatch Pro — Seeding Database")
    print("=" * 50)

    print("  Clearing existing data...")
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

    skill_objects = seed_skills()
    seed_job_roles()
    seed_test_users()
    employees_data = seed_employees(skill_objects, count=150)
    export_dataset(employees_data)

    log = AuditLog(
        action='database_seeded',
        entity_type='system',
        details=json.dumps({"employees": 150, "timestamp": str(datetime.utcnow())})
    )
    db.session.add(log)
    db.session.commit()

    print("=" * 50)
    print("✅ Database seeded successfully!")
    print(f"   • Skills: {Skill.query.count()}")
    print(f"   • Job Roles: {JobRole.query.count()}")
    print(f"   • Users: {User.query.count()}")
    print(f"   • Employee Profiles: {EmployeeProfile.query.count()}")
    print(f"   • Dataset exported to /exports/")
    print()