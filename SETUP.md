# セットアップ計画

> **ステータス: 計画（未実行）／作成日 2026-08-26**
> 技術スタックは `CLAUDE.md` の「技術スタック」を正本とする。本書はそれを前提に、
> 何をどの順で実行し、各段でどう緑を確認するかだけを書く。
> 実行済みのフェーズは各節の冒頭に「実行済み: YYYY-MM-DD」を追記していく。

## 前提（実測値・2026-08-26 確認）

| ツール | 状態 |
|---|---|
| Node.js | v24.16.0（インストール済み） |
| npm | 11.13.0（インストール済み） |
| Python | 3.12.3（インストール済み） |
| uv | **未インストール** — Phase 1 で導入する |
| Docker | 29.7.2（インストール済みだが本プロジェクトでは使わない） |
| create-vue | 3.23.0（npm レジストリ上の最新。Phase 3 で取得） |

現状のディレクトリは `CLAUDE.md` / `SETUP.md` / `.gitignore` と、空の `frontend/` `backend/` のみ。
git は初期化済み（単一リポジトリ・`main` ブランチ）。

## 全体の流れ

```
Phase 0  git 初期化                   ← 完了（2026-08-26）
   ↓
Phase 1  uv の導入                    ← ユーザーの手動実行が必要
   ↓
Phase 2  backend: プロジェクト生成と依存追加
   ↓
Phase 3  backend: アプリ実装（DB / モデル / ルータ）
   ↓
Phase 4  backend: pytest
   ↓
Phase 5  frontend: プロジェクト生成
   ↓
Phase 6  frontend: 実装（型 / ストア / コンポーネント）
   ↓
Phase 7  結線（Vite dev proxy）と通し確認   ← ブラウザ確認はユーザー
   ↓
Phase 8  ドキュメント反映
```

backend を先に立ち上げる。フロントは叩く先が動いていないと確認できないため。

---

## Claude が実行できない作業（先に宣言）

以下はユーザーに手動実行を依頼する。Claude は**実行後の検証だけ**を引き受ける。

| # | 作業 | 依頼するコマンド / 操作 | Phase |
|---|---|---|---|
| 1 | uv のインストール | `! curl -LsSf https://astral.sh/uv/install.sh \| sh` | 1 |
| 2 | dev サーバの常駐起動 | `! cd backend && uv run uvicorn app.main:app --reload` 等 | 7 |
| 3 | ブラウザでの目視確認 | http://localhost:5173 を開いて CRUD を一巡 | 7 |

`! <command>` はこのセッション内で実行され、出力がそのまま会話に入る。

---

## Phase 0: git 初期化

**実行済み: 2026-08-26**

- `git init -b main` をリポジトリルートで実行。**フロント / バックを分けず単一リポジトリ**で管理する。
  （`init.defaultBranch` はグローバル未設定＝`master` だったため、この repo だけ `-b main` を明示。）
- ルートに `.gitignore` を配置。Python 側（`.venv/` `__pycache__/` `.pytest_cache/` `.ruff_cache/`）、
  Node 側（`node_modules/` `dist/`）、SQLite（`*.db`）、エディタ / OS 由来をまとめてカバーする。
- `frontend/` `backend/` は空のため git の追跡対象外。`.gitkeep` は**置かない** —
  Phase 5 の create-vue が「対象ディレクトリが空でない」と判断してしまうため。
  両ディレクトリは Phase 2 / Phase 5 で中身ができた時点で追跡される。

**ゲート**

```bash
git status --short      # CLAUDE.md / SETUP.md / .gitignore が未追跡として出ること
```

---

## Phase 1: uv の導入

**実行済み: 2026-08-26（uv 0.12.5 / uvx 0.12.5 を `~/.local/bin` に導入）**

公式インストーラで入れる。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- インストール先は `~/.local/bin`。**このディレクトリは既に PATH に入っている**
  （`claude` / `ctxray` 等が同居）ため、`source $HOME/.local/bin/env` や端末の開き直しは不要。
- `pip install uv` は選ばない — Ubuntu 24.04 のシステム Python は PEP 668 で保護されており
  `--break-system-packages` が必要になるため。
- Python 3.12.3 はインストール済みなので、uv に別バージョンを引かせる必要はない。

**ゲート**

```bash
uv --version    # バージョンが表示されること
```

---

## Phase 2: backend のプロジェクト生成と依存追加

**実行済み: 2026-08-26**

導入されたバージョン: fastapi 0.141.1 / sqlmodel 0.0.39（+ sqlalchemy 2.0.52）/
uvicorn 0.52.4 / pydantic 2.13.4 / pytest 9.1.1 / httpx 0.28.1 / ruff 0.16.4

