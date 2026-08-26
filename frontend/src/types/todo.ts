// backend の app/schemas.py と手で同期させる。
// あちらを変更したらこのファイルも必ず合わせて直す（OpenAPI からの自動生成はしない方針）。

/** レスポンス。backend の TodoRead に対応する。 */
export interface Todo {
  id: number
  title: string
  completed: boolean
  /** ISO 8601 文字列。SQLite はタイムゾーンを保持しないため、オフセットなしの値が返る。 */
  created_at: string
}

/** POST /api/todos のリクエスト。backend の TodoCreate に対応する。 */
export interface TodoCreate {
  title: string
}

/** PATCH /api/todos/{id} のリクエスト。backend の TodoUpdate に対応する。
 *  渡さなかった項目は変更されない。 */
export interface TodoUpdate {
  title?: string
  completed?: boolean
}
