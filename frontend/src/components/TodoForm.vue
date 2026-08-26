<script setup lang="ts">
import { computed, ref } from 'vue'

const emit = defineEmits<{
  submit: [title: string]
}>()

const title = ref('')
const canSubmit = computed(() => title.value.trim().length > 0)

/** 空文字は backend が 422 で弾くので、送る前に止める。 */
function onSubmit(): void {
  if (!canSubmit.value) {
    return
  }
  emit('submit', title.value.trim())
  title.value = ''
}
</script>

<template>
  <form class="form" @submit.prevent="onSubmit">
    <input
      v-model="title"
      type="text"
      placeholder="やることを入力"
      maxlength="200"
      aria-label="やること"
    />
    <button type="submit" :disabled="!canSubmit">追加</button>
  </form>
</template>

<style scoped>
.form {
  display: flex;
  gap: 0.5rem;
}

input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: #42b883;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