```bash
cd backend
# pyproject.toml だけ作る。--vcs none でルート単一リポジトリに .git を増やさない
uv init --bare --python 3.12 --vcs none --no-workspace
uv add fastapi "uvicorn[standard]" sqlmodel
uv add --dev pytest httpx ruff
```

- `httpx` は FastAPI の `TestClient` が内部で使うため dev 依存に必須。
- `uv.lock` が生成される。`requirements.txt` は作らない。

`pyproject.toml` に Ruff と pytest の設定を追記する:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- `testpaths` は当初の計画にはなかったが、`uv run pytest` を引数なしで叩いたときに
  `.venv/` 配下まで走査させないために追加した。

`.gitignore` はルートのもので既にカバー済み（`backend/.gitignore` は作らない）。
`backend/` で追跡されるのは `pyproject.toml` と `uv.lock` のみ
（`.venv/` `.ruff_cache/` はルートの `.gitignore` で除外済みを確認）。

**ゲート**

```bash
ctxray capture -- uv run python -c "import fastapi, sqlmodel, uvicorn"
```

---

## Phase 3: backend のアプリ実装

**実行済み: 2026-08-26**

### ファイル構成（実績）

```
backend/
├── pyproject.toml
├── uv.lock
└── app/
    ├── __init__.py
    ├── main.py         # FastAPI インスタンス、ルータ登録、lifespan でのテーブル作成
    ├── db.py           # engine / get_session / SessionDep
    ├── models.py       # SQLModel テーブルモデル Todo
    ├── schemas.py      # TodoCreate / TodoUpdate / TodoRead
    ├── crud.py         # 永続化操作（HTTP の関心事を持たない）
    └── routers/
        ├── __init__.py
        └── todos.py    # /api/todos のルータ
```

### 各ファイルの責務

| ファイル | 内容 |
|---|---|
| `db.py` | `create_engine`、`get_session()`、`SessionDep` 型別名。DB パスは `__file__` 基準で解決 |
| `models.py` | `class Todo(SQLModel, table=True)` — `id` / `title` / `completed` / `created_at` |
| `schemas.py` | `TodoCreate` / `TodoUpdate`（両項目 Optional）/ `TodoRead`。いずれも `table=True` なし |
| `crud.py` | 一覧・取得・作成・更新・削除。「見つからない」は例外でなく `None` で返す |
| `routers/todos.py` | 5 エンドポイント。HTTP ステータスと 404 判定のみ担当 |
| `main.py` | `include_router(todos.router, prefix="/api")` と lifespan での `create_all` |

### 計画からの変更点（実装時の判断）

1. **`app/crud.py` を初回から作った**（計画では「初回は不要」としていた）。
   `CLAUDE.md` の「ルータ層にビジネスロジックを直書きしない」を素直に満たすため。
   結果としてルータは「404 を返すか否か」だけを判断する薄い層になった。
2. **`Depends()` を引数のデフォルト値に書かず、`SessionDep = Annotated[Session, Depends(get_session)]`
   を `db.py` に定義**した。デフォルト値形式は Ruff の `B008`（関数呼び出しをデフォルト引数にしない）
   と衝突するため。`select = [..., "B"]` を選んだ以上、こちらが筋。
3. **404 を `responses=` で明示**した。`HTTPException` で送出する 404 は OpenAPI に自動では載らず、
   `/docs` が承認済み契約と食い違うため。
4. `create_engine` に **`connect_args={"check_same_thread": False}`** を付けた。
   FastAPI は同期エンドポイントをスレッドプールで実行するため、これがないと SQLite が例外を投げる。

### 規約上の注意（`CLAUDE.md` より）

- テーブルモデルを直接レスポンスに返さず、`response_model=TodoRead` を指定する。
- `schemas.py` も `SQLModel`（`table=True` なし）で書けば Pydantic と兼用でき、二重定義の手間は小さい。
- DB セッションはルータ内で生成せず、必ず `SessionDep`（= `Depends`）経由で受け取る。

### 確認時の注意（ハマった点）

`app.include_router()` したルートは、**Starlette 1.6 系では `app.routes` に展開されない**
（`_IncludedRouter` として 1 要素で保持される）。ルート一覧を目視したいときは
`app.routes` を数えるのではなく `app.openapi()["paths"]` を見ること。

### API 契約（`CLAUDE.md` の承認済み契約を実装する）

| メソッド | パス | リクエスト | レスポンス |
|---|---|---|---|
| GET | `/api/todos` | — | `TodoRead[]` |
| POST | `/api/todos` | `TodoCreate` | `TodoRead`（201） |
| GET | `/api/todos/{id}` | — | `TodoRead`／404 |
| PATCH | `/api/todos/{id}` | `TodoUpdate` | `TodoRead`／404 |
| DELETE | `/api/todos/{id}` | — | 204／404 |

