import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useDocumentStore = defineStore('documents', () => {
  const documents = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchDocuments() {
    loading.value = true
    error.value = null
    try {
      const response = await api.getDocuments()
      documents.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching documents:', err)
    } finally {
      loading.value = false
    }
  }

  async function deleteDocument(id) {
    try {
      await api.deleteDocument(id)
      documents.value = documents.value.filter(doc => doc.id !== id)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return { documents, loading, error, fetchDocuments, deleteDocument }
})
