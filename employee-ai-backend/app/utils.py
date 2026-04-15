def assign_project(row):
    if row['category'] == "High":
        return "Advanced Project"
    elif row['category'] == "Medium":
        return "Intermediate Project"
    else:
        return "Training Required"

def recommend_course(skill):
    courses = {
        "python": "Advanced Python",
        "java": "Spring Boot",
        "machine learning": "Deep Learning",
        "testing": "Automation Testing",
        "devops": "Docker & Kubernetes",
        "sql": "Advanced SQL"
    }
    return courses.get(skill.lower(), "General Training")


def course_duration_days(category: str) -> int:
    """
    AI-assigned course duration based on skill category:
    - High  → 21 days  (already strong, short refresher)
    - Medium → 30 days (needs structured learning)
    - Low   → 45 days  (needs intensive training)
    """
    durations = {
        "High":   21,
        "Medium": 30,
        "Low":    45,
    }
    return durations.get(category, 30)