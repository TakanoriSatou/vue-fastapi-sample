"""テスト共通のフィクスチャ。

本物の backend/todo.db を汚さないため、DB をインメモリ SQLite に差し替える。
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """テストごとに空のインメモリ DB を用意する。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        # インメモリ DB は接続が切れると消える。StaticPool で単一接続を使い回す。
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """get_session をインメモリ DB へ差し替えた TestClient。"""

    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override

    # with 文で使うと lifespan が走り、本物の backend/todo.db が作られてしまうため使わない。
    # テスト用のテーブルは session フィクスチャ側で作成済み。
    yield TestClient(app)

    app.dependency_overrides.clear()
