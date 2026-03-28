<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="mb-6">
      <router-link to="/" class="text-indigo-600 hover:text-indigo-900">
        ← Back to Documents
      </router-link>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h2 class="text-2xl font-semibold text-gray-900 mb-6">
          {{ isEditing ? 'Edit Document' : 'New Document' }}
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700">
              Document Name
            </label>
            <input
              v-model="formData.name"
              type="text"
              id="name"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            />
          </div>

          <div>
            <label for="schema" class="block text-sm font-medium text-gray-700">
              Schema (Optional)
            </label>
            <select
              v-model="formData.schema_id"
              id="schema"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            >
              <option :value="null">No schema</option>
              <option v-for="schema in schemas" :key="schema.id" :value="schema.id">
                {{ schema.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              JSON Content
            </label>
            <JsonEditor v-model="jsonContent" :error="jsonError" />
          </div>

          <div v-if="validationResult" class="rounded-md p-4" :class="validationResult.valid ? 'bg-green-50' : 'bg-red-50'">
            <div class="flex">
              <div class="flex-shrink-0">
                <span v-if="validationResult.valid" class="text-green-400">✓</span>
                <span v-else class="text-red-400">✗</span>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium" :class="validationResult.valid ? 'text-green-800' : 'text-red-800'">
                  {{ validationResult.valid ? 'Valid JSON' : 'Validation Errors' }}
                </h3>
                <div v-if="!validationResult.valid && validationResult.errors" class="mt-2 text-sm" :class="validationResult.valid ? 'text-green-700' : 'text-red-700'">
                  <ul class="list-disc list-inside space-y-1">
                    <li v-for="(error, index) in validationResult.errors" :key="index">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-between items-center pt-4">
            <button
              v-if="formData.schema_id"
              type="button"
              @click="validateAgainstSchema"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Validate
            </button>
            <div v-else></div>

            <div class="flex space-x-3">
              <router-link
                to="/"
                class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Cancel
              </router-link>
              <button
                type="submit"
                :disabled="saving || !!jsonError"
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import JsonEditor from '../components/JsonEditor.vue'
import { useSchemaStore } from '../stores/schemas'
import { storeToRefs } from 'pinia'

const route = useRoute()
const router = useRouter()
const schemaStore = useSchemaStore()
const { schemas } = storeToRefs(schemaStore)

const isEditing = computed(() => !!route.params.id)

const formData = ref({
  name: '',
  schema_id: null
})

const jsonContent = ref('{\n  \n}')
const jsonError = ref('')
const saving = ref(false)
const validationResult = ref(null)

onMounted(async () => {
  await schemaStore.fetchSchemas()
  
  if (isEditing.value) {
    try {
      const response = await api.getDocument(route.params.id)
      formData.value.name = response.data.name
      formData.value.schema_id = response.data.schema_id
      jsonContent.value = JSON.stringify(response.data.content, null, 2)
    } catch (err) {
      alert('Failed to load document')
      router.push('/')
    }
  }
})

const validateAgainstSchema = async () => {
  if (!formData.value.schema_id) return
  
  try {
    const content = JSON.parse(jsonContent.value)
    const response = await api.validateJson(formData.value.schema_id, content)
    validationResult.value = response.data
  } catch (err) {
    if (err instanceof SyntaxError) {
      validationResult.value = { valid: false, errors: ['Invalid JSON syntax'] }
    } else {
      validationResult.value = { valid: false, errors: ['Validation failed'] }
    }
  }
}

const handleSubmit = async () => {
  try {
    const content = JSON.parse(jsonContent.value)
    
    const data = {
      name: formData.value.name,
      content: content,
      schema_id: formData.value.schema_id
    }
    
    saving.value = true
    
    if (isEditing.value) {
      await api.updateDocument(route.params.id, data)
    } else {
      await api.createDocument(data)
    }
    
    router.push('/')
  } catch (err) {
    if (err instanceof SyntaxError) {
      jsonError.value = 'Invalid JSON syntax'
    } else {
      alert('Failed to save document')
    }
  } finally {
    saving.value = false
  }
}
</script>
