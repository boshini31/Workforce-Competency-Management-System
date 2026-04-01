from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.db_models import Base
from app.database import engine

app = FastAPI()

# ✅ CORS — allows your frontend HTML files to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://workforce-competency-management-sys.vercel.app",
                   "http://localhost:3000"],  # In production, replace * with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(router)
