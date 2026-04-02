import { ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'json-editor-theme'

function applyDarkClass(isDark) {
  document.documentElement.classList.toggle('dark', isDark)
}

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false)

  function init() {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'dark') {
      isDark.value = true
    } else if (stored === 'light') {
      isDark.value = false
    } else {
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyDarkClass(isDark.value)
  }

  function persist() {
    applyDarkClass(isDark.value)
    localStorage.setItem(STORAGE_KEY, isDark.value ? 'dark' : 'light')
  }

  function toggleTheme() {
    isDark.value = !isDark.value
    persist()
  }

  function setTheme(mode) {
    isDark.value = mode === 'dark'
    persist()
  }

  return { isDark, init, toggleTheme, setTheme }
})
