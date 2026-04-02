from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db_models import Base
from app.database import engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # temporary - open to all to test
    allow_credentials=False,  # must be False when using *
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

from app.routes import router
app.include_router(router)