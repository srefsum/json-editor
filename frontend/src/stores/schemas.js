import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useSchemaStore = defineStore('schemas', () => {
  const schemas = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchSchemas() {
    loading.value = true
    error.value = null
    try {
      const response = await api.getSchemas()
      schemas.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching schemas:', err)
    } finally {
      loading.value = false
    }
  }

  async function deleteSchema(id) {
    try {
      await api.deleteSchema(id)
      schemas.value = schemas.value.filter(schema => schema.id !== id)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return { schemas, loading, error, fetchSchemas, deleteSchema }
})
