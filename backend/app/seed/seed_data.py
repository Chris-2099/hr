"""Generates a complete, internally-consistent fake dataset shaped like what
a real Jobvite + Dayforce sync would produce, per the HR Workforce & Org
Health Dashboard charter. Run with:

    python -m app.seed.seed_data

This DROPS and recreates all tables, so re-running gives a fresh, reproducible
(random.seed-pinned) dataset. The resulting hr_dashboard.db is the entire
deliverable for this phase - there is nothing else to configure to see the
dashboards working.
"""

from __future__ import annotations

import datetime as dt
import random

from faker import Faker

from app import models
from app.auth import hash_password
from app.database import Base, SessionLocal, engine

random.seed(42)
fake = Faker()
Faker.seed(42)

TODAY = dt.date.today()
YEARS_OF_HISTORY = 6

GENDERS = ["Male", "Female", "Decline to Self Identify"]
GENDER_WEIGHTS = [0.47, 0.49, 0.04]
RACE_ETHNICITIES = [
    "White",
    "Black or African American",
    "Hispanic or Latino",
    "Asian",
    "Two Or More Races",
    "American Indian",
    "Hawaiian Or Pacific Islander",
]
RACE_WEIGHTS = [0.52, 0.12, 0.14, 0.14, 0.05, 0.015, 0.015]

DEPARTMENTS = [
    # id, name, division
    ("EXEC", "Executive Leadership", "Executive"),
    ("ENG", "Engineering", "Technology"),
    ("DATA", "Data & Analytics", "Technology"),
    ("PROD", "Product Management", "Product"),
    ("DESIGN", "Design", "Product"),
    ("SALES-ENT", "Sales - Enterprise", "Sales"),
    ("SALES-SMB", "Sales - SMB", "Sales"),
    ("CS", "Customer Success", "Customer Success"),
    ("MKT", "Marketing", "Marketing"),
    ("FIN", "Finance", "Finance"),
    ("HR", "People & Culture", "People & Culture"),
    ("ITOPS", "IT Operations", "Operations"),
    ("LEGAL", "Legal", "Operations"),
]

TARGET_HEADCOUNT = {
    "ENG": 55,
    "DATA": 20,
    "PROD": 18,
    "DESIGN": 14,
    "SALES-ENT": 25,
    "SALES-SMB": 20,
    "CS": 28,
    "MKT": 16,
    "FIN": 16,
    "HR": 14,
    "ITOPS": 14,
    "LEGAL": 8,
}

LOCATIONS = [
    ("HQ-LAS", "Las Vegas HQ", "Las Vegas", "NV", "United States", "West", "Onsite"),
    ("AUS", "Austin Office", "Austin", "TX", "United States", "South", "Onsite"),
    ("CHI", "Chicago Office", "Chicago", "IL", "United States", "Midwest", "Hybrid"),
    ("NYC", "New York Office", "New York", "NY", "United States", "Northeast", "Hybrid"),
    ("SF", "San Francisco Office", "San Francisco", "CA", "United States", "West", "Hybrid"),
    ("REMOTE-US", "US Remote", "Remote", None, "United States", "Remote", "Remote"),
    ("TOR", "Toronto Office", "Toronto", "ON", "Canada", "International", "Onsite"),
    ("LON", "London Office", "London", None, "United Kingdom", "International", "Onsite"),
]
LOCATION_WEIGHTS = [0.32, 0.14, 0.08, 0.1, 0.1, 0.16, 0.06, 0.04]

LEVEL_LADDER = [
    # level, title_suffix, is_leadership, is_critical, pyramid_pct
    (1, "Associate", False, False, 0.28),
    (2, "Specialist", False, False, 0.30),
    (3, "Senior Specialist", False, False, 0.22),
    (4, "Manager", True, False, 0.12),
    (5, "Director", True, True, 0.06),
    (6, "VP", True, True, 0.02),
]

EEO_BY_LEVEL = {
    1: "Office",
    2: "Professionals",
    3: "Professionals",
    4: "FirstLevelManagers",
    5: "Officials",
    6: "Officials",
    7: "Officials",
}

SALARY_RANGE_BY_LEVEL = {
    1: (52000, 72000),
    2: (68000, 95000),
    3: (92000, 128000),
    4: (118000, 158000),
    5: (152000, 205000),
    6: (195000, 270000),
    7: (260000, 380000),
}

TERMINATION_REASONS_VOL = ["Better Opportunity", "Relocation", "Compensation", "Career Change", "Return to School"]
TERMINATION_REASONS_INVOL = ["Performance", "Restructuring", "Policy Violation", "Role Elimination"]

