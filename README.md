# Workforce Competency Management System

> An AI-powered workforce analytics platform that automates employee data processing, skill classification, project assignment, and training recommendations using Machine Learning.

---

## Problem Statement

Organizations receive daily workforce data from multiple departments in scattered Excel sheets, making it difficult for management to get real-time visibility into workforce utilization. Tracking bench strength, delivery resources, leave status, and bench duration is time-consuming and error-prone. Additionally, there is no centralized system to monitor employee skills, recommend training for bench resources, or track course completion — leading to poor resource planning, underutilization, and ineffective decision-making.

---

## Solution

A centralized web-based dashboard that ingests Excel workforce data, processes it through an ML model, and provides real-time analytics — eliminating manual effort and enabling data-driven decisions.

---

## SDG Alignment

| SDG | Goal | Relevance |
|---|---|---|
| SDG 8 | Decent Work and Economic Growth | Optimizes workforce utilization and employee development |
| SDG 9 | Industry, Innovation and Infrastructure | Uses AI/ML to build innovative workforce infrastructure |
| SDG 4 | Quality Education | Recommends personalized training courses for upskilling |

---

## Features

- **Excel Upload** — Upload employee datasets from multiple departments
- **ML Categorization** — Auto-classifies employees as High / Medium / Low performers
- **Project Assignment** — Automatically assigns projects based on ML prediction
- **Course Recommendation** — Recommends training courses based on employee skill
- **Duplicate Detection** — Skips exact duplicate records on every upload
- **Authentication** — Secure Signup & Login with password hashing
- **Admin Panel** — Add or delete employees manually with live search
- **Analytics Dashboard** — Visual charts for performance and category distribution
- **Analysis Page** — Filter and search employee records
- **Performance Page** — Visual performance tracking with charts

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| ML Model | Scikit-learn |
| NLP | spaCy (en_core_web_sm) |
| Database | PostgreSQL (Render) / SQLite (local) |
| ORM | SQLAlchemy |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Charts | Chart.js |
| Icons | Font Awesome |
| Backend Deployment | Render.com |
| Frontend Deployment | Vercel |

---

## Project Structure

```
workforce-competency-management/
│
├── employee-ai-backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS
│   │   ├── routes.py        # All API endpoints
│   │   ├── services.py      # ML processing + duplicate check
│   │   ├── model.py         # ML model loader
│   │   ├── nlp.py           # Skill extraction using spaCy
│   │   ├── utils.py         # Project assignment + course recommendation
│   │   ├── db_models.py     # SQLAlchemy models (Employee, User)
│   │   └── database.py      # Database connection
│   ├── saved_model/
│   │   ├── model.pkl        # Trained ML classification model
│   │   └── course.pkl       # Course recommendation model
│   ├── data/
│   │   └── employee_sample_dataset.xlsx
│   ├── run.py
│   ├── train.py
│   └── requirements.txt
│
└── empolyee_dash_frontend/
    ├── login.html           # Login & Signup
    ├── dashboard.html       # Main analytics dashboard
    ├── upload.html          # Excel file upload
    ├── analysis.html        # Employee analysis & filtering
    ├── performance.html     # Performance charts
    ├── admin.html           # Admin panel
    └── style.css
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/signup` | Register a new user |
| `POST` | `/login` | Login with email & password |
| `POST` | `/upload` | Upload Excel file for ML processing |
| `GET` | `/employees` | Get all employees |
| `POST` | `/add-employee` | Manually add an employee |
| `DELETE` | `/employees/{id}` | Delete an employee |

---

## Excel File Format

Uploaded Excel file must contain these columns:

| Column | Description |
|---|---|
| `Name` | Employee full name |
| `Skill` | Primary skill (e.g. python, java, sql) |
| `Grade` | Grade level — G3, G4, G5, or G6 |
| `Bench_Days` | Number of days on bench |

---

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/workforce-competency-management.git
cd workforce-competency-management/employee-ai-backend
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Run the backend
```bash
python run.py
```
Backend runs at: `http://127.0.0.1:8000`
API docs at: `http://127.0.0.1:8000/docs`

### 5. Run the frontend
```bash
cd ../empolyee_dash_frontend
python -m http.server 3000
```
Open: `http://localhost:3000/login.html`

---

## Deployment

| Service | Platform | URL |
|---|---|---|
| Backend (FastAPI) | Render.com | `https://workforce-competency-management-system.onrender.com` |
| Frontend (HTML) | Vercel | `https://workforce-competency-management-sys.vercel.app` |

### Render Settings

| Setting | Value |
|---|---|
| Root Directory | `employee-ai-backend` |
| Build Command | `pip install -r requirements.txt && python -m spacy download en_core_web_sm` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### Vercel Settings

| Setting | Value |
|---|---|
| Root Directory | `empolyee_dash_frontend` |
| Framework Preset | Other |

---

## Duplicate Detection Logic

On every upload, the system checks if a record with the same **Name + Skill + Category** already exists:

- Same Name + Same Skill + Same Category → **Skipped**
- Same Name + Different Skill or Category → **Added**

After upload, the frontend shows:
```
✔ 8 new records added
⚠ 3 duplicates skipped
Total rows in file: 11
```

---

## ML Model

The ML model predicts employee performance category based on:
- `Bench_Days` — number of days on bench
- `Grade_Encoded` — numeric encoding of employee grade (G3=3, G4=4, G5=5, G6=6)

Output categories: **High**, **Medium**, **Low**

Based on category:
- High → Advanced Project + skill-based course
- Medium → Intermediate Project + skill-based course
- Low → Training Required + General Training

---

## License

This project is built for educational and internal enterprise use.

---

> Built with FastAPI + Scikit-learn + spaCy + Chart.js