**ゲート**

```bash
ctxray capture -- uv run ruff check .          # All checks passed!
ctxray capture -- uv run ruff format --check . # 8 files already formatted
ctxray capture -- uv run python -c "from app.main import app; print(app.openapi()['paths'].keys())"
```

OpenAPI が承認済み契約と一致することまで確認する（実績）:

| メソッド | パス | responses |
|---|---|---|
| GET | `/api/todos` | 200 |
| POST | `/api/todos` | 201, 422 |
| GET | `/api/todos/{todo_id}` | 200, 404, 422 |
| PATCH | `/api/todos/{todo_id}` | 200, 404, 422 |
| DELETE | `/api/todos/{todo_id}` | 204, 404, 422 |

公開スキーマは `TodoCreate` / `TodoRead` / `TodoUpdate` の 3 つのみ。
テーブルモデル `Todo` が API 表面に漏れていないことの確認も兼ねる。

---

## Phase 4: backend のテスト

**実行済み: 2026-08-26（15 passed）**

`tests/conftest.py` と `tests/test_todos.py` を置いた。

- SQLite のインメモリ DB（`sqlite://` + `StaticPool`）を使い、`app.dependency_overrides` で
  `get_session` を差し替える。**本物の `todo.db` をテストで汚さない。**
- `StaticPool` は必須。インメモリ DB は接続が切れた時点で消えるため、単一接続を使い回す。

### テストケース（11 関数 / 15 ケース）

| # | 内容 |
|---|---|
| 1 | 空の一覧が `[]` を返す |
| 2 | 作成が 201 と body を返す（項目が契約どおり 4 つだけであることも検証） |
| 3 | 作成後に一覧へ現れる |
| 4 | 一覧が作成順に並ぶ |
| 5 | 単体取得が作成時と同じ内容を返す |
| 6 | PATCH で `completed` が true になり、取得し直しても保持される |
| 7 | `title` だけ渡したとき `completed` は元の値のまま |
| 8 | PATCH の明示的な `null` は「変更しない」扱い（計画外に追加） |
| 9 | DELETE が 204、以降その id は 404 |
| 10 | 存在しない id への GET / PATCH / DELETE が 404（parametrize 3 ケース） |
| 11 | POST の title 未指定 / 空文字 / null が 422（parametrize 3 ケース） |

### 計画からの変更点（実装時の判断）

1. **`tests/` に `TestClient` を `with` 文で使わない**。`with` は lifespan を起動し、
   `create_db_and_tables()` が**本物の `backend/todo.db` を作ってしまう**ため。
   テーブルは `session` フィクスチャ側で作成済みなので lifespan は不要。
   （テスト後に `todo.db` が生成されないことを実際に確認した。）
2. **`pyproject.toml` に `pythonpath = ["."]` を追加**。プロジェクトをパッケージとして
   インストールしていないため、これがないと `tests/` から `import app` できない。
3. **dev 依存を `httpx` から `httpx2` へ差し替えた**。Starlette 1.6 系の `TestClient` は
   `httpx2` を優先し、`httpx` だと `StarletteDeprecationWarning` を出す。
   推奨側へ寄せて警告を解消した（httpx2 2.12.0）。
4. ケース 8（明示的 `null`）を追加。`crud.update_todo` の `exclude_none=True` が効いていることの
   回帰テストとして必要と判断した。

**ゲート**

```bash
ctxray capture -- uv run pytest -q     # 15 passed、警告なし
ctxray capture -- uv run ruff check .
ctxray capture -- uv run ruff format --check .
```

落ちたら `ctxray capture` が保存したログのパスを grep する（再実行しない）。

---

## Phase 5: frontend のプロジェクト生成

`frontend/` は空なので、**リポジトリルートから**実行してプロジェクト名に `frontend` を指定する。

```bash
cd /home/t_satou/workspace/vue-fastapi-sample
npm create vue@latest
```

対話プロンプトでの選択（create-vue 3.23.0 想定）:

| 項目 | 選択 |
|---|---|
| Project name | `frontend` |
| TypeScript | **Yes** |
| JSX Support | No |
| Vue Router | **No** — 単一画面のため |
| Pinia | **Yes** |
| Vitest | No |
| End-to-End Testing | No |
| ESLint | **Yes** |
| Prettier | **Yes** |
| Vue DevTools | No |

> 非対話で流したい場合は `npm create vue@latest -- --help` でフラグ名を確認してから使う。
> フラグ名はバージョン間で変わるため、本書では断定しない。

