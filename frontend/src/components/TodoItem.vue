<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { Todo } from '@/types/todo'

const props = defineProps<{
  todo: Todo
}>()

const emit = defineEmits<{
  toggle: [id: number, completed: boolean]
  rename: [id: number, title: string]
  remove: [id: number]
}>()

const editing = ref(false)
const draft = ref('')
const inputRef = useTemplateRef<HTMLInputElement>('input')

async function startEdit(): Promise<void> {
  draft.value = props.todo.title
  editing.value = true
  // input が描画されてからでないと focus できない
  await nextTick()
  inputRef.value?.focus()
}

/** 空文字と無変更は送らない（無駄な PATCH と 422 を避ける）。 */
function commitEdit(): void {
  const trimmed = draft.value.trim()
  editing.value = false
  if (!trimmed || trimmed === props.todo.title) {
    return
  }
  emit('rename', props.todo.id, trimmed)
}

function cancelEdit(): void {
  editing.value = false
}
</script>

<template>
  <li class="item" :class="{ 'is-completed': todo.completed }">
    <input
      type="checkbox"
      :checked="todo.completed"
      :aria-label="`${todo.title} を完了にする`"
      @change="emit('toggle', todo.id, !todo.completed)"
    />

    <input
      v-if="editing"
      ref="input"
      v-model="draft"
      class="edit"
      type="text"
      maxlength="200"
      aria-label="タイトルを編集"
      @keyup.enter="commitEdit"
      @keyup.esc="cancelEdit"
      @blur="commitEdit"
    />
    <span v-else class="title" @dblclick="startEdit">{{ todo.title }}</span>

    <button v-if="!editing" type="button" class="edit-button" @click="startEdit">編集</button>
    <button type="button" class="remove" @click="emit('remove', todo.id)">削除</button>
  </li>
</template>

<style scoped>
.item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.title {
  flex: 1;
  cursor: pointer;
}

.is-completed .title {
  color: #999;
  text-decoration: line-through;
}

.edit {
  flex: 1;
  padding: 0.25rem 0.5rem;
  border: 1px solid #42b883;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  font-size: 0.875rem;
  cursor: pointer;
}

.remove {
  color: #c0392b;
}
</style>
