"""
TempCover Insurance Platform
FastAPI application entry point
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routers import auth, drivers, vehicles, policies, superadmin
from app.routers.verify import router as verify_router
from app.routers.pdf_router import router as pdf_router

# Create tables on first start (Alembic is used for later schema changes)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TempCover Insurance API",
    description="Short-term car insurance platform API",
    version="1.0.0",
)

# Uploaded static documents (policy wording etc.)
docs_dir = os.path.join(settings.STATIC_DIR, "docs")
os.makedirs(docs_dir, exist_ok=True)
app.mount("/static/docs", StaticFiles(directory=docs_dir), name="static_docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
app.include_router(drivers.router,    prefix="/api/drivers",    tags=["Drivers"])
app.include_router(vehicles.router,   prefix="/api/vehicles",   tags=["Vehicles"])
app.include_router(policies.router,   prefix="/api/policies",   tags=["Policies"])
app.include_router(superadmin.router, prefix="/api/superadmin", tags=["Super Admin"])
app.include_router(pdf_router)
app.include_router(verify_router, prefix="/api/verify", tags=["Verify"])


@app.get("/")
def root():
    return {"status": "TempCover API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
