<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="copy-doc-title"
  >
    <div
      class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
      @click="close"
    />
    <div
      class="relative z-10 w-full max-w-md rounded-lg bg-white px-4 pb-4 pt-5 shadow-xl sm:p-6"
    >
      <h3 id="copy-doc-title" class="text-lg font-medium text-gray-900">
        Copy to new document
      </h3>
      <p class="mt-1 text-sm text-gray-500">
        The JSON content is copied as-is. If this document uses a schema, a duplicate schema is created and linked to the new document.
      </p>
      <div class="mt-4">
        <label for="copy-doc-name" class="block text-sm font-medium text-gray-700">
          New document name
        </label>
        <input
          id="copy-doc-name"
          v-model="name"
          type="text"
          class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          @keydown.enter.prevent="submit"
        />
      </div>
      <div class="mt-5 flex justify-end space-x-3">
        <button
          type="button"
          class="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          :disabled="submitting"
          @click="close"
        >
          Cancel
        </button>
        <button
          type="button"
          class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="submitting || !name.trim()"
          @click="submit"
        >
          {{ submitting ? 'Copying…' : 'Copy' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  defaultName: { type: String, default: '' },
  submitting: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const name = ref('')

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      name.value = props.defaultName
    }
  }
)

function close() {
  emit('update:modelValue', false)
}

function submit() {
  const n = name.value.trim()
  if (!n) return
  emit('submit', n)
}
</script>
