import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Answer,
    AnswerChoice,
    Form,
    FormStatus,
    Question,
    QuestionOption,
    QuestionType,
    Response,
    User,
)


def make_form(db: Session, slug: str = "abc123") -> Form:
    user = db.get(User, 1) or User(id=1, name="Alex", email="alex@example.com")
    form = Form(owner=user, slug=slug)
    db.add(form)
    db.commit()
    return form


def count(db: Session, model: type) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


def make_response_tree(db: Session) -> Form:
    """A form with one choice question, two options and one response that picked one."""
    form = make_form(db)
    question = Question(
        type=QuestionType.MULTIPLE_CHOICE,
        title="Pick",
        position=0,
        options=[QuestionOption(label="A", position=0), QuestionOption(label="B", position=1)],
    )
    form.questions.append(question)
    db.flush()
    answer = Answer(
        question_id=question.id, choices=[AnswerChoice(option_id=question.options[0].id)]
    )
    form.responses.append(Response(answers=[answer]))
    db.commit()
    return form


def test_defaults(db: Session) -> None:
    form = make_form(db)
    assert form.status == FormStatus.DRAFT
    assert form.theme["accent"] == "#0445AF"
    assert form.thank_you_title


def test_deleting_form_cascades_to_everything(db: Session) -> None:
    form = make_response_tree(db)
    db.delete(form)
    db.commit()
    for model in (Question, QuestionOption, Response, Answer, AnswerChoice):
        assert count(db, model) == 0


def test_deleting_question_cascades_to_options_and_answers(db: Session) -> None:
    form = make_response_tree(db)
    db.delete(form.questions[0])
    db.commit()
    assert count(db, QuestionOption) == 0
    assert count(db, Answer) == 0
    assert count(db, AnswerChoice) == 0
    assert count(db, Response) == 1


def test_deleting_option_cascades_to_answer_choices(db: Session) -> None:
    form = make_response_tree(db)
    db.delete(form.questions[0].options[0])
    db.commit()
    assert count(db, AnswerChoice) == 0
    assert count(db, Answer) == 1


def test_deleting_user_cascades_to_forms(db: Session) -> None:
    make_response_tree(db)
    db.delete(db.get(User, 1))
    db.commit()
    assert count(db, Form) == 0


def test_slug_must_be_unique(db: Session) -> None:
    make_form(db, slug="same")
    db.add(Form(owner_id=1, slug="same"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_user_email_must_be_unique(db: Session) -> None:
    db.add_all([User(name="A", email="x@example.com"), User(name="B", email="x@example.com")])
    with pytest.raises(IntegrityError):
        db.commit()


def test_one_answer_per_question_per_response(db: Session) -> None:
    form = make_response_tree(db)
    response = form.responses[0]
    db.add(Answer(response_id=response.id, question_id=form.questions[0].id))
    with pytest.raises(IntegrityError):
        db.commit()


def test_check_constraint_rejects_bad_status(db: Session) -> None:
    make_form(db)
    with pytest.raises(IntegrityError):
        db.execute(text("UPDATE forms SET status = 'archived'"))


def test_foreign_keys_are_enforced(db: Session) -> None:
    db.add(Form(owner_id=999, slug="orphan"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_options_come_back_ordered_by_position(db: Session) -> None:
    form = make_form(db)
    question = Question(
        type=QuestionType.DROPDOWN,
        title="Pick",
        position=0,
        options=[
            QuestionOption(label=label, position=pos)
            for label, pos in [("third", 2), ("first", 0), ("second", 1)]
        ],
    )
    form.questions.append(question)
    db.commit()
    db.expire_all()
    assert [o.label for o in db.get(Question, question.id).options] == ["first", "second", "third"]


def test_questions_come_back_ordered_by_position(db: Session) -> None:
    form = make_form(db)
    for title, pos in [("c", 2), ("a", 0), ("b", 1)]:
        form.questions.append(Question(type=QuestionType.SHORT_TEXT, title=title, position=pos))
    db.commit()
    db.expire_all()
    assert [q.title for q in db.get(Form, form.id).questions] == ["a", "b", "c"]
