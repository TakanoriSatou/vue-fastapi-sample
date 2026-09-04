# PROMPT_LOG.md

> **このプロジェクトが Claude Code とのやり取りでどう作られたかの記録（2026-08-26）**
> 実際に投げたプロンプトを全文で残し、各段で何が決まって何が保留になったかを添える。
> 技術的な決定の正本は `CLAUDE.md`、手順と実行記録の正本は `SETUP.md`。
> ここは**やり取りそのもの**を残す位置づけで、両者の内容は複写せずリンクで参照する。

## 出典

Claude Code のセッションログ（`~/.claude/projects/` 配下の JSONL）から抽出した。

| # | セッション ID | 起動ディレクトリ | 期間（JST） | 成果 |
|---|---|---|---|---|
| 1 | `cb1beca3-697e-4b12-98d6-d7a4c604d9e9` | `/home/t_satou/workspace` | 15:03〜15:09（6 分） | プロジェクトの器と `CLAUDE.md`（仮） |
| 2 | `2998398d-ed16-4e09-8eca-f0add086585d` | `/home/t_satou/workspace/vue-fastapi-sample` | 15:11〜16:23（1 時間 12 分） | スタック確定・実装一式・GitHub への push |

- 使用モデル: `claude-opus-5[1m]` / Claude Code 2.1.246
- ログ内のタイムスタンプは UTC。本ファイルでは JST（+9h）に変換して記載する。
- セッション 1 の終了からセッション 2 の開始までは 2 分。作成したフォルダに `cd` して開き直した流れ。

---

## セッション 1: プロジェクトの器と CLAUDE.md（仮）

### 投げたプロンプト（15:03）

```
vue.js + fastAPI でサンプルプロジェクトを作りたい。
workspaceに新規プロジェクト用フォルダを作成して、claude.mdを仮作成して。
```

このセッションで投げたプロンプトはこれ 1 通のみ。以降は選択肢への回答だけで完結している。

### Claude の動き

1. `ls -la /home/t_satou/workspace` で既存プロジェクトの並びを確認
2. `node -v` / `npm -v` / `python3 -V` / `uv --version` / `poetry --version` / `docker --version` をまとめて実測
   → Node v24.16.0、npm 11.13.0、Python 3.12.3、Docker 29.7.2 を確認。**uv と poetry は未インストール**と判明
3. 選択肢を提示して方針を確認（下記）
4. `frontend/` `backend/` を `mkdir` し、`CLAUDE.md`（仮）を作成

### この段で決めたこと

Claude からの 4 問に対する回答。

| 質問 | 回答 |
|---|---|
| 新規プロジェクトのフォルダ名は？ | **`vue-fastapi-sample`**（他候補: `sample-app` / `vue-fastapi-todo`） |
| モノレポの構成はどうしますか？ | **`frontend/` + `backend/` 併置**（他候補: `apps/` 配下にまとめる） |
| 技術スタックの細部はどうしますか？ | **後で検討**（選択肢に無い自由入力） |
| サンプルの題材（CLAUDE.md に書くドメイン）は？ | **TODO アプリ**（他候補: 題材は未定のまま / ユーザー管理 + 認証） |

「技術スタックの細部」は提示された 4 択（Vue 3 + Vite + TypeScript / Pinia + Vue Router / Python venv + pip / Docker Compose）をいずれも選ばず、**「後で検討」と自由入力で答えた**。これがセッション 2 の起点になっている。

### この段で保留にしたこと

上記の判断により、初版 `CLAUDE.md` は「確定 3 項目・TBD 11 項目」の構成になった。

- **確定**: Vue 3 / FastAPI / `frontend` + `backend` 併置
- **TBD**: フロントの言語、ビルドツール、状態管理、ルーティング、UI フレームワーク、Python パッケージ管理、データストア、ORM、実行方法、テスト、Lint / Format
- あわせて「未決定の論点（次に決めること）」を 6 件、「`TBD` の項目に依存する実装を始める前に、その項目を確定させる」という作業ルールを明記

