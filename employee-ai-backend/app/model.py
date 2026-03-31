import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

MODEL_PATH = "saved_model/model.pkl"

def train_model():
    df = pd.read_excel("data/employee_sample_dataset.xlsx")

    df['Grade_Encoded'] = df['Grade'].map({
        'G3': 3,
        'G4': 4,
        'G5': 5,
        'G6': 6
    })

    X = df[['Bench_Days', 'Grade_Encoded']]
    y = df['Performance_Label']

    model = RandomForestClassifier()
    model.fit(X, y)

    os.makedirs("saved_model", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("Model trained & saved")

def load_model():
    return joblib.load(MODEL_PATH)