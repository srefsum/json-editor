<template>
  <div class="json-editor-container">
    <div class="editor-wrapper" :class="{ 'has-error': error || (validationErrors && validationErrors.length > 0) }">
      <div class="line-numbers" v-if="showLineNumbers">
        <div 
          v-for="(line, index) in lineCount" 
          :key="index"
          class="line-number"
          :class="{ 'line-error': errorLines.has(index + 1) }"
        >
          {{ index + 1 }}
        </div>
      </div>
      <textarea
        ref="textareaRef"
        v-model="localValue"
        @input="handleInput"
        @scroll="handleScroll"
        class="json-editor"
        :class="{ 'error': error, 'with-line-numbers': showLineNumbers }"
        spellcheck="false"
      ></textarea>
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-if="validationErrors && validationErrors.length > 0" class="validation-errors">
      <div v-for="(err, index) in validationErrors" :key="index" class="validation-error-item">
        <span class="error-path">{{ err.path || 'root' }}</span>
        <span class="error-text">{{ err.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  },
  validationErrors: {
    type: Array,
    default: () => []
  },
  showLineNumbers: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

const localValue = ref(props.modelValue)
const textareaRef = ref(null)

const lineCount = computed(() => {
  return (localValue.value.match(/\n/g) || []).length + 1
})

const errorLines = computed(() => {
  const lines = new Set()
  if (props.validationErrors) {
    for (const err of props.validationErrors) {
      if (err.path) {
        const line = findLineForPath(err.path)
        if (line) lines.add(line)
      }
    }
  }
  return lines
})

const findLineForPath = (path) => {
  if (!path || path === 'root') return null
  
  const pathParts = path.split('/').filter(p => p)
  if (pathParts.length === 0) return null
  
  const lines = localValue.value.split('\n')
  let searchKey = pathParts[pathParts.length - 1]
  
  if (searchKey.startsWith('[') && searchKey.endsWith(']')) {
    searchKey = searchKey.slice(1, -1)
  }
  
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(`"${searchKey}"`) || lines[i].includes(`'${searchKey}'`)) {
      return i + 1
    }
  }
  
  return null
}

watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleScroll = (event) => {
  const lineNumbers = event.target.parentElement.querySelector('.line-numbers')
  if (lineNumbers) {
    lineNumbers.scrollTop = event.target.scrollTop
  }
}
</script>

<style scoped>
.json-editor-container {
  position: relative;
  width: 100%;
}
</style>

<style>
/* Light theme (default) */
.json-editor-container .editor-wrapper {
  display: flex;
  position: relative;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
  background-color: #ffffff;
}

.json-editor-container .line-numbers {
  flex-shrink: 0;
  width: 50px;
  background-color: #f3f4f6;
  color: #6b7280;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 16px 8px;
  text-align: right;
  overflow: hidden;
  user-select: none;
  border-right: 1px solid #e5e7eb;
}

.json-editor-container .line-number {
  height: 21px;
}

.json-editor-container .line-number.line-error {
  color: #dc2626;
  font-weight: bold;
  background-color: rgba(239, 68, 68, 0.12);
}

.json-editor-container .json-editor {
  flex: 1;
  min-height: 400px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 16px;
  border: none;
  background-color: #ffffff;
  color: #111827;
  resize: vertical;
  outline: none;
  transition: all 0.2s;
}

.json-editor-container .json-editor.with-line-numbers {
  border-left: none;
}

.json-editor-container .editor-wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.json-editor-container .editor-wrapper.has-error {
  border-color: #ef4444;
}

.json-editor-container .editor-wrapper.has-error:focus-within {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

.json-editor-container .json-editor.error {
  background-color: #fef2f2;
}

.json-editor-container .error-message {
  margin-top: 8px;
  font-size: 14px;
  color: #dc2626;
}

.json-editor-container .validation-errors {
  margin-top: 12px;
  border: 1px solid #fecaca;
  border-radius: 6px;
  background-color: #fef2f2;
  padding: 12px;
}

.json-editor-container .validation-error-item {
  display: flex;
  flex-direction: column;
  padding: 8px 0;
  border-bottom: 1px solid #fecaca;
}

.json-editor-container .validation-error-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.json-editor-container .error-path {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  color: #991b1b;
  font-weight: 600;
  margin-bottom: 4px;
}

.json-editor-container .error-text {
  font-size: 14px;
  color: #7f1d1d;
}

/* Dark theme */
html.dark .json-editor-container .editor-wrapper {
  background-color: #1e1e1e;
  border-color: #3e3e42;
}

html.dark .json-editor-container .line-numbers {
  background-color: #252526;
  color: #858585;
  border-right-color: #3e3e42;
}

html.dark .json-editor-container .line-number.line-error {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.1);
}

html.dark .json-editor-container .json-editor {
  background-color: #1e1e1e;
  color: #d4d4d4;
}

html.dark .json-editor-container .editor-wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

html.dark .json-editor-container .editor-wrapper.has-error:focus-within {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

html.dark .json-editor-container .json-editor.error {
  background-color: #2a1a1a;
}

html.dark .json-editor-container .error-message {
  color: #f87171;
}

html.dark .json-editor-container .validation-errors {
  border-color: #7f1d1d;
  background-color: rgba(127, 29, 29, 0.35);
}

html.dark .json-editor-container .validation-error-item {
  border-bottom-color: rgba(248, 113, 113, 0.25);
}

html.dark .json-editor-container .error-path {
  color: #fecaca;
}

html.dark .json-editor-container .error-text {
  color: #fca5a5;
}
</style>
