<template>
  <div class="json-editor-container">
    <textarea
      v-model="localValue"
      @input="handleInput"
      class="json-editor"
      :class="{ 'error': error }"
      spellcheck="false"
    ></textarea>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const localValue = ref(props.modelValue)

watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}
</script>

<style scoped>
.json-editor-container {
  position: relative;
  width: 100%;
}

.json-editor {
  width: 100%;
  min-height: 400px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}

.json-editor:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.json-editor.error {
  border-color: #ef4444;
}

.json-editor.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error-message {
  margin-top: 8px;
  font-size: 14px;
  color: #ef4444;
}
</style>
