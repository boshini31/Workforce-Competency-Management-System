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
    db.commit()
    db.close()

    return {"message": f"{data.name} added successfully as '{category}' — Project: {project}, Course: {course}"}


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
