import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Todo, TodoCreate, TodoUpdate } from '@/types/todo'

// 相対パスで書く。dev では Vite の proxy が backend へ中継する（vite.config.ts 参照）。
const BASE_URL = '/api/todos'

/** fetch を実行し、エラーレスポンスは例外に変換して返す。 */
async function send(url: string, init?: RequestInit): Promise<Response> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`)
  }
  return res
}

/** body を JSON として受け取る版。204 を返すエンドポイントには使わない。 */
async function sendJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await send(url, init)
  return (await res.json()) as T
}

/**
 * TODO の状態とサーバ通信をまとめる。
 * コンポーネントから直接 fetch を呼ばず、必ずこのストア経由にする。
 */
export const useTodosStore = defineStore('todos', () => {
  const todos = ref<Todo[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const remainingCount = computed(() => todos.value.filter((todo) => !todo.completed).length)

  /** loading と error の面倒を一箇所で見るためのラッパ。 */
  async function run(task: () => Promise<void>): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await task()
    } catch (e) {
      error.value = e instanceof Error ? e.message : '通信に失敗しました'
    } finally {
      loading.value = false
    }
  }

  /** 一覧を取得して置き換える。 */
  async function fetchTodos(): Promise<void> {
    await run(async () => {
      todos.value = await sendJson<Todo[]>(BASE_URL)
    })
  }

  /** 作成し、成功したら手元の一覧末尾に足す（backend も作成順で返すため再取得は不要）。 */
  async function createTodo(title: string): Promise<void> {
    await run(async () => {
      const body: TodoCreate = { title }
      const created = await sendJson<Todo>(BASE_URL, {
        method: 'POST',
        body: JSON.stringify(body),
      })
      todos.value.push(created)
    })
  }

  /** 部分更新。サーバが返した最新の内容で該当行を差し替える。 */
  async function updateTodo(id: number, changes: TodoUpdate): Promise<void> {
    await run(async () => {
      const updated = await sendJson<Todo>(`${BASE_URL}/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(changes),
      })
      const index = todos.value.findIndex((todo) => todo.id === id)
      if (index !== -1) {
        todos.value[index] = updated
      }
    })
  }

  /** 削除。204 が返るので body は読まない。 */
  async function deleteTodo(id: number): Promise<void> {
    await run(async () => {
      await send(`${BASE_URL}/${id}`, { method: 'DELETE' })
      todos.value = todos.value.filter((todo) => todo.id !== id)
    })
  }

  return {
    todos,
    loading,
    error,
    remainingCount,
    fetchTodos,
    createTodo,
    updateTodo,
    deleteTodo,
  }
})
