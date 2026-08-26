# セットアップ計画

> **ステータス: Phase 0〜8 すべて完了（2026-08-26）**
> 技術スタックは `CLAUDE.md` の「技術スタック」を正本とする。本書はそれを前提に、
> 何をどの順で実行し、各段でどう緑を確認したか、どこで詰まったかを残す。
> 再セットアップ時はこの順でなぞれば同じ状態に到達できる。

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
| 2 | ブラウザでの目視確認 | http://localhost:5173 を開いて CRUD を一巡 | 7 |

dev サーバの常駐起動は当初「手動が必要」としていたが、**バックグラウンド実行で Claude 側から
起動・停止できたため不要**になった。HTTP での疎通確認も `python3` の `urllib` で代替できる
（`curl` はこの環境では権限で弾かれる）。残る手動作業はブラウザ操作のみ。

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

**実行済み: 2026-08-26（create-vue 3.23.0）**

`frontend/` は空なので、**リポジトリルートから**実行してディレクトリ名に `frontend` を指定する。
フラグを全部渡せば対話プロンプトには入らない。

```bash
cd /home/t_satou/workspace/vue-fastapi-sample
npm create vue@latest -- --ts --pinia --eslint --prettier --bare frontend
cd frontend
npm install
```

### フラグの実測結果（`npm create vue@latest -- --help`）

| フラグ | 効果 |
|---|---|
| `--ts` | TypeScript |
| `--pinia` | Pinia |
| `--eslint` | ESLint。**oxlint も無条件で同梱される**（`--oxlint` は廃止済みフラグ） |
| `--prettier` | Prettier |
| `--bare` | サンプルコードなしの最小構成 |
| `--router` / `--vitest` | 今回は渡さない（不採用のため） |

`--bare` があるので、当初計画していた「生成後に `HelloWorld.vue` や `assets/` を削除する」作業は不要。
ただし **Pinia のサンプル `src/stores/counter.ts` は `--bare` でも生成される** ので、
Phase 6 で `stores/todos.ts` に置き換える際に削除する。

### 導入されたバージョン（実績）

vue 3.5.40 / pinia 4.0.2 / vite 8.2.2 / typescript 6.0 / vue-tsc 3.3.7 /
eslint 10.7 / prettier 3.9.5 / oxlint 1.80

`package.json` の `engines` は `node ^22.18.0 || >=24.12.0`。ローカルの v24.16.0 は条件を満たす。

### 踏んだ問題と対処

1. **生成された `package.json` の peer dependency が壊れていて `npm install` が失敗した。**
   `eslint-plugin-oxlint@~1.73.0`（peer: `oxlint@~1.73.0`）に対し `oxlint@~1.74.0` が指定されており、
   `ERESOLVE` で止まる。create-vue 3.23.0 側のテンプレート不整合。
   → `--legacy-peer-deps` で誤魔化さず、**両方を `~1.80.0` に揃えて解決**した
   （`eslint-plugin-oxlint@1.80.0` の peer は `oxlint@~1.80.0`、どちらも実在する最新）。

2. **`npm run lint` と `npm run format` は自動修正するため、ゲートに使えない**
   （`oxlint . --fix` / `eslint . --fix --cache` / `prettier --write`）。
   → 書き換えない検査用に `check` スクリプト群を追加した。
   `lint:*` ではなく `check:*` にしたのは、`lint` が `run-s "lint:*"` で glob 展開するため、
   `lint:check` という名前だと `npm run lint` から再帰的に呼ばれてしまうから。

   ```json
   "check": "run-s \"check:*\"",
   "check:oxlint": "oxlint .",
   "check:eslint": "eslint .",
   "check:format": "prettier --check --experimental-cli src/"
   ```

3. **`vite-plugin-vue-devtools` は `--bare` でも入る**。3.23.0 に除外フラグはない。
   dev 専用プラグインで実害がなく、学習用途ではむしろ有用なため**そのまま残す**
   （計画では「Vue DevTools: No」としていた点からの変更）。

create-vue は `frontend/.gitignore` を同梱する。`node_modules` と `dist` はこちらで無視されるため、
ルートの `.gitignore` と併存させたまま残す。

**ゲート**

```bash
ctxray capture -- npm run build   # vue-tsc の型検査 + vite build
ctxray capture -- npm run check   # oxlint / eslint / prettier をすべて検査モードで
```

---

## Phase 6: frontend の実装

**実行済み: 2026-08-26**

### ファイル構成（実績）

```
frontend/src/
├── main.ts               # createPinia() を登録（生成物のまま、変更なし）
├── App.vue               # 画面本体。ストアと子コンポーネントを繋ぐ
├── types/
│   └── todo.ts           # Todo / TodoCreate / TodoUpdate を手書き定義
├── stores/
│   └── todos.ts          # Pinia ストア。fetch をここに集約
└── components/
    ├── TodoForm.vue      # 新規作成フォーム
    └── TodoItem.vue      # 1 件の表示・完了トグル・インライン編集・削除
```

`--bare` で生成したためサンプルコンポーネントは元から無い。
Pinia のサンプル `src/stores/counter.ts` だけは生成されるので削除した。

### 設計上の要点

