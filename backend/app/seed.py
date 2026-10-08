"""Idempotent demo data: `python -m app.seed` wipes the database and reseeds it."""

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.db import Base, SessionLocal, engine
from app.models import (
    Answer,
    AnswerChoice,
    Form,
    FormStatus,
    Question,
    QuestionOption,
    QuestionType,
    Response,
    ResponseStatus,
    User,
)

Generator = Callable[[random.Random, list[str]], Any]

NAMES = [
    "Maya Patel",
    "Liam Chen",
    "Sofia Rossi",
    "Noah Williams",
    "Aisha Khan",
    "Lucas Meyer",
    "Emma Johansson",
    "Omar Hassan",
    "Zoe Martin",
    "Ravi Sharma",
    "Chloe Dubois",
    "Ben Carter",
]
FEEDBACK = [
    "Love the clean design, very easy to use.",
    "Would like more export options.",
    "Support answered within minutes, great experience.",
    "The mobile experience could be smoother.",
    "Pricing feels fair for what you get.",
    "Please add more integrations!",
    "Setup took five minutes. Impressive.",
]
IDEAS = ["Dark mode", "Offline support", "Team workspaces", "Public roadmap"]


def pick(rng: random.Random, labels: list[str]) -> str:
    return rng.choice(labels)


def pick_many(rng: random.Random, labels: list[str]) -> list[str]:
    return rng.sample(labels, rng.randint(1, min(3, len(labels))))


def email_for(rng: random.Random, _labels: list[str]) -> str:
    return rng.choice(NAMES).lower().replace(" ", ".") + str(rng.randint(1, 99)) + "@example.com"


@dataclass
class QSpec:
    type: QuestionType
    title: str
    gen: Generator
    required: bool = False
    description: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    options: list[str] = field(default_factory=list)
    skip_rate: float = 0.0  # chance an optional question is left unanswered


def create_form(
    db: Session, title: str, slug: str, status: FormStatus, thank_you: str, specs: list[QSpec]
) -> tuple[Form, list[tuple[Question, QSpec]]]:
    form = Form(
        owner_id=1,
        title=title,
        slug=slug,
        status=status,
        thank_you_title=thank_you,
        thank_you_description="We really appreciate your time.",
        published_at=datetime.now(UTC) if status == FormStatus.PUBLISHED else None,
    )
    pairs: list[tuple[Question, QSpec]] = []
    for position, spec in enumerate(specs):
        question = Question(
            type=spec.type,
            title=spec.title,
            description=spec.description,
            required=spec.required,
            position=position,
            properties=spec.properties,
            options=[
                QuestionOption(label=label, position=i) for i, label in enumerate(spec.options)
            ],
        )
        form.questions.append(question)
        pairs.append((question, spec))
    db.add(form)
    db.flush()
    return form, pairs


def store_answer(response: Response, question: Question, value: Any) -> None:
    answer = Answer(question_id=question.id)
    if question.type in (QuestionType.SHORT_TEXT, QuestionType.LONG_TEXT, QuestionType.EMAIL):
        answer.text_value = value
    elif question.type in (QuestionType.NUMBER, QuestionType.RATING):
        answer.number_value = float(value)
    elif question.type == QuestionType.YES_NO:
        answer.boolean_value = value
    else:
        by_label = {o.label: o.id for o in question.options}
        labels = value if isinstance(value, list) else [value]
        answer.choices = [AnswerChoice(option_id=by_label[label]) for label in labels]
    response.answers.append(answer)


def add_responses(
    db: Session, form: Form, pairs: list[tuple[Question, QSpec]], count: int, rng: random.Random
) -> None:
    now = datetime.now(UTC)
    for _ in range(count):
        started = now - timedelta(days=rng.uniform(0, 30), minutes=rng.randint(0, 600))
        response = Response(
            form_id=form.id,
            status=ResponseStatus.COMPLETED,
            started_at=started,
            submitted_at=started + timedelta(seconds=rng.randint(40, 400)),
            user_agent="Mozilla/5.0 (seed)",
        )
        for question, spec in pairs:
            if not spec.required and rng.random() < spec.skip_rate:
                continue
            store_answer(response, question, spec.gen(rng, spec.options))
        db.add(response)


