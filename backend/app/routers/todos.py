"""/api/todos のルータ。

ここが扱うのは HTTP の入出力（ステータスコード・404 判定）だけ。
永続化は crud に委ね、レスポンスは必ず TodoRead を通してテーブルモデルを直接返さない。
"""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session

from app import crud
from app.db import SessionDep
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])

# HTTPException で送出する 404 は自動では OpenAPI に載らないため、明示して /docs に出す
NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"description": "Todo が見つかりません"}}


def _get_or_404(session: Session, todo_id: int) -> Todo:
    """1 件取得し、なければ 404 を送出する。"""
    todo = crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} が見つかりません",
        )
    return todo


@router.get("", response_model=list[TodoRead])
def list_todos(session: SessionDep) -> list[Todo]:
    """一覧取得。"""
    return crud.list_todos(session)


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, session: SessionDep) -> Todo:
    """作成。"""
    return crud.create_todo(session, data)


@router.get("/{todo_id}", response_model=TodoRead, responses=NOT_FOUND_RESPONSE)
def get_todo(todo_id: int, session: SessionDep) -> Todo:
    """単体取得。"""
    return _get_or_404(session, todo_id)


@router.patch("/{todo_id}", response_model=TodoRead, responses=NOT_FOUND_RESPONSE)
def update_todo(todo_id: int, data: TodoUpdate, session: SessionDep) -> Todo:
    """部分更新。"""
    todo = _get_or_404(session, todo_id)
    return crud.update_todo(session, todo, data)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND_RESPONSE,
)
def delete_todo(todo_id: int, session: SessionDep) -> None:
    """削除。"""
    todo = _get_or_404(session, todo_id)
    crud.delete_todo(session, todo)
