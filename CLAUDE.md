# CLAUDE.md

> **ステータス: セットアップ完了・CRUD 一通り動作（2026-08-26）**
> セットアップの手順・実行記録・踏んだ問題は `SETUP.md` を参照する。
> 未決定の項目は「未決定の論点」セクションのみ。推測で実装を進めない。

## プロジェクト概要

Vue.js + FastAPI のサンプルプロジェクト。学習・検証用。

- **ドメイン**: TODO アプリ（タスクの作成 / 一覧 / 更新 / 完了 / 削除）
- **目的**: フロント（Vue）とバックエンド（FastAPI）を分離した構成で、CRUD 一通りが動く最小構成を作る
- **本番運用は想定しない**（認証・権限・監査ログ等は現時点でスコープ外）

## ディレクトリ構成

```
vue-fastapi-sample/               # 単一の git リポジトリ（既定ブランチ main）
├── CLAUDE.md                     # このファイル（スタック・契約・規約の正本）
├── SETUP.md                      # セットアップの手順と実行記録
├── PROMPT_LOG.md                 # 構築時のやり取り（投げたプロンプトと各段の決定）
├── .gitignore                    # フロント / バック双方をルートでまとめて管理
├── frontend/
│   ├── vite.config.ts            # @ エイリアスと /api の dev proxy
│   └── src/
│       ├── App.vue               # 画面本体
│       ├── main.ts               # createPinia() の登録
│       ├── types/todo.ts         # backend の schemas.py と手で同期
│       ├── stores/todos.ts       # Pinia ストア。fetch はここに集約
│       └── components/
│           ├── TodoForm.vue
│           └── TodoItem.vue
└── backend/
    ├── pyproject.toml            # 依存 + Ruff / pytest 設定
    ├── todo.db                   # SQLite（gitignore 済み）
    ├── app/
    │   ├── main.py               # FastAPI インスタンスと lifespan
    │   ├── db.py                 # engine / get_session / SessionDep
    │   ├── models.py             # SQLModel テーブルモデル
    │   ├── schemas.py            # 入出力スキーマ
    │   ├── crud.py               # 永続化操作
    │   └── routers/todos.py      # /api/todos
    └── tests/                    # conftest.py / test_todos.py
```

フロントとバックエンドは独立したアプリとして扱う。共通コードの共有は現時点では行わない。

## 技術スタック

### フロントエンド

| 領域 | 採用 | 理由・補足 |
|---|---|---|
| フレームワーク | Vue 3 | Composition API + `<script setup>` |
| 言語 | TypeScript | API レスポンスの型付けを効かせる |
| ビルドツール | Vite | `npm create vue@latest` のプロジェクト生成を使う |
| 状態管理 | Pinia | ストアの作り方をサンプルとして示す目的で採用 |
| ルーティング | **採用しない** | 単一画面（一覧＋インライン編集）で完結させる |
| UI | 素の CSS（`<style scoped>`） | UI フレームワークは入れない |
| テスト | **導入しない** | フロントのテストはスコープ外 |
| Lint / Format | ESLint + Prettier（+ oxlint） | create-vue 同梱の構成。oxlint は ESLint 選択時に自動で付く |

### バックエンド

| 領域 | 採用 | 理由・補足 |
|---|---|---|
| フレームワーク | FastAPI | |
| パッケージ管理 | uv | `pyproject.toml` + `uv.lock` で管理。`requirements.txt` は使わない |
| データストア | SQLite | ファイル 1 個で永続化。再起動でデータを維持する |
| ORM | SQLModel | Pydantic とモデル定義を兼用し、スキーマの二重定義を避ける |
| テスト | pytest | `TestClient` で API を検証する。HTTP クライアントは `httpx2`（Starlette 1.6 系の推奨） |
| Lint / Format | Ruff | lint と format の両方を Ruff で行う（Black / isort は使わない） |

### 共通

| 領域 | 採用 | 理由・補足 |
|---|---|---|
| 構成 | `frontend/` と `backend/` の併置 | モノレポ、パッケージ共有なし |
| バージョン管理 | 単一 git リポジトリ | フロント / バックを分けない。既定ブランチは `main` |
| 実行方法 | ローカル直起動 | Docker Compose は使わない。ターミナル 2 枚で起動する |
| CORS | Vite の dev proxy で回避 | `/api` を backend へ proxy する。FastAPI 側の CORS 設定は原則不要 |
| 型定義の同期 | 手書き | OpenAPI からの生成は行わない。`frontend/src/types/todo.ts` に手で定義する |

## ローカル環境（確認済み）

WSL2 / Ubuntu 上で作業する。

| ツール | バージョン |
|---|---|
| Node.js | v24.16.0 |
| npm | 11.13.0 |
| Python | 3.12.3（`/usr/bin/python3.12`） |
| uv | 0.12.5（`~/.local/bin/uv`） |
| Docker | 29.7.2 |

