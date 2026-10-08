from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import new_id, str_enum, utcnow
from app.models.enums import ResponseStatus


class AnswerChoice(Base):
    """Join table: which options were picked for a multiple_choice / dropdown answer."""

    __tablename__ = "answer_choices"
    # The database cascade may already have removed the row when the ORM goes to delete it.
    __mapper_args__ = {"confirm_deleted_rows": False}

    answer_id: Mapped[str] = mapped_column(
        ForeignKey("answers.id", ondelete="CASCADE"), primary_key=True
    )
    option_id: Mapped[str] = mapped_column(
        ForeignKey("question_options.id", ondelete="CASCADE"), primary_key=True
    )


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (UniqueConstraint("response_id", "question_id"),)
    __mapper_args__ = {"confirm_deleted_rows": False}

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    response_id: Mapped[str] = mapped_column(ForeignKey("responses.id", ondelete="CASCADE"))
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    text_value: Mapped[str | None] = mapped_column(String)
    number_value: Mapped[float | None] = mapped_column(Float)
    boolean_value: Mapped[bool | None] = mapped_column(Boolean)

    response: Mapped["Response"] = relationship(back_populates="answers")
    choices: Mapped[list[AnswerChoice]] = relationship(
        cascade="all, delete-orphan", passive_deletes=True
    )


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (Index("ix_responses_form_submitted", "form_id", "submitted_at"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.id", ondelete="CASCADE"))
    status: Mapped[ResponseStatus] = mapped_column(
        str_enum(ResponseStatus), default=ResponseStatus.COMPLETED
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    user_agent: Mapped[str | None] = mapped_column(String)

    form: Mapped["Form"] = relationship(back_populates="responses")  # noqa: F821
    answers: Mapped[list[Answer]] = relationship(
        back_populates="response", cascade="all, delete-orphan", passive_deletes=True
    )
