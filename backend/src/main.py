from contextlib import asynccontextmanager
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv

from .routes import documents, schemas
from .db.database import engine, Base

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    last_err: Exception | None = None
    for _attempt in range(60):
        try:
            Base.metadata.create_all(bind=engine)
            last_err = None
            break
        except OperationalError as e:
            last_err = e
            time.sleep(1)
    if last_err is not None:
        raise last_err
    yield


app = FastAPI(
    title="JSON Editor API",
    description="API for managing JSON documents and schemas",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]

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
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