- `~/.local/bin` は PATH 済み。uv 導入後のシェル再読み込みは不要。
- uv は システムの Python 3.12.3 を認識済み。別バージョンのダウンロードは不要。
- Docker は採用しない（インストール済みだが使わない）。
- `curl` はこの環境では実行が許可されていない。HTTP 疎通確認は `python3` の `urllib` を使う。

### 主要な依存バージョン（2026-08-26 時点）

| frontend | | backend | |
|---|---|---|---|
| vue | 3.5.40 | fastapi | 0.141.1 |
| pinia | 4.0.2 | sqlmodel | 0.0.39 |
| vite | 8.2.2 | sqlalchemy | 2.0.52 |
| typescript | 6.0 | pydantic | 2.13.4 |
| eslint | 10.7 | uvicorn | 0.52.4 |
| prettier | 3.9.5 | pytest | 9.1.1 |
| oxlint | 1.80 | ruff | 0.16.4 |

## 開発コマンド

### 起動（ターミナル 2 枚）

```bash
cd backend  && uv run uvicorn app.main:app --reload   # http://127.0.0.1:8000（docs: /docs）
cd frontend && npm run dev                            # http://localhost:5173
```

backend を先に起動する。frontend の `/api` は Vite の proxy で backend へ中継される。

### 検査（コミット前に通す）

```bash
# backend
cd backend && ctxray capture -- uv run pytest
cd backend && ctxray capture -- uv run ruff check .
cd backend && ctxray capture -- uv run ruff format --check .

# frontend
cd frontend && ctxray capture -- npm run build   # vue-tsc の型検査 + vite build
cd frontend && ctxray capture -- npm run check   # oxlint / eslint / prettier
```

### 自動修正

```bash
cd backend  && uv run ruff format .
cd frontend && npm run lint      # oxlint --fix + eslint --fix
cd frontend && npm run format    # prettier --write
```

**ビルド・テストの実行は必ず `ctxray capture -- <cmd>` 経由で行う。**
生ログが保存され、失敗が隠れない。`| tail` でのパイプは禁止。
ただし **dev サーバのような常駐コマンドは `ctxray capture` に通さない**（終了しないため）。

`npm run lint` / `npm run format` は自動修正するので検査には使わない。検査は `npm run check`。

## API 契約

**承認済み（2026-08-26）** — この表を正本とする。変更する場合はユーザーの承認を取る。

| メソッド | パス | リクエスト | レスポンス |
|---|---|---|---|
| GET | `/api/todos` | — | 200 `Todo[]` |
| POST | `/api/todos` | `TodoCreate` | 201 `Todo` |
| GET | `/api/todos/{id}` | — | 200 `Todo` / 404 |
| PATCH | `/api/todos/{id}` | `TodoUpdate` | 200 `Todo` / 404 |
| DELETE | `/api/todos/{id}` | — | 204 / 404 |

スキーマ:

```
Todo       = { id: int, title: str, completed: bool, created_at: datetime }
TodoCreate = { title: str }
TodoUpdate = { title?: str, completed?: bool }   # 部分更新
```

- 型定義は手書きで同期する。バックエンドの `app/schemas.py` を変更したら、`frontend/src/types/todo.ts` も必ず合わせて更新する。

## コーディング規約

### 共通
- コメント・ドキュメントは日本語で書く。
- 既存コードの書き方（命名・コメント量・イディオム）に合わせる。

### フロントエンド
- Vue 3 の Composition API + `<script setup>` を使う（Options API は使わない）。
- TypeScript の `any` は使わない。API のレスポンス型は `src/types/` に定義して共有する。
- スタイルは `<style scoped>` に書く。グローバル CSS は最小限に留める。
- サーバ通信は Pinia ストアに集約し、コンポーネントから直接 `fetch` を呼ばない。

### バックエンド
- FastAPI の依存性注入（`Depends`）を使い、ルータ層にビジネスロジックを直書きしない。
- リクエスト / レスポンスは Pydantic モデルで型付けする。
- DB セッションは `Depends` 経由で受け取る。ルータ内で直接生成しない。
- SQLModel のテーブルモデルをそのままレスポンスに返さず、レスポンス用スキーマを分ける。

## 未決定の論点（次に決めること）

セットアップ時点の論点はすべて解消済み。以降に持ち越した検討事項は次のとおり。

1. **frontend のテスト**: 現状は未導入。ストアのロジックが増えたら Vitest の導入を検討する。
2. **エラー表示の粒度**: 現状はストアの `error` を 1 行表示するのみ。
   409 / 422 など状況別の出し分けは未実装。
3. **`vite-plugin-vue-devtools`**: create-vue が無条件で同梱するため残している。
   不要になったら `vite.config.ts` の 2 行と devDependency を削る。

## 作業ルール

- 実装に入る前に、変更の方針と対象ファイルを提示して確認を取る。
- `TBD` の項目に依存する実装を始める前に、その項目を確定させる。
- 決定した内容はこのファイルに反映し、`TBD` を実際の内容へ置き換える（追記ではなく置換）。
