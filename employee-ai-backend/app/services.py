from datetime import date, timedelta
from app.model import load_model
from app.utils import assign_project, recommend_course, course_duration_days
from app.database import SessionLocal
from app.db_models import Employee, CourseTracking

model = load_model()

def process_data(df):

    df['Grade_Encoded'] = df['Grade'].map({
        'G3': 3,
        'G4': 4,
        'G5': 5,
        'G6': 6
    })

    X = df[['Bench_Days', 'Grade_Encoded']]

    df['category'] = model.predict(X)

    df['project'] = df.apply(assign_project, axis=1)
    df['course'] = df['Skill'].apply(recommend_course)

    db = SessionLocal()

    added   = 0
    skipped = 0

    for _, row in df.iterrows():
        name     = row.get("Name")
        skill    = row.get("Skill")
        category = row.get("category")
        project  = row.get("project")
        course   = row.get("course")

        # ✅ Duplicate check: same name + skill + category = skip
        # Same person with different skill or category = allowed
        existing = db.query(Employee).filter(
            Employee.name     == name,
            Employee.skill    == skill,
            Employee.category == category
        ).first()

        if existing:
            skipped += 1
            continue

        emp = Employee(
            name     = name,
            skill    = skill,
            category = category,
            project  = project,
            course   = course
        )
        db.add(emp)
        db.flush()  # get emp.id before commit

        # Auto-create CourseTracking with AI-assigned duration
        duration = course_duration_days(category)
        assigned_dt = date.today()
        deadline_dt = assigned_dt + timedelta(days=duration)

        track = CourseTracking(
            employee_id      = emp.id,
            employee_name    = name,
            course_name      = course,
            assigned_date    = assigned_dt,
            deadline_date    = deadline_dt,
            completion_date  = None,
            status           = "In Progress",
            progress_percent = 0.0
        )
        db.add(track)
        added += 1

    db.commit()
    db.close()

    # ✅ Mark status per row so frontend can show added vs duplicate
    seen = set()
    def mark_status(row):
        key = (row.get("Name"), row.get("Skill"), row.get("category"))
        if key in seen:
            return 'duplicate'
        seen.add(key)
        return 'added'

    df['_status']  = df.apply(mark_status, axis=1)
    df['_added']   = added
    df['_skipped'] = skipped

    return df