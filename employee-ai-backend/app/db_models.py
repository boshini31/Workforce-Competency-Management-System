from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    skill = Column(String)
    category = Column(String)
    project = Column(String)
    course = Column(String)


# ✅ Added User model for login/signup
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # stored as sha256 hash

# ✅ NEW: Course Tracking model
class CourseTracking(Base):
    __tablename__ = "course_tracking"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, index=True)          # FK to employees.id
    employee_name = Column(String)
    course_name = Column(String)
    assigned_date = Column(Date)
    deadline_date = Column(Date)
    completion_date = Column(Date, nullable=True)       # NULL = not yet done
    status = Column(String, default="In Progress")     # In Progress / Completed / Overdue
    progress_percent = Column(Float, default=0.0)  


class EmployeeCompleteRequest(Base):
    
    name: str

