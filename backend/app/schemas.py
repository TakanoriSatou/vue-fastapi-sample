"""リクエスト / レスポンス用スキーマ。

テーブルモデル（models.Todo）をそのまま外に出さないため、ここで入出力用の型を分けて定義する。
table=True を付けていないので、これらは通常の Pydantic モデルとして扱われる。
"""

from datetime import datetime

from sqlmodel import Field, SQLModel


class TodoCreate(SQLModel):
    """作成リクエスト。"""

    title: str = Field(min_length=1, max_length=200)


class TodoUpdate(SQLModel):
    """部分更新リクエスト。

    未指定の項目は変更しない。title だけ / completed だけの更新を許す。
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    completed: bool | None = Field(default=None)


class TodoRead(SQLModel):
    """レスポンス。"""

    id: int
    title: str
    completed: bool
    created_at: datetime
