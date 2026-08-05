"""
FastAPI Backend for AI Talent Training Mini-Program.

Provides APIs for:
- Knowledge base search (from FineWeb-Edu, QVAC Genesis, StudyChat)
- AI ability assessment
- Courses, projects, and learning paths

Usage:
    pip install -r backend/requirements.txt
    python -m backend.data_pipeline.download   # Download datasets
    python -m backend.data_pipeline.preprocess  # Process into knowledge base
    uvicorn backend.main:app --reload           # Start API server
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from config import CORS_ORIGINS, CORS_ORIGIN_REGEX, HOST, PORT
from routers import knowledge, assessment, courses, projects, learning_paths, ai

app = FastAPI(
    title="AI Talent Training API",
    description="Backend API for the AI Talent Training Mini-Program. "
                "Powered by FineWeb-Edu, QVAC Genesis, and StudyChat datasets.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug: log Origin header of all requests
@app.middleware("http")
async def log_origin(request: Request, call_next):
    origin = request.headers.get("origin", "NONE")
    logging.info(f"Request: {request.method} {request.url.path} Origin={origin}")
    response = await call_next(request)
    return response

# Register routers
app.include_router(knowledge.router)
app.include_router(assessment.router)
app.include_router(courses.router)
app.include_router(projects.router)
app.include_router(learning_paths.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    return {
        "name": "AI Talent Training API",
        "version": "1.0.0",
        "datasets": ["FineWeb-Edu", "QVAC Genesis", "StudyChat"],
        "endpoints": {
            "knowledge": "/api/knowledge/",
            "assessment": "/api/assessment/",
            "courses": "/api/courses/",
            "projects": "/api/projects/",
            "learning_paths": "/api/learning-paths/",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)