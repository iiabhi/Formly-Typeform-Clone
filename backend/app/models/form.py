from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import new_id, str_enum, utcnow
from app.models.enums import FormStatus
from app.models.question import Question
from app.models.response import Response
from app.models.user import User

DEFAULT_THEME: dict[str, str] = {
    "accent": "#0445AF",
    "background": "#FFFFFF",
    "question_color": "#262627",
    "font": "Inter",
}


class Form(Base):
    __tablename__ = "forms"
    __table_args__ = (Index("ix_forms_owner_updated", "owner_id", "updated_at"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String, default="My new form")
    slug: Mapped[str] = mapped_column(String, unique=True)
    status: Mapped[FormStatus] = mapped_column(str_enum(FormStatus), default=FormStatus.DRAFT)
    theme: Mapped[dict[str, Any]] = mapped_column(JSON, default=lambda: dict(DEFAULT_THEME))
    thank_you_title: Mapped[str] = mapped_column(String, default="Thanks for completing this form")
    thank_you_description: Mapped[str | None] = mapped_column(String)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    owner: Mapped[User] = relationship(back_populates="forms")
    questions: Mapped[list[Question]] = relationship(
        back_populates="form",
        order_by=Question.position,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    responses: Mapped[list[Response]] = relationship(
        back_populates="form", cascade="all, delete-orphan", passive_deletes=True
    )
