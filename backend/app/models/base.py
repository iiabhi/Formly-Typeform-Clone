import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Enum


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(UTC)


def str_enum(enum_cls: type[StrEnum]) -> Enum:
    """Store a StrEnum as TEXT with a CHECK constraint (SQLite has no native enum)."""
    return Enum(
        enum_cls,
        native_enum=False,
        create_constraint=True,
        length=32,
        values_callable=lambda e: [member.value for member in e],
    )
