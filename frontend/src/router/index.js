import { createRouter, createWebHistory } from 'vue-router'
import DocumentsList from '../views/DocumentsList.vue'
import DocumentEditor from '../views/DocumentEditor.vue'
import SchemasList from '../views/SchemasList.vue'
import SchemaEditor from '../views/SchemaEditor.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'documents',
      component: DocumentsList
    },
    {
      path: '/documents/new',
      name: 'document-create',
      component: DocumentEditor
    },
    {
      path: '/documents/:id',
      name: 'document-edit',
      component: DocumentEditor
    },
    {
      path: '/schemas',
      name: 'schemas',
      component: SchemasList
    },
    {
      path: '/schemas/new',
      name: 'schema-create',
      component: SchemaEditor
    },
    {
      path: '/schemas/:id',
      name: 'schema-edit',
      component: SchemaEditor
    }
  ]
})

export default router
