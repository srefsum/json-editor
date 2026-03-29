<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="mb-6 flex justify-between items-center">
      <router-link to="/" class="text-indigo-600 hover:text-indigo-900">
        ← Back to Documents
      </router-link>
      <div class="flex space-x-3">
        <button
          v-if="isEditing"
          type="button"
          @click="openCopyModal"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Copy as new…
        </button>
        <button
          v-if="formData.schema_id"
          type="button"
          @click="validateAgainstSchema"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Validate
        </button>
        <button
          type="button"
          @click="handleSubmit"
          :disabled="saving || !!jsonError || !!schemaError"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ saving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>

    <div class="bg-white shadow sm:rounded-lg mb-6">
      <div class="px-4 py-4 sm:px-6 border-b border-gray-200">
        <h2 class="text-2xl font-semibold text-gray-900">
          {{ isEditing ? 'Edit Document' : 'New Document' }}
        </h2>
      </div>
      <div class="px-4 py-4 sm:p-6 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              Schema
            </label>
            <select
              v-model="formData.schema_id"
              id="schema"
              @change="onSchemaChange"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            >
              <option :value="null">No schema</option>
              <option v-for="schema in schemas" :key="schema.id" :value="schema.id">
                {{ schema.name }}
              </option>
            </select>
          </div>
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
                  <li v-for="(error, index) in validationResult.errors" :key="index">
                    <span v-if="error.path" class="font-mono">{{ error.path }}:</span>
                    {{ error.message }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white shadow sm:rounded-lg">
        <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">Schema</h3>
            <button
              v-if="formData.schema_id && schemaModified"
              type="button"
              @click="saveSchemaChanges"
              :disabled="savingSchema || !!schemaError"
              class="text-sm px-3 py-1 border border-transparent rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ savingSchema ? 'Saving...' : 'Save Schema' }}
            </button>
          </div>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div v-if="!formData.schema_id" class="text-center py-12 px-4 text-gray-500 space-y-4">
            <p>Select a schema to view and edit it, or generate one from the document JSON.</p>
            <button
              type="button"
              @click="proposeSchemaFromDocument"
              :disabled="proposingSchema"
              class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {{ proposingSchema ? 'Proposing…' : 'Propose schema from document' }}
            </button>
          </div>
          <JsonEditor v-else v-model="schemaContent" :error="schemaError" @update:modelValue="onSchemaEdit" />
        </div>
      </div>

      <div class="bg-white shadow sm:rounded-lg">
        <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <div class="flex justify-between items-center">
            <div class="flex items-center space-x-3">
              <h3 class="text-lg font-medium text-gray-900">JSON Document</h3>
              <span 
                v-if="formData.schema_id && validating" 
                class="text-xs text-gray-500"
              >
                Validating...
              </span>
              <span 
                v-else-if="formData.schema_id && validationResult && validationResult.valid" 
                class="text-xs text-green-600 font-medium"
              >
                ✓ Valid
              </span>
              <span 
                v-else-if="formData.schema_id && validationResult && !validationResult.valid" 
                class="text-xs text-red-600 font-medium"
              >
                ✗ Invalid
              </span>
            </div>
            <div class="flex items-center space-x-2">
              <select
                v-model="selectedDocumentToInsert"
                class="text-sm rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-2 py-1 border"
              >
                <option :value="null">Insert from...</option>
                <option v-for="doc in availableDocuments" :key="doc.id" :value="doc.id">
                  {{ doc.name }}
                </option>
              </select>
              <button
                type="button"
                @click="insertDocument"
                :disabled="!selectedDocumentToInsert"
                class="text-sm px-3 py-1 border border-gray-300 rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Insert
              </button>
            </div>
          </div>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <JsonEditor v-model="jsonContent" :error="jsonError" :validationErrors="validationErrors" />
        </div>
      </div>
    </div>

    <CopyDocumentModal
      v-model="copyModalOpen"
      :default-name="copyDefaultName"
      :submitting="copySubmitting"
      @submit="onCopySubmit"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import JsonEditor from '../components/JsonEditor.vue'
import CopyDocumentModal from '../components/CopyDocumentModal.vue'
import { useSchemaStore } from '../stores/schemas'
import { useDocumentStore } from '../stores/documents'
import { storeToRefs } from 'pinia'

const route = useRoute()
const router = useRouter()
const schemaStore = useSchemaStore()
const documentStore = useDocumentStore()
const { schemas } = storeToRefs(schemaStore)
const { documents } = storeToRefs(documentStore)

const isEditing = computed(() => !!route.params.id)

const availableDocuments = computed(() => {
  return documents.value.filter(doc => doc.id !== route.params.id)
})

const selectedDocumentToInsert = ref(null)

const formData = ref({
  name: '',
  schema_id: null
})

const jsonContent = ref('{\n  \n}')
const jsonError = ref('')
const saving = ref(false)
const validationResult = ref(null)
const validationErrors = ref([])
const validating = ref(false)
let validationTimeout = null

const schemaContent = ref('{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "type": "object"\n}')
const schemaError = ref('')
const originalSchemaContent = ref('')
const schemaModified = ref(false)
const savingSchema = ref(false)

const copyModalOpen = ref(false)
const copyDefaultName = ref('')
const copySubmitting = ref(false)
const proposingSchema = ref(false)

const openCopyModal = () => {
  copyDefaultName.value = formData.value.name ? `${formData.value.name} (copy)` : 'Untitled (copy)'
  copyModalOpen.value = true
}

const onCopySubmit = async (name) => {
  if (!route.params.id) return
  copySubmitting.value = true
  try {
    const created = await documentStore.copyDocument(route.params.id, { name })
    await schemaStore.fetchSchemas()
    copyModalOpen.value = false
    router.push(`/documents/${created.id}`)
  } catch (err) {
    alert('Failed to copy document')
  } finally {
    copySubmitting.value = false
  }
}

const proposeSchemaFromDocument = async () => {
  if (formData.value.schema_id) return
  let sample
  try {
    sample = JSON.parse(jsonContent.value)
  } catch {
    alert('Fix the document JSON syntax before proposing a schema.')
    return
  }
  proposingSchema.value = true
  schemaError.value = ''
  try {
    const { data } = await api.proposeSchemaFromSample({ sample })
    const docName = formData.value.name?.trim() || 'Document'
    const created = await api.createSchema({
      name: `${docName} (proposed schema)`,
      description: 'Generated from the current document JSON',
      schema: data.schema
    })
    await schemaStore.fetchSchemas()
    formData.value.schema_id = created.data.id
    await loadSchema(created.data.id)
    validationResult.value = null
    debouncedValidation()
  } catch (err) {
    alert('Failed to propose schema')
  } finally {
    proposingSchema.value = false
  }
}

watch(jsonContent, () => {
  if (formData.value.schema_id) {
    debouncedValidation()
  }
})

watch(schemaContent, () => {
  if (formData.value.schema_id) {
    debouncedValidation()
  }
})

watch(() => formData.value.schema_id, (newSchemaId) => {
  if (newSchemaId) {
    debouncedValidation()
  } else {
    validationResult.value = null
    validationErrors.value = []
  }
})

const debouncedValidation = () => {
  if (validationTimeout) {
    clearTimeout(validationTimeout)
  }
  validationTimeout = setTimeout(() => {
    autoValidate()
  }, 1000)
}

const autoValidate = async () => {
  if (!formData.value.schema_id) return
  
  try {
    const content = JSON.parse(jsonContent.value)
    validating.value = true
    const response = await api.validateJson(formData.value.schema_id, content)
    validationResult.value = response.data
    validationErrors.value = response.data.errors || []
  } catch (err) {
    if (err instanceof SyntaxError) {
      validationResult.value = null
      validationErrors.value = []
    }
  } finally {
    validating.value = false
  }
}

onMounted(async () => {
  await schemaStore.fetchSchemas()
  await documentStore.fetchDocuments()
  
  if (isEditing.value) {
    try {
      const response = await api.getDocument(route.params.id)
      formData.value.name = response.data.name
      formData.value.schema_id = response.data.schema_id
      jsonContent.value = JSON.stringify(response.data.content, null, 2)
      
      if (response.data.schema_id) {
        await loadSchema(response.data.schema_id)
        autoValidate()
      }
    } catch (err) {
      alert('Failed to load document')
      router.push('/')
    }
  }
})

const loadSchema = async (schemaId) => {
  if (!schemaId) {
    schemaContent.value = '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "type": "object"\n}'
    originalSchemaContent.value = ''
    schemaModified.value = false
    return
  }
  
  try {
    const response = await api.getSchema(schemaId)
    const schemaJson = JSON.stringify(response.data.schema, null, 2)
    schemaContent.value = schemaJson
    originalSchemaContent.value = schemaJson
    schemaModified.value = false
  } catch (err) {
    console.error('Failed to load schema:', err)
  }
}

const onSchemaChange = async () => {
  validationResult.value = null
  await loadSchema(formData.value.schema_id)
}

const onSchemaEdit = () => {
  schemaModified.value = schemaContent.value !== originalSchemaContent.value
}

const saveSchemaChanges = async () => {
  if (!formData.value.schema_id) return
  
  try {
    const schema = JSON.parse(schemaContent.value)
    const currentSchema = schemas.value.find(s => s.id === formData.value.schema_id)
    
    if (!currentSchema) return
    
    const data = {
      name: currentSchema.name,
      description: currentSchema.description,
      schema: schema
    }
    
    savingSchema.value = true
    schemaError.value = ''
    
    await api.updateSchema(formData.value.schema_id, data)
    
    originalSchemaContent.value = schemaContent.value
    schemaModified.value = false
    
    await schemaStore.fetchSchemas()
    
    alert('Schema saved successfully')
  } catch (err) {
    if (err instanceof SyntaxError) {
      schemaError.value = 'Invalid JSON syntax'
    } else {
      alert('Failed to save schema')
    }
  } finally {
    savingSchema.value = false
  }
}

const validateAgainstSchema = async () => {
  if (!formData.value.schema_id) return
  
  try {
    const content = JSON.parse(jsonContent.value)
    const schema = JSON.parse(schemaContent.value)
    
    const response = await api.validateJson(formData.value.schema_id, content)
    validationResult.value = response.data
    validationErrors.value = response.data.errors || []
  } catch (err) {
    if (err instanceof SyntaxError) {
      validationResult.value = { valid: false, errors: [{ message: 'Invalid JSON syntax' }] }
      validationErrors.value = [{ message: 'Invalid JSON syntax' }]
    } else {
      validationResult.value = { valid: false, errors: [{ message: 'Validation failed' }] }
      validationErrors.value = [{ message: 'Validation failed' }]
    }
  }
}

const insertDocument = async () => {
  if (!selectedDocumentToInsert.value) return
  
  try {
    const response = await api.getDocument(selectedDocumentToInsert.value)
    const insertContent = response.data.content
    
    try {
      const currentContent = JSON.parse(jsonContent.value)
      
      if (Array.isArray(currentContent) && Array.isArray(insertContent)) {
        currentContent.push(...insertContent)
        jsonContent.value = JSON.stringify(currentContent, null, 2)
      } else if (typeof currentContent === 'object' && !Array.isArray(currentContent) && 
                 typeof insertContent === 'object' && !Array.isArray(insertContent)) {
        Object.assign(currentContent, insertContent)
        jsonContent.value = JSON.stringify(currentContent, null, 2)
      } else {
        jsonContent.value = JSON.stringify(insertContent, null, 2)
      }
    } catch (parseErr) {
      jsonContent.value = JSON.stringify(insertContent, null, 2)
    }
    
    selectedDocumentToInsert.value = null
    validationResult.value = null
    validationErrors.value = []
    if (formData.value.schema_id) {
      debouncedValidation()
    }
  } catch (err) {
    alert('Failed to load document for insertion')
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
