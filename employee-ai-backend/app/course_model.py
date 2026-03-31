import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib, os

COURSE_MODEL_PATH = "saved_model/course.pkl"

df = pd.read_excel("data/employee_sample_dataset.xlsx")
print(df.head())
print(df.columns)

def train_course_model():
    df = pd.read_excel("data/employee_sample_dataset.xlsx")

    df['Grade_Encoded'] = df['Grade'].map({'G3':3,'G4':4,'G5':5,'G6':6})

    X = df[['Bench_Days','Grade_Encoded']]
    y = df['Course_Label']

    model = RandomForestClassifier()
    model.fit(X,y)

    os.makedirs("saved_model",exist_ok=True)
    joblib.dump(model, COURSE_MODEL_PATH)

def load_course_model():
    return joblib.load(COURSE_MODEL_PATH)