ER_CASE_TYPES = ["Harassment Complaint", "Policy Violation", "Conflict Resolution", "Accommodation Request", "Compensation Dispute"]
ER_SEVERITY = ["Low", "Medium", "High"]
ER_SEVERITY_WEIGHTS = [0.55, 0.33, 0.12]

CANDIDATE_SOURCES = [
    ("Indeed", "Jobboard"),
    ("LinkedIn", "Jobboard"),
    ("Company Career Site", "Career Site"),
    ("Employee Referral", "Referral"),
    ("Randstad Agency", "Agency"),
    ("ZipRecruiter", "Jobboard"),
]

TRAINING_COURSES = [
    ("Code of Conduct & Ethics", True),
    ("Information Security Awareness", True),
    ("Workplace Harassment Prevention", True),
    ("Managing as One", False),
    ("Leadership Essentials", False),
    ("Inclusive Hiring Practices", False),
]

INTERVIEW_STAGES = ["Phone Screen", "Panel", "Technical", "Final"]
RECOMMENDATIONS = ["Strong Yes", "Yes", "Neutral", "No", "Strong No"]
RECOMMENDATION_WEIGHTS = [0.2, 0.35, 0.2, 0.15, 0.1]

CANDIDATE_TITLES = [
    "Software Engineer", "Account Executive", "Customer Success Manager", "Product Manager",
    "Data Analyst", "Marketing Specialist", "Financial Analyst", "Recruiter", "UX Designer",
    "Operations Coordinator", "Sales Development Representative", "HR Generalist",
]
CANDIDATE_WORK_STATUSES = ["US Citizen", "Permanent Resident", "H1 Visa", "TN Visa", "F1 Visa", "None"]
CANDIDATE_WORK_STATUS_WEIGHTS = [0.74, 0.1, 0.08, 0.02, 0.03, 0.03]
CANDIDATE_VETERAN_STATUSES = ["Not a Veteran", "Veteran", "Disabled Veteran", "Decline to Self Identify"]
CANDIDATE_VETERAN_STATUS_WEIGHTS = [0.78, 0.1, 0.03, 0.09]

# Jobvite's workflowStateEId is a stable id that outlives the display-name
# relabeling workflow_state is subject to - fake but fixed per state name.
WORKFLOW_STATE_EIDS = {
    name: f"wf{idx:03d}"
    for idx, name in enumerate(
        ["New", "Screening", "Interview", "Offer", "Hired", "Rejected", "Withdrawn"]
    )
}


def rand_date(start: dt.date, end: dt.date) -> dt.date:
    if end <= start:
        return start
    return start + dt.timedelta(days=random.randint(0, (end - start).days))


def weighted_gender() -> str:
    return random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]


def weighted_race() -> str:
    return random.choices(RACE_ETHNICITIES, weights=RACE_WEIGHTS)[0]


def weighted_location() -> str:
    return random.choices([l[0] for l in LOCATIONS], weights=LOCATION_WEIGHTS)[0]


def salary_for_level(level: int) -> tuple[float, float]:
    lo, hi = SALARY_RANGE_BY_LEVEL.get(level, (60000, 90000))
    salary = round(random.uniform(lo, hi), -2)
    midpoint = (lo + hi) / 2
    compa_ratio = round(salary / midpoint, 2)
    return salary, compa_ratio


class IdCounter:
    def __init__(self):
        self.counters: dict[str, int] = {}

    def next(self, prefix: str) -> str:
        self.counters[prefix] = self.counters.get(prefix, 0) + 1
        return f"{prefix}{self.counters[prefix]:05d}"


ids = IdCounter()


