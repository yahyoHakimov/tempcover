"""
TempCover Insurance Platform
FastAPI application entry point
"""

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routers import auth, drivers, vehicles, policies, superadmin
from app.routers.verify import router as verify_router
from app.routers.pdf_router import router as pdf_router
from app.services import lifecycle

# Schema is managed by Alembic (`alembic upgrade head`); create_all only fills in brand-new tables.
Base.metadata.create_all(bind=engine)


async def _lifecycle_loop() -> None:
    """pending→active, expiry, driver reminders and the agent digest — see services/lifecycle.py"""
    while True:
        try:
            stats = await asyncio.to_thread(lifecycle.tick)
            if any(stats.values()):
                print(f"[lifecycle] {stats}")
        except Exception as e:  # never let a failed tick kill the loop
            print(f"[lifecycle] tick failed: {e}")
        await asyncio.sleep(settings.LIFECYCLE_TICK_SECONDS)


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(_lifecycle_loop()) if settings.LIFECYCLE_TICK_SECONDS > 0 else None
    yield
    if task:
        task.cancel()


app = FastAPI(
    title="TempCover Insurance API",
    description="Short-term car insurance platform API",
    version="1.1.0",
    lifespan=lifespan,
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