この「TBD を明示して推測で進めない」構造が、セッション 2 で埋める対象のチェックリストとして機能した。

---

## セッション 2: スタック確定から push まで

`vue-fastapi-sample/` に `cd` して起動し直したセッション。以降のプロンプトはすべてこちら。

### 2-1. 技術スタックの決定（15:11）

```
本プロジェクトの技術スタックを決めたい。一言説明付きで候補を提案して。
```

Claude は `CLAUDE.md` の TBD 11 項目に対応する候補表（フロント / バック / 共通）を推奨マーク付きで提示し、API 契約のたたき台も添えた。そのうえで**主要な分岐だけを 2 回に分けて確認**した。

**1 回目の 4 問**

| 質問 | 回答 |
|---|---|
| フロントエンドの言語はどちらにしますか？ | **TypeScript**（推奨どおり） |
| Python のパッケージ管理はどうしますか？ | **uv**（推奨どおり。未インストールなので導入から） |
| データストアはどうしますか？ | **SQLite + SQLModel**（推奨どおり） |
| 起動方法はどうしますか？ | **ローカル直起動**（推奨どおり。Docker Compose を却下） |

**2 回目の 4 問**

| 質問 | 回答 |
|---|---|
| UI はどうしますか？ | **素の CSS（scoped）**（推奨どおり） |
| テストはどこまで入れますか？ | **pytest のみ**（推奨どおり。Vitest は入れない） |
| フロントの状態管理とルーティングは？ | **Pinia だけ入れる** ← **推奨（どちらもなし）から外した唯一の選択** |
| フロント / バック間の型定義の同期は？ | **手書き**（推奨どおり。OpenAPI からの生成を却下） |

Pinia は「TODO 一画面なら composable 一枚で足りる」として非推奨だったが、**ストアの作り方をサンプルとして示す目的**で採用した。この意図は `CLAUDE.md` の技術スタック表にも理由として残っている。

**Claude が確認を取らずに推奨で書いた項目**（その旨を明示して報告あり）

- フロント: ESLint + Prettier（create-vue 同梱）
- バック: Ruff（lint と format を兼用、Black / isort は使わない）

また API 契約はこの時点では**「未承認の案」として記載**され、正本扱いにはされなかった。

### 2-2. API 契約の承認とセットアップ計画の文書化（15:24）

```
api契約はサンプルなのでこれでOK
セットアップ計画を新規mdファイルに文書化して。
```

- `CLAUDE.md` の API 契約を **承認済み（正本）** に切り替え
- `SETUP.md` を新規作成。**Phase 0〜8 の一直線**で、backend を先に立てる順序（フロントは叩く先が動かないと確認できないため）
- 「Claude が実行できない作業」を冒頭で表にして先に宣言する構成

この段で、**`curl` の実行が権限で拒否された**。npm レジストリから create-vue の最新版を実測しようとして弾かれたため、`npm create vue@latest` のプロンプト構成は「create-vue 3.23.0 想定・**未実測**」と断り書き付きで書かれた（実際に Phase 5 で食い違いが出る）。

### 2-3. git 初期化（15:31）

```
git でバージョン管理するため初期化して
リポジトリは1つにまとめてOK
```

- `git init -b main` — グローバルの `init.defaultBranch` が未設定（= `master`）だったため、この repo だけ `-b main` を明示。グローバル設定は変更していない
- ルートに `.gitignore` を 1 枚置き、フロント / バック双方をまとめて管理
- **`frontend/.gitkeep` `backend/.gitkeep` は置かない判断**。`frontend/.gitkeep` があると Phase 5 の `npm create vue@latest` が「対象ディレクトリが空でない」と判断して上書き確認を挟むため

### 2-4. Phase 1〜4: backend（15:33〜15:49）

