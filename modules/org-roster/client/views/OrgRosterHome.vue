<template>
  <div>
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Team Directory</h2>
          <p class="text-sm text-gray-500">
            {{ filteredTeams.length }} team{{ filteredTeams.length !== 1 ? 's' : '' }}
            <span v-if="fetchedAt"> &middot; Updated {{ formatDate(fetchedAt) }}</span>
          </p>
        </div>
        <button
          v-if="selectedOrg"
          @click="goToOrgDashboard"
          class="px-4 py-2 text-sm font-medium text-primary-600 border border-primary-300 rounded-lg hover:bg-primary-50 transition-colors"
        >
          Org Dashboard
        </button>
      </div>
    </div>

    <!-- Org filter -->
    <div v-if="orgs.length > 0" class="mb-4">
      <OrgSelector :orgs="orgs" :modelValue="selectedOrg" @select="handleOrgSelect" />
    </div>

    <!-- Search + Sort -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <div class="relative flex-1">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search teams, PMs, components..."
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </div>
      <select
        v-model="sortBy"
        class="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        <option value="name">Sort: A-Z</option>
        <option value="headcount">Sort: Headcount</option>
        <option value="rfe">Sort: RFE Backlog</option>
      </select>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-700 text-sm">{{ error }}</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredTeams.length === 0 && !searchQuery" class="text-center py-12">
      <svg class="h-12 w-12 mx-auto text-gray-300 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <p class="text-gray-500">Roster data not found. Run Roster Sync in Team Tracker settings to populate team data.</p>
    </div>

    <!-- No search results -->
    <div v-else-if="filteredTeams.length === 0 && searchQuery" class="text-center py-12">
      <p class="text-gray-500">No teams match "{{ searchQuery }}"</p>
    </div>

    <!-- Team grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <TeamCard
        v-for="team in filteredTeams"
        :key="`${team.org}::${team.name}`"
        :team="team"
        @select="handleSelectTeam"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, inject, watch } from 'vue'
import OrgSelector from '../components/OrgSelector.vue'
import TeamCard from '../components/TeamCard.vue'
import { useOrgRoster } from '../composables/useOrgRoster'

const nav = inject('moduleNav')
const {
  orgs, selectedOrg, loading, error, fetchedAt,
  searchQuery, sortBy, filteredTeams,
  loadTeams, loadOrgs
} = useOrgRoster()

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString()
}

function handleOrgSelect(orgName) {
  selectedOrg.value = orgName
  loadTeams(orgName)
}

function handleSelectTeam(team) {
  nav.navigateTo('team-detail', { teamKey: `${team.org}::${team.name}` })
}

function goToOrgDashboard() {
  nav.navigateTo('org-dashboard', { org: selectedOrg.value })
}

onMounted(async () => {
  await Promise.all([loadOrgs(), loadTeams(selectedOrg.value)])
})
</script>
