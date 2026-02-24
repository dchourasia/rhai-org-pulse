<template>
  <div class="container mx-auto px-6 py-6">
    <div class="flex items-center gap-3 mb-6">
      <button
        @click="$emit('back')"
        class="text-primary-600 hover:text-primary-800 font-medium flex items-center gap-1"
      >
        <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </button>
    </div>

    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-6">Board Settings</h2>

      <div class="flex items-center gap-3 mb-6">
        <button
          @click="handleDiscover"
          :disabled="isDiscovering"
          class="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md font-medium hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ isDiscovering ? 'Discovering...' : 'Discover Boards' }}
        </button>
        <button
          @click="handleSave"
          :disabled="isSaving"
          class="px-4 py-2 text-sm bg-primary-600 text-white rounded-md font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>

      <div v-if="teams.length === 0" class="text-center py-12 text-gray-500">
        <p class="text-lg">No boards found.</p>
        <p>Click "Discover Boards" to fetch the board list from Jira.</p>
      </div>

      <div v-else>
        <div class="flex items-center gap-3 mb-3 text-sm">
          <button
            @click="selectAll"
            class="text-primary-600 hover:text-primary-800 font-medium"
          >Select All</button>
          <span class="text-gray-300">|</span>
          <button
            @click="deselectAll"
            class="text-primary-600 hover:text-primary-800 font-medium"
          >Deselect All</button>
          <span class="text-gray-400 ml-2">{{ enabledCount }} of {{ teams.length }} enabled</span>
        </div>
        <div class="divide-y divide-gray-200">
          <template v-for="group in groupedTeams" :key="group.boardId">
            <div
              v-for="(team, idx) in group.entries"
              :key="team.teamId || `${team.boardId}-${idx}`"
              :class="[
                'py-3 px-3 rounded-md hover:bg-primary-50 transition-colors',
                team.stale ? 'opacity-60' : '',
                idx > 0 ? 'ml-6' : ''
              ]"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-900">{{ team.displayName || team.boardName }}</span>
                    <span class="ml-2 text-sm text-gray-500">ID: {{ team.boardId }}</span>
                    <span
                      v-if="team.sprintFilter"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700"
                    >
                      {{ team.sprintFilter }}
                    </span>
                    <span
                      v-if="team.stale"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600"
                    >
                      Inactive
                    </span>
                  </div>
                  <p v-if="team.stale" class="text-xs text-gray-400 mt-0.5">
                    {{ team.lastSprintEndDate ? `Last sprint ended ${formatRelativeDate(team.lastSprintEndDate)}` : 'No sprints found' }}
                  </p>
                  <div class="flex items-center gap-2 mt-1.5">
                    <input
                      v-model="team.sprintFilter"
                      type="text"
                      class="px-2 py-1 text-xs border border-gray-300 rounded w-48 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Sprint name filter..."
                    />
                    <button
                      @click="addSubTeam(team.boardId, team.boardName)"
                      class="text-xs text-primary-600 hover:text-primary-800 font-medium whitespace-nowrap"
                    >+ Add Sub-team</button>
                    <button
                      v-if="team.sprintFilter && group.entries.length > 1"
                      @click="removeSubTeam(team)"
                      class="text-xs text-red-500 hover:text-red-700 font-medium whitespace-nowrap"
                    >Remove</button>
                  </div>
                </div>
                <label class="relative inline-flex items-center cursor-pointer ml-3">
                  <input
                    type="checkbox"
                    :checked="team.enabled"
                    @change="toggleTeam(team)"
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTeams, saveTeams, discoverBoards } from '../services/api'

const emit = defineEmits(['back', 'saved'])

const teams = ref([])
const isSaving = ref(false)
const isDiscovering = ref(false)

onMounted(() => loadTeams())

function getEffectiveTeamId(team) {
  if (team.teamId) return team.teamId
  if (team.sprintFilter) {
    return `${team.boardId}_${team.sprintFilter.toLowerCase().replace(/\s+/g, '-')}`
  }
  return String(team.boardId)
}

const groupedTeams = computed(() => {
  const groups = new Map()
  for (const team of sortedTeams.value) {
    if (!groups.has(team.boardId)) {
      groups.set(team.boardId, { boardId: team.boardId, entries: [] })
    }
    groups.get(team.boardId).entries.push(team)
  }
  return [...groups.values()]
})

const sortedTeams = computed(() =>
  [...teams.value].sort((a, b) => {
    if (a.stale && !b.stale) return 1
    if (!a.stale && b.stale) return -1
    if (a.boardId !== b.boardId) return 0
    // Within same board: entries without filter first
    if (!a.sprintFilter && b.sprintFilter) return -1
    if (a.sprintFilter && !b.sprintFilter) return 1
    return 0
  })
)

function formatRelativeDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays < 30) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
  const diffMonths = Math.floor(diffDays / 30)
  if (diffMonths < 12) return `${diffMonths} month${diffMonths !== 1 ? 's' : ''} ago`
  const diffYears = Math.floor(diffMonths / 12)
  return `${diffYears} year${diffYears !== 1 ? 's' : ''} ago`
}

async function loadTeams() {
  try {
    const data = await getTeams()
    teams.value = (data.teams || []).map(t => ({ ...t }))
  } catch (error) {
    console.error('Failed to load teams:', error)
    teams.value = []
  }
}

const enabledCount = computed(() => teams.value.filter(t => t.enabled).length)

function toggleTeam(team) {
  team.enabled = !team.enabled
}

function addSubTeam(boardId, boardName) {
  teams.value.push({
    boardId,
    boardName: boardName,
    displayName: '',
    sprintFilter: '',
    enabled: true,
    stale: false,
    manuallyConfigured: true
  })
}

function removeSubTeam(team) {
  const idx = teams.value.indexOf(team)
  if (idx !== -1) teams.value.splice(idx, 1)
}

function selectAll() {
  teams.value.forEach(t => { t.enabled = true })
}

function deselectAll() {
  teams.value.forEach(t => { t.enabled = false })
}

async function handleSave() {
  isSaving.value = true
  try {
    // Auto-generate teamId for entries with sprintFilter
    const teamsToSave = teams.value.map(t => {
      const copy = { ...t }
      // Trim whitespace from filter
      if (copy.sprintFilter) copy.sprintFilter = copy.sprintFilter.trim()
      if (copy.sprintFilter) {
        // Always regenerate teamId from current filter
        copy.teamId = `${copy.boardId}_${copy.sprintFilter.toLowerCase().replace(/\s+/g, '-')}`
      } else {
        delete copy.teamId
        delete copy.sprintFilter
      }
      return copy
    })
    await saveTeams(teamsToSave)
    // Reload to get the saved state
    teams.value = teamsToSave.map(t => ({ ...t }))
    emit('saved')
  } catch (error) {
    console.error('Failed to save teams:', error)
  } finally {
    isSaving.value = false
  }
}

async function handleDiscover() {
  isDiscovering.value = true
  try {
    await discoverBoards()
    await loadTeams()
  } catch (error) {
    console.error('Failed to discover boards:', error)
  } finally {
    isDiscovering.value = false
  }
}
</script>
