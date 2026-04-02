<template>
  <div class="json-editor-container">
    <div
      class="editor-toolbar flex flex-wrap items-center gap-2 mb-2 px-1"
      role="toolbar"
      aria-label="JSON folding"
    >
      <button
        type="button"
        class="rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1 text-xs font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 focus:ring-offset-white dark:focus:ring-offset-gray-900"
        @click="runFoldAll"
      >
        Fold all
      </button>
      <button
        type="button"
        class="rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1 text-xs font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 focus:ring-offset-white dark:focus:ring-offset-gray-900"
        @click="runUnfoldAll"
      >
        Unfold all
      </button>
      <span class="text-xs text-gray-500 dark:text-gray-400">Fold at depth</span>
      <input
        v-model.number="foldDepthInput"
        type="number"
        min="1"
        max="16"
        class="w-14 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-1 py-0.5 text-xs text-gray-900 dark:text-white"
      />
      <button
        type="button"
        class="rounded border border-indigo-600 bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 focus:ring-offset-white dark:focus:ring-offset-gray-900"
        @click="runFoldAtDepth"
      >
        Apply
      </button>
    </div>

    <div class="editor-wrapper" :class="{ 'has-error': error || (validationErrors && validationErrors.length > 0) }">
      <Codemirror
        v-model="localValue"
        placeholder=""
        :style="{ minHeight: '400px' }"
        :autofocus="false"
        :indent-with-tab="true"
        :tab-size="2"
        :extensions="codemirrorExtensions"
        @ready="onCmReady"
        @update:model-value="onCmUpdate"
      />
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
import { ref, watch, shallowRef } from 'vue'
import { storeToRefs } from 'pinia'
import { Codemirror } from 'vue-codemirror'
import { json } from '@codemirror/lang-json'
import {
  syntaxTree,
  foldGutter,
  foldKeymap,
  foldEffect,
  foldAll,
  unfoldAll
} from '@codemirror/language'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { EditorState, Compartment, RangeSetBuilder } from '@codemirror/state'
import { keymap, lineNumbers, EditorView, Decoration, ViewPlugin } from '@codemirror/view'
import { oneDark } from '@codemirror/theme-one-dark'
import { useThemeStore } from '../stores/theme'

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
const editorView = shallowRef(null)
const foldDepthInput = ref(1)
const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const themeCompartment = new Compartment()
const errorCompartment = new Compartment()

function objectArrayDepth(node) {
  let d = 0
  let n = node
  while (n) {
    const name = n.type.name
    if (name === 'Object' || name === 'Array') d++
    n = n.parent
  }
  return d
}

/**
 * Fold regions whose Object/Array node has structural depth `targetDepth`
 * (root value is depth 1, one level nested is depth 2, etc.).
 */
function collectRangesAtDepth(state, targetDepth) {
  const ranges = []
  const tree = syntaxTree(state)
  try {
    tree.iterate({
      enter(nodeRef) {
        const name = nodeRef.type.name
        if (name !== 'Object' && name !== 'Array') return
        const node = nodeRef.node ?? tree.resolveInner(nodeRef.from + 1, 1)
        if (!node) return
        if (objectArrayDepth(node) === targetDepth) {
          ranges.push({ from: nodeRef.from, to: nodeRef.to })
        }
      }
    })
  } catch {
    /* incomplete parse */
  }
  return ranges
}