| 箇所 | 内容 |
|---|---|
| `stores/todos.ts` | `send()` / `sendJson<T>()` の 2 段構成。DELETE は 204 で body が無いため `send()` を使う |
| 〃 | `run()` ラッパで `loading` / `error` の面倒を 1 箇所に集約 |
| 〃 | URL は `/api/todos` の相対パス。絶対 URL は書かず proxy に任せる |
| `App.vue` | `storeToRefs()` を通して state を取り出す（分割代入だけだと reactivity が切れる） |
| `TodoForm.vue` | 空文字は送信前に止める（backend の 422 を無駄に踏まない） |
| `TodoItem.vue` | 編集確定時、空文字と無変更は PATCH を送らない |
| 〃 | `useTemplateRef()`（Vue 3.5 以降）で input を掴み、`nextTick()` 後に focus |

### 計画からの変更点

- 一覧の再取得を避け、**作成 / 更新 / 削除の結果で手元の配列を直接更新**している。
  backend が作成順で返すため、末尾 push で並びが一致する。

### 規約上の注意（`CLAUDE.md` より）

- 全コンポーネントで `<script setup lang="ts">` を使う（Options API 禁止）。
- `any` を使わない。API の戻りは `types/todo.ts` の型で受ける。
- **`fetch` はコンポーネントから直接呼ばない** — すべて `stores/todos.ts` 経由。
- スタイルは `<style scoped>`。UI フレームワークは入れない。
- 型定義は手書き同期。backend の `schemas.py` を変えたら `types/todo.ts` も必ず直す。

### ストアの持ち物（実績）

`useTodosStore`:

- state: `todos` / `loading` / `error`
- getter: `remainingCount`（未完了件数）
- action: `fetchTodos` / `createTodo` / `updateTodo` / `deleteTodo`

リクエスト先は `/api/todos`（絶対 URL は書かない。proxy に任せる）。

**ゲート**

```bash
ctxray capture -- npm run build   # vue-tsc の型検査 + vite build
ctxray capture -- npm run check   # oxlint / eslint / prettier（すべて検査モード）
```

`npm run lint` はゲートに使わない（`--fix` 付きで書き換えてしまうため。Phase 5 の記録を参照）。

---

## Phase 7: 結線と通し確認

**実行済み: 2026-08-26（ブラウザ目視確認まで完了）**

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

`curl` はこの環境では権限で弾かれるため、疎通確認は `python3` の `urllib` で行う。

| # | 確認 | 結果 |
|---|---|---|
| 1 | backend 単体が応答する | ✅ `GET http://127.0.0.1:8000/api/todos` → 200 `[]` |
| 2 | OpenAPI / docs が引ける | ✅ `/docs`・`/openapi.json` とも 200 |
| 3 | 画面が配信される | ✅ `GET http://localhost:5173/` → 200 |
| 4 | **proxy が通っている** | ✅ `GET http://localhost:5173/api/todos` → 200 `[]` |
| 5 | proxy 経由で作成できる | ✅ POST → 201、`id` 採番あり |
| 6 | proxy 経由で更新できる | ✅ PATCH `completed` / `title` 単独更新とも 200 |
| 7 | 404 が返る | ✅ 存在しない id → 404 |
| 8 | proxy 経由で削除できる | ✅ DELETE → 204、以降一覧は空 |
| 9 | 永続化されている | ✅ backend を停止・再起動しても 1 件残った |
| 10 | 画面から CRUD を一巡 | ✅ ユーザーによるブラウザ目視確認で問題なし |

1〜10 すべて OK。

### 実測した挙動のメモ

- `created_at` はオフセットなしの ISO 文字列で返る（例 `2026-08-26T07:05:04.577478`）。
  SQLite がタイムゾーンを保持しないという `models.py` のコメントどおりの結果。
- 全件削除後に作成すると **`id` は 1 から振り直される**。SQLite の rowid は `AUTOINCREMENT` を
  付けない限り最大値の再利用を行うため。サンプル用途では問題にしない。
- backend を再起動しても Vite の proxy はそのまま繋がり直す。frontend の再起動は不要。

---

## Phase 8: ドキュメント反映

**実行済み: 2026-08-26**

`CLAUDE.md` を更新した（追記ではなく置換）。

- 「開発コマンド」の `TBD` を、実際に動いたコマンドへ置換。起動 / 検査 / 自動修正の 3 分類にした。
- ディレクトリ構成を実構成へ置換（主要ファイルの役割つき）。
- ローカル環境に uv 0.12.5 と「`curl` は使えない」旨を追記。主要な依存バージョン表を新設。
- 「未決定の論点」をセットアップ後の検討事項へ差し替え。
- 本書の各フェーズに「実行済み」を追記。

**ゲート**

`CLAUDE.md` の本文に `TBD` プレースホルダが残っていないこと。

```bash
grep -n TBD CLAUDE.md
```

ヒットするのは「作業ルール」節の 2 行のみ。これは運用ルールとしての `TBD` への言及であり、
未確定の placeholder ではないので残してよい。

---

## 判断が必要になったら止まる箇所

以下に行き当たったら、推測で進めずユーザーに確認する。

1. Phase 1 で uv のインストーラが失敗する（プロキシ・証明書等）→ venv + pip への切り替え判断
2. Phase 5 で create-vue のプロンプト構成が上表と食い違う → 選択の読み替え確認
3. Phase 7 で proxy が通らない → CORS ミドルウェア追加に切り替えるかの判断
4. API 契約の変更が必要になった → `CLAUDE.md` の契約表の改訂承認