```
phase 1 に進んで
```

uv のインストールは Claude が実行できないため手動依頼となり、セッション内で実行した。

```
! curl -LsSf https://astral.sh/uv/install.sh | sh
```

```
downloading uv 0.12.5 x86_64-unknown-linux-gnu
installing to /home/t_satou/.local/bin
  uv
  uvx
everything's installed!
```

以降は同じ粒度で進めた。

```
phase2 を進めて
```

```
phase3 を進めて
```

```
phase4 を進めて
```

```
ここまでをコミットして
```

各段の実装時の判断（`crud.py` を初回から作る、`SessionDep` を `Annotated` で定義して Ruff `B008` を避ける、`TestClient` を `with` で使わず本物の `todo.db` を作らせない、`httpx` → `httpx2` への差し替えなど）は `SETUP.md` の Phase 3 / Phase 4 の「計画からの変更点（実装時の判断）」に記録されている。

コミット `53a3199`「初期構成: 技術スタック確定と backend 実装」がこの段の成果。

### 2-5. Phase 5〜7: frontend と結線（15:52〜16:09）

```
feature/frontend で phase5 を進めて
実行して構成を読み取りながら進めて
```

ここで初めて**作業ブランチの指定**と、**「実行して構成を読み取りながら」という指示**が入った。Phase 5 の手順が `curl` 拒否のため未実測だったことへの対応で、実際に create-vue を動かして出力を見ながら進める形になった。

```
phase6 を進めて
```

```
phase7 を進めて
```

Phase 5 で踏んだ問題（create-vue 3.23.0 の peer dependency 不整合による `npm install` の `ERESOLVE` 失敗、`npm run lint` / `format` が `--fix` 付きでゲートに使えない問題）と、その対処は `SETUP.md` の Phase 5「踏んだ問題と対処」に記録されている。

Phase 7 のブラウザでの目視確認は Claude が実行できないため手動で行った。dev サーバの常駐起動は当初「手動が必要」と宣言していたが、バックグラウンド実行で Claude 側から起動・停止できたため不要になった。

### 2-6. Phase 8: ドキュメント反映とマージ（16:09〜16:12）

```
phase8 を進めて
```

`CLAUDE.md` の TBD を実測値へ置換した段。開発コマンドを起動 / 検査 / 自動修正の 3 分類に整理し、依存バージョン表を新設し、「`curl` はこの環境では実行が許可されていない。HTTP 疎通確認は `python3` の `urllib` を使う」を追記した（**今回実際に詰まった点の反映**）。「未決定の論点」もセットアップ時点の 6 件から持ち越し 3 件へ差し替えた。

最終ゲートは全通過（pytest 15 passed / ruff check・format / `npm run build` / `npm run check`）。

続いて `feature/frontend` の扱いを 2 択で聞かれ、番号で回答した。

```
1
```

`1` = **「`main` にマージして、このブランチを削除」**（`2` = そのまま置いておく）。`main` に差分コミットが無かったため fast-forward マージになり、履歴は線形。コミット `1313a43`「frontend: Vue 3 + Pinia で TODO 画面を実装し backend と結線」が `main` の HEAD になった。

### 2-7. GitHub への push（16:15）

```
下記リモートリポジトリに接続してpushして

https://github.com/TakanoriSatou/vue-fastapi-sample.git
```

リモートが**空・private** であることを確認してから remote を追加して push した（上書きの危険がないことの事前確認）。

### 2-8. フロントのテスト → 保留（16:19〜16:20）

```
フロントの単体テストを作成して
```

`CLAUDE.md` で「テスト: 導入しない」と決めていた項目だったため、Claude は**方針転換として扱い**、いきなり実装せず前提を実測してから方針（Vitest 4.1.11 + @vue/test-utils 2.4.11 + happy-dom、対象ファイル 6 種）を提示した。テストの対象範囲を確認する質問が出たところで、次の指示が入る。

