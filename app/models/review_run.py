from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ReviewRun(Base):
    __tablename__ = 'review_runs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    repository: Mapped[str] = mapped_column(String(255), index=True)
    pr_number: Mapped[int] = mapped_column(Integer, index=True)
    head_sha: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default='pending')
    review_json: Mapped[str] = mapped_column(Text, default='{}')
    summary: Mapped[str] = mapped_column(Text, default='')
    comments_posted: Mapped[int] = mapped_column(Integer, default=0)
    used_memory: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
