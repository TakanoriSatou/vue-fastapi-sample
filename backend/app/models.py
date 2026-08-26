"""SQLModel のテーブルモデル定義。"""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    """現在時刻（UTC）を返す。"""
    return datetime.now(UTC)


class Todo(SQLModel, table=True):
    """todo テーブル。

    created_at は UTC で保存するが、SQLite はタイムゾーンを保持しないため、
    DB から読み戻した値は naive な datetime になる。
    """

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=_now)
