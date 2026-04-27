<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

defineProps({
  text: { type: String, required: true }
})

const open = ref(false)
const el = ref(null)

function toggle(e) {
  e.stopPropagation()
  open.value = !open.value
}

function onClickOutside(e) {
  if (el.value && !el.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <span class="relative inline-flex" ref="el">
    <button
      @click="toggle"
      class="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
      aria-label="More info"
    >
      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
      </svg>
    </button>
    <Transition name="fade">
      <div
        v-if="open"
        class="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 px-3 py-2 text-xs text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg"
      >
        {{ text }}
        <div class="absolute top-full left-1/2 -translate-x-1/2 -mt-px">
          <div class="w-2 h-2 bg-white dark:bg-gray-700 border-r border-b border-gray-200 dark:border-gray-600 rotate-45 -translate-y-1" />
        </div>
      </div>
    </Transition>
  </span>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
