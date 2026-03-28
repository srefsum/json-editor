from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .routes import documents, schemas
from .db.database import engine, Base

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JSON Editor API",
    description="API for managing JSON documents and schemas",
    version="1.0.0"
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(schemas.router)

@app.get("/")
def root():
    return {
        "message": "JSON Editor API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