生成後:

```bash
cd frontend
npm install
```

create-vue は `frontend/.gitignore` を同梱する。ルートの `.gitignore` と併存して問題ないのでそのまま残す。

**ゲート**

```bash
ctxray capture -- npm run build
```

---

## Phase 6: frontend の実装

### 目標のファイル構成

```
frontend/src/
├── main.ts               # createPinia() を登録（生成物のまま）
├── App.vue               # 画面本体
├── types/
│   └── todo.ts           # Todo / TodoCreate / TodoUpdate を手書き定義
├── stores/
│   └── todos.ts          # Pinia ストア。fetch をここに集約
└── components/
    ├── TodoForm.vue      # 新規作成フォーム
    └── TodoItem.vue      # 1 件の表示・完了トグル・編集・削除
```

create-vue が生成する `components/HelloWorld.vue` 等のサンプルと `assets/` の初期 CSS は削除する。

### 規約上の注意（`CLAUDE.md` より）

- 全コンポーネントで `<script setup lang="ts">` を使う（Options API 禁止）。
- `any` を使わない。API の戻りは `types/todo.ts` の型で受ける。
- **`fetch` はコンポーネントから直接呼ばない** — すべて `stores/todos.ts` 経由。
- スタイルは `<style scoped>`。UI フレームワークは入れない。
- 型定義は手書き同期。backend の `schemas.py` を変えたら `types/todo.ts` も必ず直す。

### ストアの持ち物

`useTodosStore`: state に `todos` / `loading` / `error`、actions に
`fetchTodos` / `createTodo` / `updateTodo` / `deleteTodo`。
リクエスト先は `/api/todos`（絶対 URL は書かない。proxy に任せる）。

**ゲート**

```bash
ctxray capture -- npm run lint
ctxray capture -- npm run build      # vue-tsc の型チェックが通ること
```

---

## Phase 7: 結線と通し確認

### Vite dev proxy

`frontend/vite.config.ts` の `defineConfig` に追加:

```ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
  },
},
```

- `localhost` ではなく **`127.0.0.1`** を指定する。Node 18 以降は `localhost` を `::1` に
  先に解決するため、uvicorn が IPv4 のみで待ち受けていると接続に失敗する。
- proxy が効いていれば FastAPI 側に CORS ミドルウェアは不要。
  もし追加したくなったら、proxy が壊れているサインなので先に proxy を疑う。

### 起動（ユーザーに依頼）

ターミナル 2 枚。**dev サーバは常駐するので `ctxray capture` は使わない**
（capture はビルド・テストなど終了するコマンド用）。

```bash
# 1 枚目
cd backend && uv run uvicorn app.main:app --reload      # → http://127.0.0.1:8000

# 2 枚目
cd frontend && npm run dev                              # → http://localhost:5173
```

### 確認項目

| # | 確認 | 方法 |
|---|---|---|
| 1 | backend 単体が応答する | `curl http://127.0.0.1:8000/api/todos` → `[]` |
| 2 | OpenAPI が引ける | http://127.0.0.1:8000/docs を開く |
| 3 | proxy が通っている | `curl http://localhost:5173/api/todos` → `[]` |
| 4 | 画面から作成できる | ブラウザで入力 → 一覧に出る |
| 5 | 完了トグルが効く | チェック → リロードしても保持される |
| 6 | 編集・削除が効く | 各操作後にリロードして確認 |
| 7 | 永続化されている | backend を再起動しても一覧が残る |

**ゲート**: 1〜7 すべて OK。4〜7 はブラウザ操作なのでユーザーに依頼する。

---

## Phase 8: ドキュメント反映

`CLAUDE.md` を更新する（追記ではなく置換）。

- 「開発コマンド」の `TBD` を、Phase 7 で実際に動いたコマンドへ置換。
- ディレクトリ構成の「未セットアップ」を実構成へ置換。
- ローカル環境の表に uv の実バージョンを追記し、「未インストール」の記述を消す。
- 「未決定の論点」から完了した項目を削除。
- 本書（`SETUP.md`）の各フェーズに「実行済み: YYYY-MM-DD」を追記。

---

## 判断が必要になったら止まる箇所

以下に行き当たったら、推測で進めずユーザーに確認する。

1. Phase 1 で uv のインストーラが失敗する（プロキシ・証明書等）→ venv + pip への切り替え判断
2. Phase 5 で create-vue のプロンプト構成が上表と食い違う → 選択の読み替え確認
3. Phase 7 で proxy が通らない → CORS ミドルウェア追加に切り替えるかの判断
4. API 契約の変更が必要になった → `CLAUDE.md` の契約表の改訂承認
