"""FastAPI アプリのエントリポイント。

起動: uv run uvicorn app.main:app --reload
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

# SQLModel.metadata にテーブル定義を登録させるために読み込む（参照はしない）
from app import models  # noqa: F401
from app.db import create_db_and_tables
from app.routers import todos


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """起動時にテーブルを作成する。"""
    create_db_and_tables()
    yield


app = FastAPI(title="TODO API", version="0.1.0", lifespan=lifespan)

# CLAUDE.md の API 契約どおり /api 配下に生やす
app.include_router(todos.router, prefix="/api")
