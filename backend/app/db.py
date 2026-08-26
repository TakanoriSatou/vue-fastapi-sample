"""DB エンジンとセッションの提供。

セッションは必ず get_session（Depends 用）経由で受け取る。ルータ内で直接生成しない。
"""

from collections.abc import Generator
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# 実行時のカレントディレクトリに依存させないため、このファイルからの相対で解決する
DB_PATH = Path(__file__).resolve().parent.parent / "todo.db"

# check_same_thread=False は必須。FastAPI は同期エンドポイントをスレッドプールで動かすため、
# 接続を作ったスレッド以外から触られることがある。
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    """テーブルを作成する。アプリ起動時に一度だけ呼ぶ。"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """リクエストごとの DB セッションを提供する。"""
    with Session(engine) as session:
        yield session


# 各ルータはこの別名を型注釈に使う。
# Depends() を引数のデフォルト値に書くと Ruff の B008 に引っかかるため、Annotated 形式で持つ。
SessionDep = Annotated[Session, Depends(get_session)]
