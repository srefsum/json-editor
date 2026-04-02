<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-3xl font-semibold text-gray-900 dark:text-gray-100">JSON Schemas</h1>
        <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Manage your JSON schema definitions.
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
        <router-link
          to="/schemas/new"
          class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900"
        >
          New Schema
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="mt-8 text-center">
      <div class="text-gray-500 dark:text-gray-400">Loading...</div>
    </div>

    <div v-else-if="error" class="mt-8 text-center text-red-600 dark:text-red-400">
      Error: {{ error }}
    </div>

    <div v-else-if="schemas.length === 0" class="mt-8 text-center text-gray-500 dark:text-gray-400">
      No schemas found. Create your first schema!
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
                    Description
                  </th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                    Created
                  </th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-600 bg-white dark:bg-gray-800">
                <tr v-for="schema in schemas" :key="schema.id">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 dark:text-gray-100 sm:pl-6">
                    {{ schema.name }}
                  </td>
                  <td class="px-3 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {{ schema.description || '-' }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {{ formatDate(schema.created_at) }}
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <router-link
                      :to="`/schemas/${schema.id}`"
                      class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300 mr-4"
                    >
                      Edit
                    </router-link>
                    <button
                      @click="handleDelete(schema.id)"
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
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSchemaStore } from '../stores/schemas'
import { storeToRefs } from 'pinia'

const schemaStore = useSchemaStore()
const { schemas, loading, error } = storeToRefs(schemaStore)

onMounted(() => {
  schemaStore.fetchSchemas()
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const handleDelete = async (id) => {
  if (confirm('Are you sure you want to delete this schema?')) {
    try {
      await schemaStore.deleteSchema(id)
    } catch (err) {
      alert('Failed to delete schema')
    }
  }
}
</script>