def feedback_specs() -> list[QSpec]:
    return [
        QSpec(
            QuestionType.SHORT_TEXT,
            "What's your name?",
            lambda r, _: r.choice(NAMES),
            required=True,
            properties={"placeholder": "Jane Doe"},
        ),
        QSpec(QuestionType.EMAIL, "What's your email address?", email_for, required=True),
        QSpec(
            QuestionType.MULTIPLE_CHOICE,
            "How did you hear about us?",
            pick,
            description="Pick one.",
            properties={"allow_multiple": False, "randomize": False},
            options=["Social media", "A friend", "Search engine", "Other"],
            required=True,
        ),
        QSpec(
            QuestionType.MULTIPLE_CHOICE,
            "Which features do you use?",
            pick_many,
            description="Choose as many as you like.",
            properties={"allow_multiple": True, "randomize": False},
            options=["Form builder", "Analytics", "Integrations", "Themes"],
            skip_rate=0.15,
        ),
        QSpec(
            QuestionType.DROPDOWN,
            "Which region are you in?",
            pick,
            properties={"randomize": False},
            options=["North America", "Europe", "Asia", "South America", "Africa", "Oceania"],
        ),
        QSpec(
            QuestionType.RATING,
            "How would you rate our product?",
            lambda r, _: r.choices([1, 2, 3, 4, 5], weights=[1, 2, 4, 8, 6])[0],
            required=True,
            properties={"steps": 5, "shape": "star"},
        ),
        QSpec(
            QuestionType.YES_NO,
            "Would you recommend us to a friend?",
            lambda r, _: r.random() < 0.75,
            required=True,
        ),
        QSpec(
            QuestionType.NUMBER,
            "How many people are on your team?",
            lambda r, _: r.choice([1, 2, 3, 5, 8, 12, 25, 40]),
            properties={"min": 1, "max": 1000},
            skip_rate=0.2,
        ),
        QSpec(
            QuestionType.LONG_TEXT,
            "Any other feedback?",
            lambda r, _: r.choice(FEEDBACK),
            description="Tell us anything on your mind.",
            skip_rate=0.4,
        ),
    ]


def event_specs() -> list[QSpec]:
    return [
        QSpec(QuestionType.SHORT_TEXT, "Full name", lambda r, _: r.choice(NAMES), required=True),
        QSpec(QuestionType.EMAIL, "Email", email_for, required=True),
        QSpec(
            QuestionType.MULTIPLE_CHOICE,
            "Which session will you attend?",
            pick,
            properties={"allow_multiple": False, "randomize": False},
            required=True,
            options=["Keynote", "Design workshop", "Engineering deep dive"],
        ),
        QSpec(
            QuestionType.DROPDOWN,
            "T-shirt size",
            pick,
            properties={"randomize": False},
            options=["S", "M", "L", "XL"],
        ),
        QSpec(
            QuestionType.YES_NO,
            "Do you have any dietary restrictions?",
            lambda r, _: r.random() < 0.3,
            required=True,
        ),
        QSpec(
            QuestionType.NUMBER,
            "How many guests are you bringing?",
            lambda r, _: r.randint(0, 3),
            properties={"min": 0, "max": 5},
            skip_rate=0.3,
        ),
    ]


def ideas_specs() -> list[QSpec]:
    return [
        QSpec(
            QuestionType.SHORT_TEXT,
            "What should we build next?",
            lambda r, _: r.choice(IDEAS),
            required=True,
        ),
        QSpec(QuestionType.LONG_TEXT, "Why would it help you?", lambda r, _: r.choice(FEEDBACK)),
        QSpec(
            QuestionType.RATING,
            "How important is it?",
            lambda r, _: r.randint(1, 5),
            properties={"steps": 5, "shape": "star"},
        ),
    ]


def seed(db: Session) -> None:
    rng = random.Random(42)
    db.add(User(id=1, name="Alex Creator", email="alex@example.com"))
    db.flush()
    fb, fb_pairs = create_form(
        db,
        "Customer Feedback Survey",
        "customer-feedback",
        FormStatus.PUBLISHED,
        "Thanks for your feedback!",
        feedback_specs(),
    )
    add_responses(db, fb, fb_pairs, 25, rng)
    ev, ev_pairs = create_form(
        db,
        "Event Registration",
        "event-registration",
        FormStatus.PUBLISHED,
        "You're registered!",
        event_specs(),
    )
    add_responses(db, ev, ev_pairs, 12, rng)
    create_form(
        db,
        "Product Ideas",
        "product-ideas",
        FormStatus.DRAFT,
        "Thanks for the idea!",
        ideas_specs(),
    )
    db.commit()


def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    print("Seeded: 3 forms (2 published), 37 responses.")


if __name__ == "__main__":
    main()