```
フロントのテストは保留で。
```

**この時点で何も変更されていない**（インストールも設定ファイル作成もなし）ため、リポジトリは push した `1313a43` のままクリーンな状態を維持している。調査結果だけが会話に残り、`CLAUDE.md` の「未決定の論点」1 番目（frontend のテスト）がそのまま保留項目として機能した。

これがセッション 2 の最後のプロンプト。

---

## 横断的な記録

### 手動実行を依頼した操作

Claude が実行できず、ユーザーに依頼した作業は 2 件のみ。

| # | 作業 | Phase |
|---|---|---|
| 1 | uv のインストール（`! curl -LsSf https://astral.sh/uv/install.sh \| sh`） | 1 |
| 2 | ブラウザでの目視確認（http://localhost:5173 で CRUD を一巡） | 7 |

`! <command>` はセッション内で実行され、出力がそのまま会話に入るため、Claude は**実行後の検証だけ**を引き受けた。

### 実行が拒否されたコマンド

`curl` は権限で弾かれた。グローバル設定の「実行を拒否されたとき」ルールにより**別手段での迂回はせず**、影響が以下のように処理された。

- Phase 5 の手順を「未実測」と断り書き付きで記述 → 実際に食い違いが出て、実行しながら読み取る方針に切り替え
- HTTP 疎通確認は `python3` の `urllib` で代替
- この制約自体を `CLAUDE.md` の「ローカル環境」節に恒久的な注意として追記

### 決定を覆した / 保留にした項目

| 項目 | 当初 | 結果 |
|---|---|---|
| 状態管理（Pinia） | 推奨は「どちらもなし」 | サンプルとして示す目的で採用 |
| Vue DevTools プラグイン | 計画では「No」 | create-vue が無条件で同梱するため残す（`CLAUDE.md` の持ち越し論点 3） |
| フロントのテスト | 「導入しない」 | 追加を依頼 → 方針提示の段階で保留（持ち越し論点 1） |

### プロンプトの傾向

- **方針の確認は Claude 側の選択肢提示に任せ、回答は短い**。19 通のプロンプトのうち、実質的な指示は 11 通で、うち 6 通は `phaseN を進めて` の形
- **段取りを先に文書化させ（`SETUP.md`）、以降はフェーズ名で駆動する**進め方
- 推奨から外したのは Pinia のみ。それ以外は提案を受け入れている

なお 16:19 に `/context` の出力がログ上ユーザーメッセージとして記録されているが、これは Claude への指示ではなくコンテキスト使用量の表示。

---

## 記録の再現方法

セッションログから同じ抽出を行うコマンド。

```bash
# 投げたプロンプトを全文で時系列に出す
cd ~/.claude/projects
jq -r 'select(.type=="user" and (.message.content|type=="string"))
       | "----- [" + .timestamp + "] -----\n" + .message.content' \
  ./-home-t-satou-workspace-vue-fastapi-sample/2998398d-ed16-4e09-8eca-f0add086585d.jsonl

# 選択肢への回答（AskUserQuestion）だけを出す
jq -r 'select(.toolUseResult? and (.toolUseResult|type=="object") and .toolUseResult.answers)
       | .toolUseResult.answers | to_entries | map("Q: " + .key + "\nA: " + .value) | join("\n")' \
  ./-home-t-satou-workspace/cb1beca3-697e-4b12-98d6-d7a4c604d9e9.jsonl
```

ファイル名が `-` で始まるため、`jq` にはオプションと解釈されないよう `./` を付けて渡す。

セッションを対話形式で読み返す場合は、**起動ディレクトリを合わせてから** resume する。

```bash
cd /home/t_satou/workspace         && claude --resume cb1beca3-697e-4b12-98d6-d7a4c604d9e9
cd /home/t_satou/workspace/vue-fastapi-sample && claude --resume 2998398d-ed16-4e09-8eca-f0add086585d
```
