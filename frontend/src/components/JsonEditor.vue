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

.editor-wrapper {
  display: flex;
  position: relative;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
  background-color: #1e1e1e;
}

.line-numbers {
  flex-shrink: 0;
  width: 50px;
  background-color: #252526;
  color: #858585;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 16px 8px;
  text-align: right;
  overflow: hidden;
  user-select: none;
  border-right: 1px solid #3e3e42;
}

.line-number {
  height: 21px;
}

.line-number.line-error {
  color: #ef4444;
  font-weight: bold;
  background-color: rgba(239, 68, 68, 0.1);
}

.json-editor {
  flex: 1;
  min-height: 400px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 16px;
  border: none;
  background-color: #1e1e1e;
  color: #d4d4d4;
  resize: vertical;
  outline: none;
  transition: all 0.2s;
}

.json-editor.with-line-numbers {
  border-left: none;
}

.editor-wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.editor-wrapper.has-error {
  border-color: #ef4444;
}

.editor-wrapper.has-error:focus-within {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.json-editor.error {
  background-color: #2a1a1a;
}

.error-message {
  margin-top: 8px;
  font-size: 14px;
  color: #ef4444;
}

.validation-errors {
  margin-top: 12px;
  border: 1px solid #fecaca;
  border-radius: 6px;
  background-color: #fef2f2;
  padding: 12px;
}

.validation-error-item {
  display: flex;
  flex-direction: column;
  padding: 8px 0;
  border-bottom: 1px solid #fecaca;
}

.validation-error-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.error-path {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  color: #991b1b;
  font-weight: 600;
  margin-bottom: 4px;
}

.error-text {
  font-size: 14px;
  color: #7f1d1d;
}
</style>
