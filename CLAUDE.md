# CLAUDE.md

> **ステータス: 技術スタック・API 契約 確定（2026-08-26） / セットアップ未着手**
> セットアップの手順とゲートは `SETUP.md` を参照する。
> 未決定の項目は「未決定の論点」セクションのみ。推測で実装を進めない。

## プロジェクト概要

Vue.js + FastAPI のサンプルプロジェクト。学習・検証用。

- **ドメイン**: TODO アプリ（タスクの作成 / 一覧 / 更新 / 完了 / 削除）
- **目的**: フロント（Vue）とバックエンド（FastAPI）を分離した構成で、CRUD 一通りが動く最小構成を作る
- **本番運用は想定しない**（認証・権限・監査ログ等は現時点でスコープ外）

## ディレクトリ構成

```
vue-fastapi-sample/          # 単一の git リポジトリ（main ブランチ）
├── CLAUDE.md          # このファイル（スタック・契約・規約の正本）
├── SETUP.md           # セットアップ計画（手順とゲート）
├── .gitignore         # フロント / バック双方をルートでまとめて管理
├── frontend/          # Vue 3 + Vite + TypeScript（未セットアップ）
└── backend/           # FastAPI + uv（未セットアップ）
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
| Lint / Format | ESLint + Prettier | create-vue 同梱の構成をそのまま使う |

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

## 開発コマンド

TBD — セットアップ未着手。以下は予定のコマンドであり、セットアップ完了後に実測値へ置換する。

```
# frontend（予定）
cd frontend && npm run dev

# backend（予定）
cd backend && uv run uvicorn app.main:app --reload
```

**ビルド・テストの実行は必ず `ctxray capture -- <cmd>` 経由で行う。**
生ログが保存され、失敗が隠れない。`| tail` でのパイプは禁止。

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

1. **セットアップの実行**: `SETUP.md` の Phase 1（uv 導入）から着手してよいか

## 作業ルール

- 実装に入る前に、変更の方針と対象ファイルを提示して確認を取る。
- `TBD` の項目に依存する実装を始める前に、その項目を確定させる。
- 決定した内容はこのファイルに反映し、`TBD` を実際の内容へ置き換える（追記ではなく置換）。
