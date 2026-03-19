<template>
  <div class="max-w-3xl">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Settings</h2>
    <RosterSyncSettings @toast="(t) => $emit('toast', t)" />
  </div>
</template>

<script setup>
import RosterSyncSettings from './RosterSyncSettings.vue'

defineEmits(['toast'])
</script>
