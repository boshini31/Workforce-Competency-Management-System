import spacy

nlp = spacy.load("en_core_web_sm")

SKILLS = ["python", "java", "machine learning", "testing", "devops", "sql"]

def extract_skill(text):
    doc = nlp(text.lower())
    for token in doc:
        if token.text in SKILLS:
            return token.text
    return "general"