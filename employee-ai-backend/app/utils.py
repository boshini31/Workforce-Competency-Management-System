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