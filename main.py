"""Запуск: uvicorn main:app --reload --port 8000 → открыть http://localhost:8000"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers.chat import router as chat_router
from app.routers.upload import router as upload_router
from app.routers.admin import router as admin_router

app = FastAPI(title="Reglament Assistant API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
                   allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(admin_router)

STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/admin", include_in_schema=False)
def admin_page():
    return FileResponse(STATIC / "admin.html")