def seed():
    print("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _seed_roles(db)
        departments = _seed_departments(db)
        locations = _seed_locations(db)
        positions = _seed_positions(db, departments)
        employees = _seed_employees(db, departments, positions)
        _seed_compensation(db, employees)
        _seed_performance(db, employees)
        _seed_pto(db, employees)
        _seed_er_cases(db, departments)
        _seed_engagement(db, departments, employees)
        _seed_succession(db, positions, employees)
        _seed_training(db, employees)
        _seed_workforce_plans(db, departments, employees)
        requisitions = _seed_requisitions(db, departments, locations, employees, positions)
        candidates = _seed_candidates(db)
        _seed_applications_and_interviews(db, requisitions, candidates, employees)
        _seed_users(db, departments, employees)
        _seed_ingestion_log(db)
        db.commit()
        print("Seed complete.")
        print(f"  departments={len(departments)} locations={len(locations)} positions={len(positions)}")
        print(f"  employees={len(employees)} requisitions={len(requisitions)} candidates={len(candidates)}")
    finally:
        db.close()


def _seed_roles(db) -> dict[str, models.Role]:
    role_defs = [
        (models.ROLE_ADMIN, "Full access, user management"),
        (models.ROLE_EXECUTIVE, "Read access to all dashboards and departments"),
        (models.ROLE_HRBP, "Read access scoped to assigned departments"),
        (models.ROLE_RECRUITER, "Read access to talent acquisition data only"),
        (models.ROLE_VIEWER, "Read-only access, no compensation data"),
    ]
    roles = {}
    for name, desc in role_defs:
        r = models.Role(name=name, description=desc)
        db.add(r)
        roles[name] = r
    db.flush()
    return roles


def _seed_departments(db) -> dict[str, models.Department]:
    out = {}
    for dept_id, name, division in DEPARTMENTS:
        d = models.Department(
            department_id=dept_id,
            dayforce_xref_code=f"ORGUNIT-{dept_id}",
            name=name,
            division=division,
            active=True,
        )
        db.add(d)
        out[dept_id] = d
    db.flush()
    return out


def _seed_locations(db) -> dict[str, models.Location]:
    out = {}
    for loc_id, name, city, state, country, region, remote_type in LOCATIONS:
        l = models.Location(
            location_id=loc_id,
            dayforce_xref_code=f"LOC-{loc_id}",
            name=name, city=city, state=state, country=country,
            region=region, remote_type=remote_type,
        )
        db.add(l)
        out[loc_id] = l
    db.flush()
    return out


def _seed_positions(db, departments) -> dict[str, dict[int, models.Position]]:
    """Returns {department_id: {level: Position}}"""
    out: dict[str, dict[int, models.Position]] = {}
    for dept_id, name, _division in DEPARTMENTS:
        out[dept_id] = {}
        max_level = 7 if dept_id == "EXEC" else 6
        for level, suffix, is_leadership, is_critical, _pct in LEVEL_LADDER:
            if level > max_level:
                continue
            title = f"VP, {name}" if level == 6 else f"{name} {suffix}"
            pos_id = ids.next("POS")
            p = models.Position(
                position_id=pos_id,
                dayforce_xref_code=f"JOB-{pos_id}",
                title=title,
                department_id=dept_id,
                job_family=name,
                job_level=level,
                is_critical=is_critical,
                is_leadership=is_leadership,
                pay_grade=f"P{level}",
                status="Active",
            )
            db.add(p)
            out[dept_id][level] = p
        if dept_id == "EXEC":
            pos_id = ids.next("POS")
            p = models.Position(
                position_id=pos_id,
                dayforce_xref_code=f"JOB-{pos_id}",
                title="Chief Executive Officer", department_id="EXEC",
                job_family="Executive Leadership", job_level=7, is_critical=True, is_leadership=True,
                pay_grade="P7", status="Active",
            )
            db.add(p)
            out["EXEC"][7] = p
    db.flush()
    return out


def _make_employee(dept_id, position, location_id, hire_date, manager_id=None) -> models.Employee:
    emp_id = ids.next("EMP")
    first = fake.first_name()
    last = fake.last_name()
    salary, _ = salary_for_level(position.job_level)
    e = models.Employee(
        employee_id=emp_id,
        dayforce_employee_id=f"DF-{emp_id}",
        first_name=first,
        last_name=last,
        email=f"{first.lower()}.{last.lower()}@company.example",
        gender=weighted_gender(),
        race_ethnicity=weighted_race(),
        birth_date=fake.date_of_birth(minimum_age=23, maximum_age=62),
        hire_date=hire_date,
        employment_status="Active",
        employee_type=random.choices(["FTE", "Part-Time", "Contractor"], weights=[0.88, 0.05, 0.07])[0],
        fte_percent=1.0,
        department_id=dept_id,
        position_id=position.position_id,
        location_id=location_id,
        manager_employee_id=manager_id,
        remote_type=random.choice(["Onsite", "Hybrid", "Remote"]) if location_id == "REMOTE-US" else
        {"Onsite": "Onsite", "Hybrid": "Hybrid", "Remote": "Remote"}.get(
            next(l[6] for l in LOCATIONS if l[0] == location_id), "Onsite"
        ),
        is_high_potential=random.random() < 0.12,
    )
    return e


def _seed_employees(db, departments, positions) -> list[models.Employee]:
    employees: list[models.Employee] = []

    # CEO first - anchors the manager chain.
    ceo_location = "HQ-LAS"
    ceo = _make_employee("EXEC", positions["EXEC"][7], ceo_location, rand_date(TODAY - dt.timedelta(days=YEARS_OF_HISTORY * 365), TODAY - dt.timedelta(days=1500)))
    db.add(ceo)
    db.flush()
    departments["EXEC"].leader_employee_id = ceo.employee_id
    employees.append(ceo)

    for dept_id, name, _division in DEPARTMENTS:
        if dept_id == "EXEC":
            continue
        target = TARGET_HEADCOUNT[dept_id]
        level_counts = {}
        remaining = target
        for level, _suffix, _lead, _crit, pct in LEVEL_LADDER[:-1]:  # all but VP
            n = max(1, round(target * pct))
            level_counts[level] = n
            remaining -= n
        level_counts[1] = max(1, level_counts.get(1, 0) + remaining)
        level_counts[6] = 1  # exactly one VP per department

        by_level: dict[int, list[models.Employee]] = {}

        # VP first, reports to CEO
        vp_hire = rand_date(TODAY - dt.timedelta(days=YEARS_OF_HISTORY * 365), TODAY - dt.timedelta(days=900))
        vp = _make_employee(dept_id, positions[dept_id][6], weighted_location(), vp_hire, ceo.employee_id)
        db.add(vp)
        db.flush()
        by_level[6] = [vp]
        employees.append(vp)
        departments[dept_id].leader_employee_id = vp.employee_id

        for level in [5, 4, 3, 2, 1]:
            count = level_counts.get(level, 0)
            by_level[level] = []
            manager_pool = by_level.get(level + 1, [vp])
            for _ in range(count):
                manager = random.choice(manager_pool) if manager_pool else vp
                days_back = int(YEARS_OF_HISTORY * 365 * (0.4 + 0.6 * random.random()))
                hire = rand_date(TODAY - dt.timedelta(days=days_back), TODAY - dt.timedelta(days=14))
                loc = weighted_location()
                emp = _make_employee(dept_id, positions[dept_id][level], loc, hire, manager.employee_id)
                db.add(emp)
                by_level[level].append(emp)
                employees.append(emp)
        db.flush()

    # Terminated history cohort: ~18% of current active headcount, spread
    # across the last 24 months, mostly at lower levels (realistic for churn).
    active_total = len(employees)
    term_target = int(active_total * 0.18)
    for _ in range(term_target):
        dept_id = random.choice([d for d, _, _ in DEPARTMENTS if d != "EXEC"])
        level = random.choices([1, 2, 3, 4, 5], weights=[0.35, 0.3, 0.2, 0.1, 0.05])[0]
        pos = positions[dept_id][level]
        candidates_for_mgr = [e for e in employees if e.department_id == dept_id and e.position_id in (
            positions[dept_id].get(level + 1, pos).position_id, positions[dept_id].get(6, pos).position_id
        )]
        manager = random.choice(candidates_for_mgr).employee_id if candidates_for_mgr else departments[dept_id].leader_employee_id

        term_date = rand_date(TODAY - dt.timedelta(days=730), TODAY - dt.timedelta(days=1))
        hire_date = rand_date(term_date - dt.timedelta(days=int(365 * random.uniform(0.3, 5))), term_date - dt.timedelta(days=60))
        loc = weighted_location()
        emp = _make_employee(dept_id, pos, loc, hire_date, manager)
        emp.employment_status = "Terminated"
        emp.termination_date = term_date
        vol = random.random() < 0.68
        emp.termination_type = "Voluntary" if vol else "Involuntary"
        emp.termination_reason = random.choice(TERMINATION_REASONS_VOL if vol else TERMINATION_REASONS_INVOL)
        emp.regrettable = vol and random.random() < 0.35
        db.add(emp)
        employees.append(emp)

    db.flush()
    return employees


def _seed_compensation(db, employees):
    for e in employees:
        salary, compa_ratio = salary_for_level(_level_of(db, e))
        comp = models.Compensation(
            employee_id=e.employee_id,
            effective_date=e.hire_date,
            base_salary=salary,
            currency="USD",
            pay_frequency="Annually",
            bonus_target_pct=_bonus_for_level(_level_of(db, e)),
            equity_value=_equity_for_level(_level_of(db, e)),
            compa_ratio=compa_ratio,
            change_reason="New Hire",
        )
        db.add(comp)
        if e.employment_status == "Active" and random.random() < 0.55:
            raise_date = rand_date(e.hire_date + dt.timedelta(days=365), TODAY)
            if raise_date < TODAY:
                new_salary = round(salary * random.uniform(1.03, 1.12), -2)
                comp2 = models.Compensation(
                    employee_id=e.employee_id,
                    effective_date=raise_date,
                    base_salary=new_salary,
                    currency="USD",
                    pay_frequency="Annually",
                    bonus_target_pct=_bonus_for_level(_level_of(db, e)),
                    equity_value=_equity_for_level(_level_of(db, e)),
                    compa_ratio=round(new_salary / ((SALARY_RANGE_BY_LEVEL.get(_level_of(db, e), (60000, 90000))[0] + SALARY_RANGE_BY_LEVEL.get(_level_of(db, e), (60000, 90000))[1]) / 2), 2),
                    change_reason="Annual Merit",
                )
                db.add(comp2)
    db.flush()


_position_cache: dict[str, models.Position] = {}


def _level_of(db, employee: models.Employee) -> int:
    pos = _position_cache.get(employee.position_id)
    if not pos:
        pos = db.get(models.Position, employee.position_id)
        _position_cache[employee.position_id] = pos
    return pos.job_level


def _bonus_for_level(level: int) -> float:
    return {1: 0.0, 2: 0.03, 3: 0.05, 4: 0.1, 5: 0.15, 6: 0.25, 7: 0.4}.get(level, 0.03)


def _equity_for_level(level: int) -> float:
    return {1: 0, 2: 2000, 3: 6000, 4: 15000, 5: 35000, 6: 90000, 7: 250000}.get(level, 0)


RATINGS = ["Low", "Meets", "Exceeds", "High Performer"]
RATING_WEIGHTS = [0.08, 0.55, 0.27, 0.10]
RATING_SCORE = {"Low": 2, "Meets": 3, "Exceeds": 4, "High Performer": 5}


def _seed_performance(db, employees):
    periods = ["2024-H2", "2025-H1", "2025-H2"]
    for e in employees:
        tenure_days = ((e.termination_date or TODAY) - e.hire_date).days
        n_reviews = 2 if tenure_days > 365 else (1 if tenure_days > 150 else 0)
        for period in periods[-n_reviews:] if n_reviews else []:
            rating = random.choices(RATINGS, weights=RATING_WEIGHTS)[0]
            review = models.PerformanceReview(
                employee_id=e.employee_id,
                review_period=period,
                rating=rating,
                rating_score=RATING_SCORE[rating],
                goal_completion_pct=round(random.uniform(60, 100) if rating != "Low" else random.uniform(30, 70), 1),
                reviewer_employee_id=e.manager_employee_id,
            )
            db.add(review)
            if rating == "High Performer" and random.random() < 0.3 and e.employment_status == "Active":
                e.last_promotion_date = rand_date(TODAY - dt.timedelta(days=365), TODAY)
            e.last_performance_rating = rating
    db.flush()


def _seed_pto(db, employees):
    active = [e for e in employees if e.employment_status == "Active"]
    for e in active:
        for months_ago in range(12):
            d = TODAY.replace(day=1) - dt.timedelta(days=months_ago * 30)
            period = f"{d.year:04d}-{d.month:02d}"
            used = round(max(0, random.gauss(7, 5)), 1)
            db.add(
                models.PtoUsage(
                    employee_id=e.employee_id,
                    period=period,
                    pto_hours_used=used,
                    pto_hours_available=13.33,
                    absenteeism_days=round(max(0, random.gauss(0.3, 0.5)), 1),
                )
            )
    db.flush()


def _seed_er_cases(db, departments):
    dept_ids = [d for d in departments if d != "EXEC"]
    for _ in range(42):
        opened = rand_date(TODAY - dt.timedelta(days=540), TODAY - dt.timedelta(days=1))
        closed = None
        if random.random() < 0.75:
            closed = rand_date(opened + dt.timedelta(days=3), min(opened + dt.timedelta(days=90), TODAY))
        db.add(
            models.EmployeeRelationsCase(
                case_id=ids.next("ERC"),
                department_id=random.choice(dept_ids),
                case_type=random.choice(ER_CASE_TYPES),
                severity=random.choices(ER_SEVERITY, weights=ER_SEVERITY_WEIGHTS)[0],
                opened_date=opened,
                closed_date=closed,
                source=random.choices(["ER Intake", "Ethics Hotline"], weights=[0.8, 0.2])[0],
            )
        )
    db.flush()


def _seed_engagement(db, departments, employees):
    dept_ids = [d for d in departments if d != "EXEC"]
    periods = [("2025-Q1", 95, 100), ("2025-Q2", 100, 100), ("2025-Q3", 100, 100)]
    base_trend = 0
    for i, (period, start_pct, _end_pct) in enumerate(periods):
        launched = dt.date.fromisoformat(f"{period[:4]}-{int(period[-1]) * 3 - 2:02d}-01")
        closed = launched + dt.timedelta(days=14)
        active_count = sum(1 for e in employees if e.employment_status == "Active")
        eligible = active_count
        responded = int(eligible * random.uniform(0.68, 0.87))
        survey = models.EngagementSurvey(
            name=f"Pulse Survey {period}",
            period=period,
            launched_date=launched,
            closed_date=closed,
            eligible_count=eligible,
            responded_count=responded,
        )
        db.add(survey)
        db.flush()

        base_trend += random.uniform(-2, 3)
        for dept_id in dept_ids:
            dept_active = [e for e in employees if e.department_id == dept_id and e.employment_status == "Active"]
            n_responses = max(1, len(dept_active) // 2)
            for _ in range(n_responses):
                score = max(20, min(98, random.gauss(68 + base_trend, 12)))
                sentiment = "Positive" if score > 70 else ("Neutral" if score > 45 else "Negative")
                db.add(
                    models.EngagementResponse(
                        survey_id=survey.id,
                        department_id=dept_id,
                        engagement_score=round(score, 1),
                        leadership_confidence=round(max(20, min(98, random.gauss(65 + base_trend, 14))), 1),
                        career_growth=round(max(20, min(98, random.gauss(60 + base_trend, 14))), 1),
                        belonging=round(max(20, min(98, random.gauss(70 + base_trend, 13))), 1),
                        recognition=round(max(20, min(98, random.gauss(62 + base_trend, 15))), 1),
                        wellbeing=round(max(20, min(98, random.gauss(64 + base_trend, 14))), 1),
                        manager_effectiveness=round(max(20, min(98, random.gauss(70 + base_trend, 13))), 1),
                        sentiment=sentiment,
                    )
                )
    db.flush()


READINESS = ["Ready Now", "Ready 1-2yr", "Not Ready", "No Successor"]
READINESS_WEIGHTS = [0.25, 0.35, 0.15, 0.25]


def _seed_succession(db, positions, employees):
    by_dept_level: dict[tuple[str, int], list[models.Employee]] = {}
    for e in employees:
        if e.employment_status != "Active":
            continue
        lvl = _level_of(db, e)
        by_dept_level.setdefault((e.department_id, lvl), []).append(e)

    for dept_id, levels in positions.items():
        for level, pos in levels.items():
            if not pos.is_leadership:
                continue
            readiness = random.choices(READINESS, weights=READINESS_WEIGHTS)[0]
            successor = None
            if readiness in ("Ready Now", "Ready 1-2yr"):
                pool = by_dept_level.get((dept_id, level - 1), [])
                if pool:
                    successor = random.choice(pool).employee_id
                else:
                    readiness = "No Successor"
            db.add(
                models.SuccessionPlan(
                    position_id=pos.position_id,
                    successor_employee_id=successor,
                    readiness=readiness,
                )
            )
    db.flush()


def _seed_training(db, employees):
    for e in employees:
        if e.employment_status != "Active":
            continue
        for course_name, is_compliance in TRAINING_COURSES:
            if is_compliance or random.random() < 0.6:
                status = random.choices(["Completed", "In Progress", "Not Started"], weights=[0.72, 0.18, 0.1])[0]
                completion_date = rand_date(max(e.hire_date, TODAY - dt.timedelta(days=365)), TODAY) if status == "Completed" else None
                db.add(
                    models.TrainingCompletion(
                        employee_id=e.employee_id,
                        course_name=course_name,
                        is_compliance=is_compliance,
                        status=status,
                        completion_date=completion_date,
                        hours=round(random.uniform(0.5, 4), 1) if status == "Completed" else 0.0,
                    )
                )
    db.flush()


def _seed_workforce_plans(db, departments, employees):
    dept_ids = [d for d in departments if d != "EXEC"]
    for dept_id in dept_ids:
        for months_ago in range(12):
            d = TODAY.replace(day=1) - dt.timedelta(days=months_ago * 30)
            last_day = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)
            actual = sum(
                1
                for e in employees
                if e.department_id == dept_id and e.hire_date <= last_day and (e.termination_date is None or e.termination_date > last_day)
            )
            budget = round(actual * random.uniform(0.97, 1.08))
            db.add(
                models.WorkforcePlan(
                    department_id=dept_id,
                    plan_month=d,
                    budget_headcount=budget,
                    forecast_headcount=round(actual * random.uniform(0.98, 1.05)),
                    actual_headcount=actual,
                    expected_hires=random.randint(0, 3),
                    expected_exits=random.randint(0, 2),
                )
            )
    db.flush()


JOB_CATEGORY_WEIGHTS = ["Open", "Filled", "Closed", "On Hold", "Draft"]
JOB_STATE_WEIGHTS = [0.25, 0.40, 0.15, 0.1, 0.1]


def _seed_requisitions(db, departments, locations, employees, positions) -> list[models.Requisition]:
    dept_ids = [d for d in departments if d != "EXEC"]
    reqs = []
    for _ in range(46):
        dept_id = random.choice(dept_ids)
        level = random.choices([1, 2, 3, 4], weights=[0.35, 0.35, 0.2, 0.1])[0]
        pos = positions[dept_id].get(level, positions[dept_id][1])
        lo, hi = SALARY_RANGE_BY_LEVEL[level]
        managers = [e for e in employees if e.department_id == dept_id and _level_of(db, e) >= level + 1 and e.employment_status == "Active"]
        hiring_manager = random.choice(managers).employee_id if managers else departments[dept_id].leader_employee_id
        recruiters = [e for e in employees if e.department_id == "HR" and e.employment_status == "Active"]
        recruiter = random.choice(recruiters).employee_id if recruiters else departments["HR"].leader_employee_id

        opened = rand_date(TODAY - dt.timedelta(days=365), TODAY - dt.timedelta(days=3))
        state = random.choices(JOB_CATEGORY_WEIGHTS, weights=JOB_STATE_WEIGHTS)[0]
        target_close = opened + dt.timedelta(days=random.randint(30, 75))
        closed_date = None
        filled_date = None
        if state in ("Filled", "Closed"):
            closed_date = rand_date(opened + dt.timedelta(days=15), min(opened + dt.timedelta(days=120), TODAY))
            if state == "Filled":
                filled_date = closed_date

        req = models.Requisition(
            requisition_id=ids.next("REQ"),
            jobvite_eid=ids.next("jveid"),
            title=pos.title,
            department_id=dept_id,
            location_id=weighted_location(),
            hiring_manager_employee_id=hiring_manager,
            recruiter_employee_id=recruiter,
            job_state=state,
            category=pos.job_family,
            eeo_category=EEO_BY_LEVEL.get(level, "Office"),
            posting_type=random.choices(["External", "Internal", "Both"], weights=[0.6, 0.1, 0.3])[0],
            remote_type=random.choices(["Onsite", "Hybrid Remote", "No Remote", "Temporarily Remote"], weights=[0.35, 0.35, 0.2, 0.1])[0],
            position_count=random.choices([1, 2, 3], weights=[0.75, 0.18, 0.07])[0],
            salary_min=lo,
            salary_max=hi,
            salary_currency="USD",
            salary_frequency="Annually",
            opened_date=opened,
            target_close_date=target_close,
            closed_date=closed_date,
            filled_date=filled_date,
        )
        db.add(req)
        reqs.append(req)
    db.flush()
    return reqs


def _seed_candidates(db) -> list[models.Candidate]:
    candidates = []
    for _ in range(480):
        first = fake.first_name()
        last = fake.last_name()
        source, source_type = random.choice(CANDIDATE_SOURCES)
        c = models.Candidate(
            candidate_id=ids.next("CAND"),
            jobvite_eid=ids.next("jveid"),
            first_name=first,
            last_name=last,
            email=fake.unique.email(),
            city=fake.city(),
            state=fake.state_abbr(),
            postal_code=fake.postcode(),
            country="United States",
            current_title=random.choice(CANDIDATE_TITLES),
            current_company_name=fake.company(),
            work_status=random.choices(CANDIDATE_WORK_STATUSES, weights=CANDIDATE_WORK_STATUS_WEIGHTS)[0],
            veteran_status=random.choices(CANDIDATE_VETERAN_STATUSES, weights=CANDIDATE_VETERAN_STATUS_WEIGHTS)[0],
            source=source,
            source_type=source_type,
            gender=weighted_gender(),
            race_ethnicity=weighted_race(),
            is_internal=random.random() < 0.08,
        )
        db.add(c)
        candidates.append(c)
    db.flush()
    return candidates


def _seed_applications_and_interviews(db, requisitions, candidates, employees):
    employees_by_dept: dict[str, list[models.Employee]] = {}
    for e in employees:
        if e.employment_status == "Active":
            employees_by_dept.setdefault(e.department_id, []).append(e)

    for req in requisitions:
        n_apps = random.randint(4, 18)
        req_candidates = random.sample(candidates, min(n_apps, len(candidates)))
        hired_done = False
        for cand in req_candidates:
            applied = rand_date(req.opened_date, req.closed_date or TODAY)
            app = models.Application(
                application_id=ids.next("APP"),
                candidate_id=cand.candidate_id,
                requisition_id=req.requisition_id,
                workflow_state="New",
                workflow_state_eid=WORKFLOW_STATE_EIDS["New"],
                applied_date=applied,
            )

            if req.job_state == "Filled" and not hired_done and cand == req_candidates[0]:
                hired_done = True
                app.workflow_state = "Hired"
                app.workflow_state_eid = WORKFLOW_STATE_EIDS["Hired"]
                app.disposition = "Hired"
                offer_ext = applied + dt.timedelta(days=random.randint(10, 35))
                offer_acc = offer_ext + dt.timedelta(days=random.randint(1, 7))
                app.offer_extended_date = min(offer_ext, req.filled_date or TODAY)
                app.offer_accepted_date = min(offer_acc, req.filled_date or TODAY)
                app.hire_date = req.filled_date
                app.start_date = (req.filled_date or TODAY) + dt.timedelta(days=14)
                app.offer_salary = round(random.uniform(req.salary_min, req.salary_max), -2)
                app.hiring_manager_satisfaction = random.randint(3, 5)
                if app.hire_date and (TODAY - app.hire_date).days > 90:
                    app.new_hire_90day_retained = random.random() < 0.92
                if app.hire_date and (TODAY - app.hire_date).days > 365:
                    app.new_hire_1yr_retained = random.random() < 0.85
            else:
                stage = random.choices(
                    ["Rejected", "Withdrawn", "Screening", "Interview", "Offer"],
                    weights=[0.55, 0.1, 0.15, 0.15, 0.05],
                )[0]
                app.workflow_state = stage
                app.workflow_state_eid = WORKFLOW_STATE_EIDS[stage]
                if stage == "Rejected":
                    app.disposition = random.choice(["Not a Fit", "Not Enough Experience", "Position Filled"])
                    app.rejected_date = applied + dt.timedelta(days=random.randint(2, 20))
                elif stage == "Offer":
                    app.offer_extended_date = applied + dt.timedelta(days=random.randint(10, 30))

            db.add(app)

            if app.workflow_state in ("Interview", "Offer", "Hired") or (app.workflow_state == "Rejected" and random.random() < 0.3):
                dept_employees = employees_by_dept.get(req.department_id, [])
                n_interviews = random.randint(1, 3)
                for _ in range(n_interviews):
                    interviewer = random.choice(dept_employees).employee_id if dept_employees else req.hiring_manager_employee_id
                    sched = applied + dt.timedelta(days=random.randint(3, 25))
                    interview_id = ids.next("INT")
                    db.add(
                        models.Interview(
                            interview_id=interview_id,
                            jobvite_interview_eid=f"jveid-int-{interview_id}",
                            application_id=app.application_id,
                            interviewer_employee_id=interviewer,
                            scheduled_date=min(sched, TODAY),
                            duration_minutes=random.choice([30, 45, 60, 90]),
                            timezone=random.choice(["America/Los_Angeles", "America/Chicago", "America/New_York"]),
                            evaluation_link=f"https://app.jvistg2.com/jhire/evaluations-submit/{app.application_id}/{interview_id}",
                            stage=random.choice(INTERVIEW_STAGES),
                            status="Completed" if sched < TODAY else "Scheduled",
                            evaluation_score=random.randint(2, 5) if sched < TODAY else None,
                            recommendation=random.choices(RECOMMENDATIONS, weights=RECOMMENDATION_WEIGHTS)[0]
                            if sched < TODAY
                            else None,
                        )
                    )
    db.flush()


DEMO_USERS = [
    # email, full_name, role, department_scope, link_to_employee
    ("admin", "Chris Johnson", models.ROLE_ADMIN, None),
    ("admin@admin", "Chris Johnson", models.ROLE_ADMIN, None),
]
DEMO_PASSWORD = "password"


def _seed_users(db, departments, employees):
    roles = {r.name: r for r in db.query(models.Role).all()}
    for email, full_name, role_name, dept_scope in DEMO_USERS:
        user = models.User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(DEMO_PASSWORD),
            auth_provider="local",
            role_id=roles[role_name].id,
            is_active=True,
        )
        db.add(user)
        db.flush()
        if dept_scope:
            for dept_id in dept_scope:
                db.add(models.UserDepartmentScope(user_id=user.id, department_id=dept_id))
    db.flush()


def _seed_ingestion_log(db):
    for source, entity in [
        ("seed", "departments"), ("seed", "locations"), ("seed", "positions"),
        ("seed", "employees"), ("seed", "compensation"), ("seed", "requisitions"),
        ("seed", "candidates"), ("seed", "applications"), ("seed", "interviews"),
        ("seed", "engagement_surveys"),
    ]:
        db.add(
            models.IngestionRun(
                source_system=source,
                entity=entity,
                started_at=dt.datetime.utcnow(),
                completed_at=dt.datetime.utcnow(),
                status="success",
                records_processed=0,
                notes="Synthetic seed data generated for demo/dev purposes (no live API calls).",
            )
        )
    db.flush()


if __name__ == "__main__":
    seed()
