<template>
  <div>
    <ul class="divide-y divide-gray-100">
      <li
        v-for="comp in components"
        :key="comp"
        class="flex items-center justify-between py-2"
      >
        <span class="text-sm text-gray-800">{{ comp }}</span>
        <span
          v-if="rfeCounts[comp]"
          class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800"
        >
          {{ rfeCounts[comp] }} RFEs
        </span>
      </li>
    </ul>
    <div v-if="components.length === 0" class="text-sm text-gray-500 py-2">
      No components assigned.
    </div>
  </div>
</template>

<script setup>
defineProps({
  components: { type: Array, required: true },
  rfeCounts: { type: Object, default: () => ({}) }
})
</script>
