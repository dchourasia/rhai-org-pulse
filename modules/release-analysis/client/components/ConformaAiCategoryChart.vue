<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { AI_CATEGORIES } from '../constants/conforma'
import ConformaHelpText from './ConformaHelpText.vue'

const props = defineProps({
  exceptions: { type: Array, default: () => [] },
  chartKey: { type: Number, default: 0 }
})

const categorized = computed(() => {
  const cats = {}
  for (const [key, info] of Object.entries(AI_CATEGORIES)) {
    cats[key] = { ...info, fbc: 0, registry: 0 }
  }
  for (const ex of props.exceptions) {
    if (ex.aiCategory && cats[ex.aiCategory]) {
      if (ex.policyFile === 'fbc') cats[ex.aiCategory].fbc++
      else cats[ex.aiCategory].registry++
    }
  }
  return cats
})

const quickFixCount = computed(() => {
  const c = categorized.value.quick_fix
  return c ? c.fbc + c.registry : 0
})

const alreadyFixedCount = computed(() => {
  const c = categorized.value.already_fixed
  return c ? c.fbc + c.registry : 0
})

const chartData = computed(() => {
  const entries = Object.entries(AI_CATEGORIES)
  return {
    labels: entries.map(([, info]) => info.label),
    datasets: [
      {
        label: 'FBC',
        data: entries.map(([key]) => categorized.value[key]?.fbc || 0),
        backgroundColor: 'rgba(59,130,246,0.75)',
        borderColor: 'rgb(59,130,246)',
        borderWidth: 1,
        borderRadius: 3
      },
      {
        label: 'Components',
        data: entries.map(([key]) => categorized.value[key]?.registry || 0),
        backgroundColor: 'rgba(16,185,129,0.75)',
        borderColor: 'rgb(16,185,129)',
        borderWidth: 1,
        borderRadius: 3
      }
    ]
  }
})

const chartOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12 } },
    tooltip: { mode: 'index' }
  },
  scales: {
    x: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, grid: { color: 'rgba(156,163,175,0.15)' } },
    y: { stacked: true, grid: { display: false } }
  }
}

const hasCategorizedData = computed(() =>
  props.exceptions.some(e => e.aiCategory)
)
</script>

<template>
  <div v-if="hasCategorizedData" class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/60 p-5">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">AI Exception Analysis</h3>
      <ConformaHelpText
        good="Many exceptions are 'Always Expected' with few quick fixes remaining"
        attention="'Quick Fix' and 'Already Fixed' exceptions should be resolved to reduce exception count"
        action="Review quick fixes first — they are the easiest path to reducing exceptions"
      />
    </div>

    <!-- Quick Wins summary -->
    <div class="flex flex-wrap gap-3 mb-4">
      <div v-if="quickFixCount > 0" class="flex items-center gap-2 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg px-4 py-2">
        <span class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{{ quickFixCount }}</span>
        <span class="text-xs text-emerald-700 dark:text-emerald-300">Quick Fixes available</span>
      </div>
      <div v-if="alreadyFixedCount > 0" class="flex items-center gap-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg px-4 py-2">
        <span class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ alreadyFixedCount }}</span>
        <span class="text-xs text-purple-700 dark:text-purple-300">Already Fixed (removable)</span>
      </div>
    </div>

    <div style="height: 200px; position: relative;">
      <Bar :key="`ai-cat-${chartKey}`" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
