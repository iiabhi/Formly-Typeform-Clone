from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import new_id, str_enum, utcnow
from app.models.enums import QuestionType


class QuestionOption(Base):
    __tablename__ = "question_options"
    __table_args__ = (Index("ix_options_question_position", "question_id", "position"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String)
    position: Mapped[int]

    question: Mapped["Question"] = relationship(back_populates="options")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (Index("ix_questions_form_position", "form_id", "position"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.id", ondelete="CASCADE"))
    type: Mapped[QuestionType] = mapped_column(str_enum(QuestionType))
    title: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str | None] = mapped_column(String)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int]
    properties: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    form: Mapped["Form"] = relationship(back_populates="questions")  # noqa: F821
    options: Mapped[list[QuestionOption]] = relationship(
        back_populates="question",
        order_by=QuestionOption.position,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
