from datetime import date, timedelta
from app.db_models import CourseTracking 
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd
from app.services import process_data
from app.nlp import extract_skill
from app.database import SessionLocal
from app.db_models import Employee, User
import hashlib

router = APIRouter()


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SelfCompleteRequest(BaseModel):
    employee_name: str  

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/signup")
def signup(data: SignupRequest):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(name=data.name, email=data.email, password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.close()
    return {"message": "Signup successful"}


@router.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    db.close()
    if not user or user.password != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful", "name": user.name, "email": user.email}


# ─────────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────────

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files are supported")

    df = pd.read_excel(file.file)

    if 'Skill' not in df.columns:
        raise HTTPException(status_code=400, detail="Excel file must contain a 'Skill' column")

    df['Skill'] = df['Skill'].astype(str).apply(extract_skill)

    result = process_data(df)

    added   = int(result['_added'].iloc[0])   if '_added'   in result.columns else 0
    skipped = int(result['_skipped'].iloc[0]) if '_skipped' in result.columns else 0

    records = result.drop(columns=['_added', '_skipped', '_status'], errors='ignore').to_dict(orient="records")

    return {
        "records": records,
        "added":   added,
        "skipped": skipped,
        "total":   len(records)
    }


# ─────────────────────────────────────────────
# GET ALL EMPLOYEES
# ─────────────────────────────────────────────

@router.get("/employees")
def get_employees():
    db = SessionLocal()
    employees = db.query(Employee).all()
    db.close()
    return [
        {
            "id":       e.id,
            "name":     e.name,
            "skill":    e.skill,
            "category": e.category,
            "project":  e.project,
            "course":   e.course
        }
        for e in employees
    ]


# ─────────────────────────────────────────────
# ADD EMPLOYEE MANUALLY (admin form)
# ─────────────────────────────────────────────

class AddEmployeeRequest(BaseModel):
    name:       str
    skill:      str
    grade:      str
    bench_days: int


@router.post("/add-employee")
def add_employee(data: AddEmployeeRequest):
    from app.utils import assign_project, recommend_course
    from app.model import load_model

    grade_map = {"G3": 3, "G4": 4, "G5": 5, "G6": 6}
    grade_encoded = grade_map.get(data.grade, 3)

    model = load_model()
    X = pd.DataFrame([{"Bench_Days": data.bench_days, "Grade_Encoded": grade_encoded}])
    category = model.predict(X)[0]

    skill_clean = extract_skill(data.skill)
    project     = assign_project({"category": category})
    course      = recommend_course(skill_clean)

    db = SessionLocal()

    # Duplicate check
    existing = db.query(Employee).filter(
        Employee.name     == data.name,
        Employee.skill    == skill_clean,
        Employee.category == category
    ).first()

    if existing:
        db.close()
        raise HTTPException(
            status_code=400,
            detail=f"{data.name} with skill '{skill_clean}' and category '{category}' already exists."
        )

    emp = Employee(
        name     = data.name,
        skill    = skill_clean,
        category = category,
        project  = project,
        course   = course
    )
    db.add(emp)
    db.flush()  # get emp.id

    # Auto-create CourseTracking with AI-assigned duration
    from app.utils import course_duration_days
    from datetime import date, timedelta
    duration    = course_duration_days(category)
    assigned_dt = date.today()
    deadline_dt = assigned_dt + timedelta(days=duration)

    track = CourseTracking(
        employee_id      = emp.id,
        employee_name    = data.name,
        course_name      = course,
        assigned_date    = assigned_dt,
        deadline_date    = deadline_dt,
        completion_date  = None,
        status           = "In Progress",
        progress_percent = 0.0
    )
    db.add(track)
    db.commit()
    db.close()

    return {"message": f"{data.name} added as '{category}' — Project: {project}, Course: {course}, Deadline: {deadline_dt} ({duration}d)"}


# ─────────────────────────────────────────────
# DELETE EMPLOYEE (admin)
# ─────────────────────────────────────────────

@router.delete("/employees/{emp_id}")
def delete_employee(emp_id: int):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        db.close()
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    db.close()
    return {"message": "Employee deleted successfully"}


  # add CourseTracking to existing import line


# ── Pydantic schemas ──────────────────────────────────────────────

class AssignCourseRequest(BaseModel):
    employee_id: int
    course_name: str
    duration_days: int = 30          # default 30-day window

class UpdateProgressRequest(BaseModel):
    progress_percent: float          # 0–100

class CompleteCourseRequest(BaseModel):
    completion_date: str             # "YYYY-MM-DD"


# ── Helper: auto-compute status ───────────────────────────────────

def compute_status(deadline: date, completion: date | None, progress: float) -> str:
    if completion:
        return "Completed"
    if date.today() > deadline:
        return "Overdue"
    return "In Progress"


# ── Assign a course to an employee ───────────────────────────────

@router.post("/course-tracking/assign")
def assign_course(data: AssignCourseRequest):
    db = SessionLocal()

    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        db.close()
        raise HTTPException(status_code=404, detail="Employee not found")

    # Prevent duplicate active assignment for same course
    existing = db.query(CourseTracking).filter(
        CourseTracking.employee_id == data.employee_id,
        CourseTracking.course_name == data.course_name,
        CourseTracking.status != "Completed"
    ).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Course already assigned and not yet completed")

    assigned = date.today()
    deadline = assigned + timedelta(days=data.duration_days)

    record = CourseTracking(
        employee_id      = data.employee_id,
        employee_name    = emp.name,
        course_name      = data.course_name,
        assigned_date    = assigned,
        deadline_date    = deadline,
        completion_date  = None,
        status           = "In Progress",
        progress_percent = 0.0
    )
    db.add(record)
    db.commit()
    emp_name = emp.name
    db.close()
    return {"message": f"Course '{data.course_name}' assigned to {emp.name}. Deadline: {deadline}"}


# ── Get all course tracking records ──────────────────────────────

@router.get("/course-tracking")
def get_all_course_tracking():
    db = SessionLocal()
    records = db.query(CourseTracking).all()

    # Auto-update overdue status on the fly
    result = []
    for r in records:
        status = compute_status(r.deadline_date, r.completion_date, r.progress_percent)
        result.append({
            "id":               r.id,
            "employee_id":      r.employee_id,
            "employee_name":    r.employee_name,
            "course_name":      r.course_name,
            "assigned_date":    str(r.assigned_date),
            "deadline_date":    str(r.deadline_date),
            "completion_date":  str(r.completion_date) if r.completion_date else None,
            "status":           status,
            "progress_percent": r.progress_percent,
            "days_remaining":   max((r.deadline_date - date.today()).days, 0) if not r.completion_date else 0
        })

    db.close()
    return result


# ── Get course tracking for a specific employee ───────────────────

@router.get("/course-tracking/employee/{employee_id}")
def get_employee_courses(employee_id: int):
    db = SessionLocal()
    records = db.query(CourseTracking).filter(
        CourseTracking.employee_id == employee_id
    ).all()

    result = []
    for r in records:
        status = compute_status(r.deadline_date, r.completion_date, r.progress_percent)
        result.append({
            "id":               r.id,
            "course_name":      r.course_name,
            "assigned_date":    str(r.assigned_date),
            "deadline_date":    str(r.deadline_date),
            "completion_date":  str(r.completion_date) if r.completion_date else None,
            "status":           status,
            "progress_percent": r.progress_percent,
            "days_remaining":   max((r.deadline_date - date.today()).days, 0) if not r.completion_date else 0
        })

    db.close()
    return result


# ── Update progress % ─────────────────────────────────────────────

@router.patch("/course-tracking/{record_id}/progress")
def update_progress(record_id: int, data: UpdateProgressRequest):
    db = SessionLocal()
    record = db.query(CourseTracking).filter(CourseTracking.id == record_id).first()
    if not record:
        db.close()
        raise HTTPException(status_code=404, detail="Record not found")

    record.progress_percent = max(0.0, min(100.0, data.progress_percent))
    record.status = compute_status(record.deadline_date, record.completion_date, record.progress_percent)
    db.commit()
    db.close()
    return {"message": "Progress updated", "progress_percent": record.progress_percent}


# ── Mark course as completed ──────────────────────────────────────

@router.patch("/course-tracking/{record_id}/complete")
def complete_course(record_id: int, data: CompleteCourseRequest):
    db = SessionLocal()
    record = db.query(CourseTracking).filter(CourseTracking.id == record_id).first()
    if not record:
        db.close()
        raise HTTPException(status_code=404, detail="Record not found")

    record.completion_date  = date.fromisoformat(data.completion_date)
    record.progress_percent = 100.0
    record.status           = "Completed"
    db.commit()
    db.close()
    return {"message": f"Course '{record.course_name}' marked as completed"}


# ── Delete a tracking record ──────────────────────────────────────

@router.delete("/course-tracking/{record_id}")
def delete_course_record(record_id: int):
    db = SessionLocal()
    record = db.query(CourseTracking).filter(CourseTracking.id == record_id).first()
    if not record:
        db.close()
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    db.close()
    return {"message": "Course tracking record deleted"}

# ── One-time migration: seed course_tracking from existing employees ──
@router.post("/course-tracking/seed-from-employees")
def seed_course_tracking():
    """
    One-time migration: seed CourseTracking for all existing employees
    that don't yet have a tracking record.
    Duration is AI-assigned based on skill category:
      High → 21 days, Medium → 30 days, Low → 45 days
    """
    from app.utils import course_duration_days
    db = SessionLocal()
    employees = db.query(Employee).all()
    
    added = 0
    skipped = 0

    for emp in employees:
        if not emp.course:
            skipped += 1
            continue

        # Skip if already tracked
        existing = db.query(CourseTracking).filter(
            CourseTracking.employee_id == emp.id,
            CourseTracking.course_name == emp.course
        ).first()

        if existing:
            skipped += 1
            continue

        duration    = course_duration_days(emp.category)
        assigned_dt = date.today()
        deadline_dt = assigned_dt + timedelta(days=duration)

        record = CourseTracking(
            employee_id      = emp.id,
            employee_name    = emp.name,
            course_name      = emp.course,
            assigned_date    = assigned_dt,
            deadline_date    = deadline_dt,
            completion_date  = None,
            status           = "In Progress",
            progress_percent = 0.0
        )
        db.add(record)
        added += 1

    db.commit()
    db.close()
    return {
        "message": f"Seeded {added} records, skipped {skipped}",
        "added": added,
        "skipped": skipped,
        "note": "Durations: High=21d, Medium=30d, Low=45d"
    }

# ─────────────────────────────────────────────
# EMPLOYEE SELF-UPDATE PORTAL
# ─────────────────────────────────────────────

class SelfCompleteRequest(BaseModel):
    employee_name: str   # employee types their name to identify themselves

@router.get("/portal/my-courses")
def get_my_courses(name: str):
    """Employee looks up their assigned courses by name."""
    db = SessionLocal()
    name_clean = name.strip().lower()

    records = db.query(CourseTracking).all()
    matched = [r for r in records if r.employee_name.strip().lower() == name_clean]

    result = []
    for r in matched:
        status = compute_status(r.deadline_date, r.completion_date, r.progress_percent)
        result.append({
            "id":               r.id,
            "employee_name":    r.employee_name,
            "course_name":      r.course_name,
            "assigned_date":    str(r.assigned_date),
            "deadline_date":    str(r.deadline_date),
            "completion_date":  str(r.completion_date) if r.completion_date else None,
            "status":           status,
            "progress_percent": r.progress_percent,
            "days_remaining":   max((r.deadline_date - date.today()).days, 0) if not r.completion_date else 0
        })

    db.close()

    if not matched:
        raise HTTPException(status_code=404, detail="No courses found for this name. Check spelling.")

    return result


@router.patch("/portal/complete/{record_id}")
def self_complete_course(record_id: int, data: SelfCompleteRequest):
    """Employee marks their own course as complete."""
    db = SessionLocal()
    record = db.query(CourseTracking).filter(CourseTracking.id == record_id).first()

    if not record:
        db.close()
        raise HTTPException(status_code=404, detail="Course record not found")

    # Security: only allow if name matches
    if record.employee_name.strip().lower() != data.employee_name.strip().lower():
        db.close()
        raise HTTPException(status_code=403, detail="Name does not match. You can only complete your own courses.")

    if record.status == "Completed":
        db.close()
        raise HTTPException(status_code=400, detail="Course is already marked as completed")

    record.completion_date  = date.today()
    record.progress_percent = 100.0
    record.status           = "Completed"
    db.commit()
    db.close()

    return {"message": f"✅ '{record.course_name}' marked as completed. Well done!"}