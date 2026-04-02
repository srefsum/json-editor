<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-3xl font-semibold text-gray-900 dark:text-gray-100">JSON Documents</h1>
        <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
          A list of all JSON documents in your collection.
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
        <router-link
          to="/documents/new"
          class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900"
        >
          New Document
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="mt-8 text-center">
      <div class="text-gray-500 dark:text-gray-400">Loading...</div>
    </div>

    <div v-else-if="error" class="mt-8 text-center text-red-600 dark:text-red-400">
      Error: {{ error }}
    </div>

    <div v-else-if="documents.length === 0" class="mt-8 text-center text-gray-500 dark:text-gray-400">
      No documents found. Create your first document!
    </div>

    <div v-else class="mt-8 flex flex-col">
      <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 dark:ring-gray-700 md:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300 dark:divide-gray-600 bg-white dark:bg-gray-800">
              <thead class="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100 sm:pl-6">
                    Name
                  </th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                    Created
                  </th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                    Updated
                  </th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-600 bg-white dark:bg-gray-800">
                <tr v-for="document in documents" :key="document.id">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 dark:text-gray-100 sm:pl-6">
                    {{ document.name }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {{ formatDate(document.created_at) }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {{ formatDate(document.updated_at) }}
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <router-link
                      :to="`/documents/${document.id}`"
                      class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300 mr-4"
                    >
                      Edit
                    </router-link>
                    <button
                      type="button"
                      @click="openCopyModal(document)"
                      class="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white mr-4"
                    >
                      Copy
                    </button>
                    <button
                      @click="handleDelete(document.id)"
                      class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '../stores/documents'
import { useSchemaStore } from '../stores/schemas'
import { storeToRefs } from 'pinia'
import CopyDocumentModal from '../components/CopyDocumentModal.vue'

const router = useRouter()
const documentStore = useDocumentStore()
const schemaStore = useSchemaStore()
const { documents, loading, error } = storeToRefs(documentStore)

const copyModalOpen = ref(false)
const copyDefaultName = ref('')
const copySourceId = ref(null)
const copySubmitting = ref(false)

onMounted(() => {
  documentStore.fetchDocuments()
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const handleDelete = async (id) => {
  if (confirm('Are you sure you want to delete this document?')) {
    try {
      await documentStore.deleteDocument(id)
    } catch (err) {
      alert('Failed to delete document')
    }
  }
}

const openCopyModal = (document) => {
  copySourceId.value = document.id
  copyDefaultName.value = `${document.name} (copy)`
  copyModalOpen.value = true
}

const onCopySubmit = async (name) => {
  if (!copySourceId.value) return
  copySubmitting.value = true
  try {
    const created = await documentStore.copyDocument(copySourceId.value, { name })
    await schemaStore.fetchSchemas()
    copyModalOpen.value = false
    router.push(`/documents/${created.id}`)
  } catch (err) {
    alert('Failed to copy document')
  } finally {
    copySubmitting.value = false
  }
}
</script>
