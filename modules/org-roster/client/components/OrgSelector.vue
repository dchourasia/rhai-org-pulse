<template>
  <div class="flex flex-wrap gap-2">
    <button
      @click="$emit('select', null)"
      class="px-4 py-2 rounded-lg text-sm font-medium transition-colors border"
      :class="!modelValue
        ? 'bg-primary-600 text-white border-primary-600'
        : 'bg-white text-gray-700 border-gray-300 hover:border-primary-300 hover:bg-primary-50'"
    >
      All
    </button>
    <button
      v-for="org in orgs"
      :key="org.name"
      @click="$emit('select', org.name)"
      class="px-4 py-2 rounded-lg text-sm font-medium transition-colors border"
      :class="modelValue === org.name
        ? 'bg-primary-600 text-white border-primary-600'
        : 'bg-white text-gray-700 border-gray-300 hover:border-primary-300 hover:bg-primary-50'"
    >
      {{ org.name }}
      <span class="ml-1 text-xs opacity-75">({{ org.teamCount }})</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  orgs: { type: Array, required: true },
  modelValue: { type: String, default: null }
})
defineEmits(['select'])
</script>
