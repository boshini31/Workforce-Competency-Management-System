# Employee AI Dashboard

An intelligent employee analytics platform that uses machine learning to categorize employees, assign projects, and recommend training courses — built with **FastAPI** (backend) and **HTML/CSS/JS** (frontend).

---

## Features

- **Excel Upload** — Upload employee datasets and auto-process them with ML
- **Duplicate Detection** — Skips exact duplicate records on every upload
- **ML Categorization** — Automatically classifies employees as High / Medium / Low performers
- **Project Assignment** — Auto-assigns projects based on ML prediction
- **Course Recommendation** — Recommends training courses based on employee skill
- **Authentication** — Signup & Login with password hashing (SHA-256)
- **Admin Panel** — Add or delete employees manually with live search
- **Analytics Dashboard** — Visual charts for performance overview and category distribution
- **Analysis Page** — Filter and search employee records

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| ML Model | Scikit-learn (pre-trained `.pkl`) |
| Database | SQLite (local) / PostgreSQL (production) |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Charts | Chart.js |
| Deployment | Render (backend) + Netlify (frontend) |

---

## Project Structure

```
employee-ai-backend/
│
├── app/
│   ├── main.py          # FastAPI app entry point + CORS
│   ├── routes.py        # All API endpoints
│   ├── services.py      # ML processing + duplicate check logic
│   ├── models.py        # ML model loader
│   ├── nlp.py           # Skill extraction (NLP)
│   ├── utils.py         # Project assignment + course recommendation
│   ├── db_models.py     # SQLAlchemy database models
│   └── database.py      # Database connection setup
│
├── empolyee_dash_frontend/
│   ├── login.html       # Login & Signup page
│   ├── dashboard.html   # Main analytics dashboard
│   ├── upload.html      # Excel file upload page
│   ├── analysis.html    # Employee analysis & filtering
│   ├── performance.html # Performance tracking
│   ├── admin.html       # Admin panel (add/delete employees)
│   └── style.css        # Shared styles
│
├── saved_model/
│   ├── model.pkl        # Trained ML classification model
│   └── course.pkl       # Course recommendation model
│
├── data/
│   └── employee_sample_dataset.xlsx
│
├── run.py               # App entry point
├── train.py             # Model training script
└── requirements.txt
```

---

## Getting Started (Local Setup)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/employee-ai-backend.git
cd employee-ai-backend
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the backend

```bash
python run.py
```

Backend runs at: `http://127.0.0.1:8000`
Swagger API docs: `http://127.0.0.1:8000/docs`

### 4. Run the frontend

```bash
cd empolyee_dash_frontend
python -m http.server 3000
```

Open in browser: `http://localhost:3000/login.html`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/signup` | Register a new user |
| `POST` | `/login` | Login with email & password |
| `POST` | `/upload` | Upload Excel file for ML processing |
| `GET` | `/employees` | Get all employees from database |
| `POST` | `/add-employee` | Manually add an employee (admin) |
| `DELETE` | `/employees/{id}` | Delete an employee by ID |

---

## Excel File Format

Your uploaded Excel file must contain these columns:

| Column | Description |
|---|---|
| `Name` | Employee full name |
| `Skill` | Primary skill (e.g. python, java, sql) |
| `Grade` | Grade level — G3, G4, G5, or G6 |
| `Bench_Days` | Number of days on bench |

---

## Duplicate Detection Logic

On every upload, the system checks if a record with the **same Name + Skill + Category** already exists in the database.

- Same employee, same skill, same category → **Skipped**
- Same employee, different skill or category → **Added** (treated as a new entry)

After upload, the frontend shows a summary:
```
✔ 8 new records added
⚠ 3 duplicates skipped
Total rows in file: 11
```

---

## Deployment

### Backend → Render.com

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port 10000` |

### Frontend → Netlify

| Setting | Value |
|---|---|
| Publish Directory | `empolyee_dash_frontend` |

After deploying, update the API URL in all frontend HTML files:

```js
// Change this in login.html, dashboard.html, upload.html, admin.html, analysis.html
const API = "https://your-app-name.onrender.com";
```

---

## Environment Notes

- The free tier on Render sleeps after 15 minutes of inactivity — first request may take ~30 seconds to wake up
- SQLite resets on Render redeploy — use Render's PostgreSQL for persistent storage in production
- Make sure `saved_model/` folder with `.pkl` files is committed to GitHub

---

## Screenshots

> Add your screenshots here after deployment

| Page | Description |
|---|---|
| `login.html` | User login and signup |
| `dashboard.html` | Analytics overview with charts |
| `upload.html` | Excel upload with duplicate summary |
| `admin.html` | Add/delete employees manually |
| `analysis.html` | Filter and search employee records |

---

## License

This project is for educational and internal use.

---

> Built with FastAPI + Scikit-learn + Chart.js
