from typing import Literal

from pydantic import BaseModel, Field


class ReviewComment(BaseModel):
    path: str
    line: int = Field(ge=1)
    severity: Literal['low', 'medium', 'high'] = 'medium'
    category: Literal['bug', 'security', 'performance', 'readability', 'test', 'design'] = 'bug'
    title: str
    body: str
    suggestion: str | None = None


class ReviewResponse(BaseModel):
    summary: str
    verdict: Literal['approve', 'comment', 'request_changes'] = 'comment'
    comments: list[ReviewComment] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    memory_used: bool = False
