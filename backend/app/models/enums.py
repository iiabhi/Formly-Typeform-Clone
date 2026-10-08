from enum import StrEnum


class QuestionType(StrEnum):
    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    MULTIPLE_CHOICE = "multiple_choice"
    DROPDOWN = "dropdown"
    EMAIL = "email"
    NUMBER = "number"
    YES_NO = "yes_no"
    RATING = "rating"


# Types whose answers reference rows in question_options.
CHOICE_TYPES = frozenset({QuestionType.MULTIPLE_CHOICE, QuestionType.DROPDOWN})


class FormStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class ResponseStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