function findLineForPath(text, path) {
  if (!path || path === 'root') return null

  const pathParts = path.split('/').filter((p) => p)
  if (pathParts.length === 0) return null

  const lines = text.split('\n')
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

function computeErrorLineNumbers(text, validationErrors) {
  const lines = new Set()
  if (validationErrors && validationErrors.length) {
    for (const err of validationErrors) {
      if (err.path) {
        const ln = findLineForPath(text, err.path)
        if (ln) lines.add(ln)
      }
    }
  }
  return lines
}

function errorLinesExtension(lineNumbersSet) {
  return ViewPlugin.define(
    (view) => ({
      decorations: computeLineDecorations(view.state, lineNumbersSet)
    }),
    {
      decorations: (v) => v.decorations
    }
  )
}

function computeLineDecorations(state, lineNumbersSet) {
  const errorLineMark = Decoration.line({ attributes: { class: 'cm-json-error-line' } })
  const b = new RangeSetBuilder()
  const sorted = [...lineNumbersSet].sort((a, z) => a - z)
  for (const lineNo of sorted) {
    if (lineNo < 1) continue
    try {
      const line = state.doc.line(lineNo)
      b.add(line.from, line.from, errorLineMark)
    } catch {
      /* invalid line */
    }
  }
  return b.finish()
}

const baseTheme = EditorView.theme({
  '&': {
    minHeight: '400px',
    fontSize: '14px'
  },
  '.cm-scroller': {
    fontFamily: "'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace",
    overflow: 'auto'
  },
  '.cm-json-error-line': {
    backgroundColor: 'rgba(239, 68, 68, 0.12)'
  },
  '&.cm-focused': {
    outline: 'none'
  }
})

const darkExtraTheme = EditorView.theme({
  '.cm-json-error-line': {
    backgroundColor: 'rgba(239, 68, 68, 0.18)'
  }
})

function initialThemeExtension() {
  return isDark.value ? [oneDark, darkExtraTheme] : [baseTheme]
}

function buildStaticExtensions() {
  const core = [
    EditorState.tabSize.of(2),
    json(),
    foldGutter(),
    history(),
    keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab, ...foldKeymap]),
    themeCompartment.of(initialThemeExtension()),
    errorCompartment.of(errorLinesExtension(new Set()))
  ]
  if (props.showLineNumbers) {
    core.splice(2, 0, lineNumbers())
  }
  return core
}

const codemirrorExtensions = shallowRef(buildStaticExtensions())

watch(
  () => props.showLineNumbers,
  () => {
    codemirrorExtensions.value = buildStaticExtensions()
  }
)

watch(
  () => props.modelValue,
  (v) => {
    if (v !== localValue.value) localValue.value = v
  }
)

function applyThemeAndErrors(view) {
  const lines = computeErrorLineNumbers(props.modelValue, props.validationErrors)
  view.dispatch({
    effects: [
      errorCompartment.reconfigure(errorLinesExtension(lines)),
      themeCompartment.reconfigure(initialThemeExtension())
    ]
  })
}

watch(
  () => [props.modelValue, props.validationErrors, isDark.value],
  () => {
    const view = editorView.value
    if (view) applyThemeAndErrors(view)
  },
  { deep: true }
)

function onCmReady(payload) {
  editorView.value = payload.view
  applyThemeAndErrors(payload.view)
}

function onCmUpdate(val) {
  emit('update:modelValue', val)
}

function runFoldAll() {
  const view = editorView.value
  if (view) foldAll(view)
}

function runUnfoldAll() {
  const view = editorView.value
  if (view) unfoldAll(view)
}

function runFoldAtDepth() {
  const view = editorView.value
  if (!view) return
  let d = Number(foldDepthInput.value)
  if (!Number.isFinite(d) || d < 1) d = 1
  if (d > 16) d = 16
  const ranges = collectRangesAtDepth(view.state, d)
  if (ranges.length === 0) return
  view.dispatch({
    effects: ranges.map((r) => foldEffect.of(r))
  })
}
</script>

<style scoped>
.json-editor-container {
  position: relative;
  width: 100%;
}
</style>

<style>
.json-editor-container .editor-wrapper {
  position: relative;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
  background-color: #ffffff;
}

.json-editor-container .editor-wrapper .cm-editor {
  min-height: 400px;
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

html.dark .json-editor-container .editor-wrapper {
  background-color: #1e1e1e;
  border-color: #3e3e42;
}

html.dark .json-editor-container .editor-wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

html.dark .json-editor-container .editor-wrapper.has-error:focus-within {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
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
