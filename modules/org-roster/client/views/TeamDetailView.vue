<template>
  <div>
    <!-- Back button -->
    <button
      @click="nav.goBack()"
      class="flex items-center gap-1 text-sm text-gray-500 hover:text-primary-600 mb-4"
    >
      <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back to directory
    </button>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-700 text-sm">{{ error }}</p>
    </div>

    <template v-else-if="team">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">{{ team.name }}</h2>
            <p class="text-sm text-gray-500 mt-1">{{ team.org }}</p>
          </div>
          <RfeBacklogBadge :count="team.rfeCount || 0" />
        </div>

        <div class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <!-- PMs -->
          <div v-if="team.pms && team.pms.length > 0">
            <p class="text-xs text-gray-500 uppercase font-medium mb-1">Product Manager</p>
            <p class="text-sm text-gray-800">{{ team.pms.join(', ') }}</p>
          </div>
          <!-- Eng Leads -->
          <div v-if="team.staffEngineers && team.staffEngineers.length > 0">
            <p class="text-xs text-gray-500 uppercase font-medium mb-1">Engineering Lead</p>
            <p class="text-sm text-gray-800">{{ team.staffEngineers.join(', ') }}</p>
          </div>
          <!-- Board Links -->
          <div v-if="boardLinks.length > 0">
            <p class="text-xs text-gray-500 uppercase font-medium mb-1">Jira Board{{ boardLinks.length > 1 ? 's' : '' }}</p>
            <div class="flex flex-col gap-1">
              <a
                v-for="(board, i) in boardLinks"
                :key="i"
                :href="board.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm text-primary-600 hover:underline truncate"
              >
                {{ board.label }}
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Headcount by Role -->
      <div v-if="team.headcount" class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Headcount by Role</h3>
        <HeadcountChart :headcount="team.headcount" />
      </div>

      <!-- Components -->
      <div v-if="team.components && team.components.length > 0" class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Components</h3>
        <ComponentList :components="team.components" :rfeCounts="rfeCounts" />
      </div>

      <!-- Team Members -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          Team Members
          <span class="text-sm font-normal text-gray-500 ml-2">{{ members.length }} member{{ members.length !== 1 ? 's' : '' }}</span>
        </h3>
        <TeamMembersTable :members="members" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import HeadcountChart from '../components/HeadcountChart.vue'
import TeamMembersTable from '../components/TeamMembersTable.vue'
import ComponentList from '../components/ComponentList.vue'
import RfeBacklogBadge from '../components/RfeBacklogBadge.vue'
import { useOrgRoster } from '../composables/useOrgRoster'

const nav = inject('moduleNav')
const { loadTeamDetail, loadTeamMembers, loadRfeBacklog } = useOrgRoster()

const team = ref(null)
const members = ref([])
const rfeCounts = ref({})
const loading = ref(true)
const error = ref(null)

const boardLinks = computed(() => {
  if (!team.value) return []
  // Use enriched boards array if available, fall back to boardUrls
  const boards = team.value.boards || (team.value.boardUrls || []).map(url => ({ url, name: null }))
  return boards.map((board, i) => ({
    url: board.url,
    label: board.name || fallbackBoardLabel(board.url, i)
  }))
})

function fallbackBoardLabel(url, index) {
  try {
    const u = new URL(url)
    return `Board ${index + 1} — ${u.hostname}`
  } catch {
    return `Board ${index + 1}`
  }
}

onMounted(async () => {
  const teamKey = nav.params.value?.teamKey
  if (!teamKey) {
    error.value = 'No team specified'
    loading.value = false
    return
  }

  try {
    const [teamData, membersData] = await Promise.all([
      loadTeamDetail(teamKey),
      loadTeamMembers(teamKey),
    ])
    team.value = teamData
    members.value = membersData.members || []

    // Load RFE data for components
    if (teamData.components && teamData.components.length > 0) {
      try {
        const rfeData = await loadRfeBacklog()
        const counts = {}
        for (const comp of teamData.components) {
          if (rfeData.byComponent?.[comp]) {
            counts[comp] = rfeData.byComponent[comp].count
          }
        }
        rfeCounts.value = counts
      } catch {
        // RFE data is optional
      }
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>
