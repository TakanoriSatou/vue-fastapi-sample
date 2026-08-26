"""todo の永続化操作。

HTTP の関心事（404 を返す、ステータスコードを決める等）はここに持ち込まない。
「見つからない」は例外ではなく None で表現し、その解釈はルータ側に任せる。
"""

from sqlmodel import Session, select

from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate


def list_todos(session: Session) -> list[Todo]:
    """全件を作成順で返す。created_at が同値でも順序が揺れないよう id も見る。"""
    statement = select(Todo).order_by(Todo.created_at, Todo.id)
    return list(session.exec(statement).all())


def get_todo(session: Session, todo_id: int) -> Todo | None:
    """1 件取得。見つからなければ None を返す。"""
    return session.get(Todo, todo_id)


def create_todo(session: Session, data: TodoCreate) -> Todo:
    """作成して、採番済みの行を返す。"""
    todo = Todo(title=data.title)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def update_todo(session: Session, todo: Todo, data: TodoUpdate) -> Todo:
    """部分更新。リクエストに現れなかった項目は触らない。

    exclude_unset で「未指定」を、exclude_none で「明示的な null」を弾く。
    title / completed はいずれも NOT NULL なので、null を書き込ませない。
    """
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in changes.items():
        setattr(todo, key, value)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def delete_todo(session: Session, todo: Todo) -> None:
    """削除する。"""
    session.delete(todo)
    session.commit()
