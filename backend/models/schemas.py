"""Pydantic schemas for API responses."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


# ---- Knowledge Base ----

class KnowledgeItem(BaseModel):
    """A single knowledge entry extracted from training datasets."""
    id: str
    source: str  # Dataset name: fineweb-edu, qvac-genesis, studychat
    topic: str   # AI/ML/CS topic category
    title: str
    content: str
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    tags: list[str] = []
    url: Optional[str] = None


class KnowledgeQuery(BaseModel):
    query: str
    topic: Optional[str] = None
    limit: int = 10


class KnowledgeResponse(BaseModel):
    results: list[KnowledgeItem]
    total: int


# ---- Assessment ----

class AssessmentQuestion(BaseModel):
    """Assessment question generated from dataset content."""
    id: str
    question: str
    options: list[str]
    correct_answer: int
    explanation: str
    topic: str
    difficulty: str


class AssessmentQuestionPublic(BaseModel):
    """Assessment question for public API (without correct_answer)."""
    id: str
    question: str
    options: list[str]
    topic: str
    difficulty: str


class AssessmentSubmit(BaseModel):
    answers: list[int]


class AssessmentResult(BaseModel):
    score: int
    total: int
    level: str
    strengths: list[str]
    weaknesses: list[str]
    recommended_direction: str


# ---- Course ----

class CourseItem(BaseModel):
    """Course extracted from training data."""
    id: str
    title: str
    description: str
    topic: str
    difficulty: str
    estimated_hours: int
    source: str
    chapters: list[ChapterItem] = []
    # Enriched display fields
    coverImg: str = ""
    lessons: int = 0
    category: str = ""
    isFree: bool = True
    progress: int = 0
    duration: int = 0
    enTitle: str = ""
    enDescription: str = ""


class ChapterItem(BaseModel):
    id: str
    title: str
    content_summary: str
    duration_minutes: int


# ---- Project ----

class ProjectItem(BaseModel):
    """Project extracted from training data."""
    model_config = {"populate_by_name": True}
    id: str
    title: str
    description: str
    tech_stack: list[str] = Field(alias="techStack", default=[])
    difficulty: str
    estimated_hours: int = Field(alias="estimatedHours", default=0)
    topics_covered: list[str]
    source: str
    # Enriched display fields
    coverImg: str = ""
    stepCount: int = 0
    status: str = "available"
    progress: int = 0
    isFree: bool = True
    price: int = 0


# ---- Learning Path ----

class LearningPathNode(BaseModel):
    model_config = {"populate_by_name": True}
    id: str
    title: str
    type: str  # course, project, quiz
    items: list[str] = Field(default=[])
    # Enriched display fields
    status: str = "locked"
    progress: int = 0
    courseId: Optional[str] = None


class LearningPathItem(BaseModel):
    model_config = {"populate_by_name": True}
    id: str
    direction: str
    title: str
    nodes: list[LearningPathNode]
    total_weeks: int = Field(alias="totalWeeks", default=0)
    # Enriched display fields
    currentWeek: int = 0
    createdAt: str = ""


# ---- User Data ----

class AbilityReport(BaseModel):
    """User ability assessment report."""
    overallScore: int
    level: str
    dimensions: list[dict]
    strengths: list[str]
    weaknesses: list[str]
    recommendedDirection: str
    estimatedHours: int


class LearningRecord(BaseModel):
    """A single learning record entry."""
    date: str
    duration: int
    lessonsCompleted: int
    exercisesDone: int


class JobMatchingResult(BaseModel):
    """Job market matching result for the user."""
    jobTitle: str
    company: str
    matchScore: int
    requiredSkills: list[dict]
    gapSkills: list[str]
    recommendedCourses: list[str]
    recommendedProjects: list[str]


class LearningStats(BaseModel):
    """Overall learning statistics."""
    learningDays: int
    totalHours: int
    completedProjects: int
    completedLessons: int


# ---- Video ----

class VideoQuality(BaseModel):
    resolution: str = ""
    fps: int = 0
    audio: str = ""
    watermark: str = ""


class VideoItem(BaseModel):
    """Video item from course materials."""
    id: str
    title: str
    subtitle: str | None = None
    description: str
    coreInfo: list[str] | None = None
    narrative: str | None = None
    visual: str | None = None
    quality: VideoQuality | None = None
    url: str
    coverUrl: str
    duration: int
    chapter: str
    courseId: str
    completed: bool = False  # 用户是否已确认看完本视频（来自 video_progress.json）