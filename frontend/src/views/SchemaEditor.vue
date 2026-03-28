<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="mb-6">
      <router-link to="/schemas" class="text-indigo-600 hover:text-indigo-900">
        ← Back to Schemas
      </router-link>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h2 class="text-2xl font-semibold text-gray-900 mb-6">
          {{ isEditing ? 'Edit Schema' : 'New Schema' }}
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700">
              Schema Name
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
            <label for="description" class="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              v-model="formData.description"
              id="description"
              rows="2"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              JSON Schema
            </label>
            <JsonEditor v-model="schemaContent" :error="schemaError" />
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <router-link
              to="/schemas"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </router-link>
            <button
              type="submit"
              :disabled="saving || !!schemaError"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
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

const route = useRoute()
const router = useRouter()

const isEditing = computed(() => !!route.params.id)

const formData = ref({
  name: '',
  description: ''
})

const schemaContent = ref('{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "type": "object"\n}')
const schemaError = ref('')
const saving = ref(false)

onMounted(async () => {
  if (isEditing.value) {
    try {
      const response = await api.getSchema(route.params.id)
      formData.value.name = response.data.name
      formData.value.description = response.data.description || ''
      schemaContent.value = JSON.stringify(response.data.schema, null, 2)
    } catch (err) {
      alert('Failed to load schema')
      router.push('/schemas')
    }
  }
})

const handleSubmit = async () => {
  try {
    const schema = JSON.parse(schemaContent.value)
    
    const data = {
      name: formData.value.name,
      description: formData.value.description || null,
      schema: schema
    }
    
    saving.value = true
    
    if (isEditing.value) {
      await api.updateSchema(route.params.id, data)
    } else {
      await api.createSchema(data)
    }
    
    router.push('/schemas')
  } catch (err) {
    if (err instanceof SyntaxError) {
      schemaError.value = 'Invalid JSON syntax'
    } else {
      alert('Failed to save schema')
    }
  } finally {
    saving.value = false
  }
}
</script>
