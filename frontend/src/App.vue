<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import TodoForm from '@/components/TodoForm.vue'
import TodoItem from '@/components/TodoItem.vue'
import { useTodosStore } from '@/stores/todos'

const store = useTodosStore()
// ref のまま取り出すため storeToRefs を通す（分割代入だけだと reactivity が切れる）
const { todos, loading, error, remainingCount } = storeToRefs(store)

onMounted(store.fetchTodos)
</script>

<template>
  <main class="app">
    <h1>TODO</h1>

    <TodoForm @submit="store.createTodo" />

    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="loading" class="status">通信中…</p>

    <ul v-if="todos.length" class="list">
      <TodoItem
        v-for="todo in todos"
        :key="todo.id"
        :todo="todo"
        @toggle="(id, completed) => store.updateTodo(id, { completed })"
        @rename="(id, title) => store.updateTodo(id, { title })"
        @remove="store.deleteTodo"
      />
    </ul>
    <p v-else-if="!loading" class="empty">タスクはありません。</p>

    <p class="count">未完了 {{ remainingCount }} 件 / 全 {{ todos.length }} 件</p>
  </main>
</template>

<style scoped>
.app {
  max-width: 40rem;
  margin: 2rem auto;
  padding: 0 1rem;
  font-family: system-ui, sans-serif;
  color: #2c3e50;
}

h1 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.list {
  list-style: none;
  margin: 1rem 0 0;
  padding: 0;
}

.error {
  margin: 1rem 0 0;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  background: #fdecea;
  color: #c0392b;
}

.status,
.empty,
.count {
  margin: 1rem 0 0;
  color: #888;
  font-size: 0.875rem;
}
</style>
