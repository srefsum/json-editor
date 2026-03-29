import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  getDocuments() {
    return apiClient.get('/api/documents')
  },
  
  getDocument(id) {
    return apiClient.get(`/api/documents/${id}`)
  },
  
  createDocument(data) {
    return apiClient.post('/api/documents', data)
  },
  
  updateDocument(id, data) {
    return apiClient.put(`/api/documents/${id}`, data)
  },
  
  deleteDocument(id) {
    return apiClient.delete(`/api/documents/${id}`)
  },

  copyDocument(id, data) {
    return apiClient.post(`/api/documents/${id}/copy`, data)
  },
  
  getSchemas() {
    return apiClient.get('/api/schemas')
  },

  proposeSchemaFromSample(body) {
    return apiClient.post('/api/schemas/propose', body)
  },
  
  getSchema(id) {
    return apiClient.get(`/api/schemas/${id}`)
  },
  
  createSchema(data) {
    return apiClient.post('/api/schemas', data)
  },
  
  updateSchema(id, data) {
    return apiClient.put(`/api/schemas/${id}`, data)
  },
  
  deleteSchema(id) {
    return apiClient.delete(`/api/schemas/${id}`)
  },
  
  validateJson(schemaId, content) {
    return apiClient.post(`/api/schemas/${schemaId}/validate`, { content })
  }
}
