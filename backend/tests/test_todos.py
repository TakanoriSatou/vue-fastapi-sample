"""/api/todos の API テスト。

承認済みの API 契約（CLAUDE.md）どおりに振る舞うかを検証する。
"""

import pytest
from fastapi.testclient import TestClient


def _create(client: TestClient, title: str) -> dict:
    """1 件作成して、そのレスポンス body を返すヘルパ。"""
    res = client.post("/api/todos", json={"title": title})
    assert res.status_code == 201
    return res.json()


def test_list_is_empty_initially(client: TestClient) -> None:
    """初期状態の一覧は空配列。"""
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert res.json() == []


def test_create_returns_201_with_body(client: TestClient) -> None:
    """作成は 201 を返し、body に採番済みの全項目が入る。"""
    res = client.post("/api/todos", json={"title": "牛乳を買う"})

    assert res.status_code == 201
    body = res.json()
    assert body["id"] > 0
    assert body["title"] == "牛乳を買う"
    assert body["completed"] is False
    assert body["created_at"]
    # テーブルモデルの項目がそのまま漏れていないこと
    assert set(body) == {"id", "title", "completed", "created_at"}


def test_created_todo_appears_in_list(client: TestClient) -> None:
    """作成した内容が一覧に現れる。"""
    created = _create(client, "牛乳を買う")

    res = client.get("/api/todos")
    assert res.status_code == 200
    assert res.json() == [created]


def test_list_is_ordered_by_creation(client: TestClient) -> None:
    """一覧は作成順に並ぶ。"""
    for title in ("1 番目", "2 番目", "3 番目"):
        _create(client, title)

    titles = [todo["title"] for todo in client.get("/api/todos").json()]
    assert titles == ["1 番目", "2 番目", "3 番目"]


def test_get_returns_single_todo(client: TestClient) -> None:
    """単体取得は作成時と同じ内容を返す。"""
    created = _create(client, "牛乳を買う")

    res = client.get(f"/api/todos/{created['id']}")
    assert res.status_code == 200
    assert res.json() == created


def test_patch_marks_completed(client: TestClient) -> None:
    """PATCH で completed を true にできる。"""
    created = _create(client, "牛乳を買う")

    res = client.patch(f"/api/todos/{created['id']}", json={"completed": True})
    assert res.status_code == 200
    assert res.json()["completed"] is True

    # 取得し直しても保持されている
    assert client.get(f"/api/todos/{created['id']}").json()["completed"] is True


def test_patch_updates_title_only(client: TestClient) -> None:
    """title だけ渡したとき、completed は元の値のまま。"""
    created = _create(client, "牛乳を買う")
    client.patch(f"/api/todos/{created['id']}", json={"completed": True})

    res = client.patch(f"/api/todos/{created['id']}", json={"title": "豆乳を買う"})
    assert res.status_code == 200
    assert res.json()["title"] == "豆乳を買う"
    assert res.json()["completed"] is True


def test_patch_ignores_explicit_null(client: TestClient) -> None:
    """明示的な null は「変更しない」として扱い、NOT NULL 制約を壊さない。"""
    created = _create(client, "牛乳を買う")

    res = client.patch(f"/api/todos/{created['id']}", json={"title": None})
    assert res.status_code == 200
    assert res.json()["title"] == "牛乳を買う"


def test_delete_then_get_returns_404(client: TestClient) -> None:
    """削除は 204 を返し、以降その id は 404 になる。"""
    created = _create(client, "牛乳を買う")

    res = client.delete(f"/api/todos/{created['id']}")
    assert res.status_code == 204

    assert client.get(f"/api/todos/{created['id']}").status_code == 404
    assert client.get("/api/todos").json() == []


@pytest.mark.parametrize(
    ("method", "payload"),
    [
        ("get", None),
        ("patch", {"completed": True}),
        ("delete", None),
    ],
)
def test_missing_todo_returns_404(client: TestClient, method: str, payload: dict | None) -> None:
    """存在しない id への操作はいずれも 404。"""
    kwargs = {"json": payload} if payload is not None else {}
    res = getattr(client, method)("/api/todos/999", **kwargs)
    assert res.status_code == 404


@pytest.mark.parametrize("payload", [{}, {"title": ""}, {"title": None}])
def test_create_rejects_invalid_title(client: TestClient, payload: dict) -> None:
    """title 未指定・空文字・null は 422 で弾く。"""
    res = client.post("/api/todos", json=payload)
    assert res.status_code == 422
