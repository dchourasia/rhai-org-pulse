<template>
  <div v-if="visible" class="bg-white border-b border-gray-200 px-6 py-3 shadow-sm">
    <!-- Board-level progress -->
    <div class="flex items-center justify-between text-sm mb-1">
      <span class="text-gray-700 font-medium truncate mr-4">Refreshing: {{ currentBoard || 'Starting...' }}</span>
      <span class="text-gray-500 whitespace-nowrap">{{ completedBoards }} / {{ totalBoards }} boards</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
      <div
        class="bg-primary-600 h-2.5 rounded-full transition-all duration-300"
        :style="{ width: boardPercent + '%' }"
      ></div>
    </div>

    <!-- Sprint-level progress -->
    <div class="flex items-center justify-between text-xs mb-1">
      <span class="text-gray-500 truncate mr-4">{{ currentSprint || '' }}</span>
      <span v-if="totalSprints > 0" class="text-gray-400 whitespace-nowrap">{{ completedSprints }} / {{ totalSprints }} sprints</span>
    </div>
    <div class="w-full bg-gray-100 rounded-full h-1.5">
      <div
        class="bg-primary-400 h-1.5 rounded-full transition-all duration-300"
        :style="{ width: sprintPercent + '%' }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  totalBoards: { type: Number, default: 0 },
  completedBoards: { type: Number, default: 0 },
  currentBoard: { type: String, default: '' },
  totalSprints: { type: Number, default: 0 },
  completedSprints: { type: Number, default: 0 },
  currentSprint: { type: String, default: '' }
})

const boardPercent = computed(() => {
  if (props.totalBoards === 0) return 0
  return Math.round((props.completedBoards / props.totalBoards) * 100)
})

const sprintPercent = computed(() => {
  if (props.totalSprints === 0) return 0
  return Math.round((props.completedSprints / props.totalSprints) * 100)
})
</script>
