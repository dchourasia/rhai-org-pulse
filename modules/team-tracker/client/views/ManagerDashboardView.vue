<template>
  <div class="max-w-5xl mx-auto px-4 py-6">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">My Teams</h2>

    <!-- Loading state -->
    <div v-if="loading" class="text-center py-12 text-gray-500 dark:text-gray-400">
      Loading dashboard...
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-12 text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <!-- Empty state: no registry identity -->
    <div v-else-if="reason === 'no-registry-identity'" class="text-center py-12 text-gray-500 dark:text-gray-400">
      <p class="text-lg font-medium mb-2">No Registry Identity</p>
      <p>Your account is not linked to the people registry. In local dev, this typically means your email address does not match any person in the registry.</p>
    </div>

    <!-- Empty state: no direct reports -->
    <div v-else-if="reason === 'no-direct-reports'" class="text-center py-12 text-gray-500 dark:text-gray-400">
      <p class="text-lg font-medium mb-2">No Direct Reports</p>
      <p>You have no direct reports in the system.</p>
    </div>

    <!-- Dashboard content -->
    <template v-else>
      <!-- Tabs -->
      <div class="flex space-x-4 border-b border-gray-200 dark:border-gray-700 mb-6">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="pb-2 px-1 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === tab.id
            ? 'border-primary-600 text-primary-600'
            : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'"
        >
          {{ tab.label }}
          <span class="ml-1 text-xs text-gray-400 dark:text-gray-500">({{ tab.count }})</span>
        </button>
      </div>

      <!-- My Reports tab -->
      <div v-if="activeTab === 'reports'">
        <div v-if="directReports.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No direct reports found.
        </div>
        <div v-else>
          <!-- Edit mode controls -->
          <div class="flex items-center justify-end gap-3 mb-3">
            <template v-if="bulkEditing">
              <span v-if="pendingChangeCount > 0" class="text-xs text-amber-600 dark:text-amber-400">{{ pendingChangeCount }} unsaved change{{ pendingChangeCount !== 1 ? 's' : '' }}</span>
              <button
                class="px-3 py-1.5 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50 transition-colors"
                :disabled="saving || pendingChangeCount === 0"
                @click="saveAllChanges"
              >
                {{ saving ? 'Saving...' : `Save All (${pendingChangeCount})` }}
              </button>
              <button
                class="px-3 py-1.5 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors"
                :disabled="saving"
                @click="cancelBulkEdit"
              >
                Cancel
              </button>
            </template>
            <button
              v-else
              class="px-3 py-1.5 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors flex items-center gap-1.5"
              @click="enterBulkEdit"
            >
              <Pencil class="w-3.5 h-3.5" />
              Edit All Fields
            </button>
          </div>

          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" :class="bulkEditing ? 'text-gray-400 dark:text-gray-500' : 'text-gray-500 dark:text-gray-400'">Name</th>
                <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" :class="bulkEditing ? 'text-gray-400 dark:text-gray-500' : 'text-gray-500 dark:text-gray-400'">Title</th>
                <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" :class="bulkEditing ? 'text-primary-700 dark:text-primary-300 bg-blue-50 dark:bg-blue-900/30' : 'text-gray-500 dark:text-gray-400'">Team(s)</th>
                <th
                  v-for="field in visiblePersonFields"
                  :key="field.id"
                  class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider"
                  :class="bulkEditing ? 'text-primary-700 dark:text-primary-300 bg-blue-50 dark:bg-blue-900/30' : 'text-gray-500 dark:text-gray-400'"
                >{{ field.label }}</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="report in directReports"
                :key="report.uid"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/50"
              >
                <td class="px-4 py-3 text-sm whitespace-nowrap" :class="bulkEditing ? 'opacity-50' : ''">
                  <button
                    @click="navigateToPersonDetail(report.uid)"
                    class="text-primary-600 dark:text-primary-400 hover:underline font-medium"
                  >
                    {{ report.name }}
                  </button>
                </td>
                <td class="px-4 py-3 text-sm whitespace-nowrap" :class="bulkEditing ? 'opacity-50 text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-400'">
                  {{ report.title || '—' }}
                </td>
                <td class="px-4 py-3 text-sm" :class="bulkEditing ? 'bg-blue-50 dark:bg-blue-900/20' : ''">
                  <!-- BULK EDIT MODE -->
                  <div v-if="bulkEditing" class="min-w-[140px]">
                    <ConstrainedAutocomplete
                      :model-value="getBulkTeamValue(report.uid)"
                      :options="allOrgTeamNames"
                      :multi-value="true"
                      @update:model-value="setBulkTeamValue(report.uid, $event)"
                    />
                  </div>

                  <!-- SINGLE-CELL EDIT MODE -->
                  <div v-else-if="editingTeamUid === report.uid" class="relative min-w-[160px]">
                    <ConstrainedAutocomplete
                      :model-value="editTeamValue"
                      :options="allOrgTeamNames"
                      :multi-value="true"
                      @update:model-value="editTeamValue = $event"
                    />
                    <div class="flex gap-1.5 mt-1">
                      <button class="px-2 py-0.5 text-xs font-medium text-white bg-primary-600 rounded hover:bg-primary-700 disabled:opacity-50" :disabled="saving" @click="saveTeamEdit(report.uid)">Save</button>
                      <button class="px-2 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600" @click="cancelTeamEdit">Cancel</button>
                    </div>
                  </div>

                  <!-- DISPLAY MODE -->
                  <div v-else class="group flex items-center gap-1.5 cursor-pointer" @click="startTeamEdit(report)">
                    <div v-if="report.teamIds.length > 0">
                      <template v-for="(id, idx) in report.teamIds" :key="id">
                        <span v-if="idx > 0" class="text-gray-400 dark:text-gray-500">, </span>
                        <button
                          v-if="teamById[id]"
                          @click.stop="navigateToTeamDetail(teamById[id])"
                          class="text-primary-600 dark:text-primary-400 hover:underline"
                        >{{ teamById[id].name }}</button>
                        <span v-else class="text-gray-600 dark:text-gray-400">{{ id }}</span>
                      </template>
                    </div>
                    <span v-else class="text-amber-500 dark:text-amber-400">Unassigned</span>
                    <svg class="h-3 w-3 text-gray-400 dark:text-gray-500 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                  </div>
                </td>
                <!-- Field cells -->
                <td
                  v-for="field in visiblePersonFields"
                  :key="field.id"
                  class="px-4 py-3 text-sm"
                  :class="bulkEditing ? 'bg-blue-50 dark:bg-blue-900/20' : ''"
                >
                  <!-- BULK EDIT MODE: all cells are editors -->
                  <div v-if="bulkEditing" class="min-w-[140px]">
                    <ConstrainedAutocomplete
                      v-if="field.type === 'constrained' && field.allowedValues"
                      :model-value="getBulkValue(report.uid, field)"
                      :options="field.allowedValues"
                      :multi-value="!!field.multiValue"
                      @update:model-value="setBulkValue(report.uid, field.id, $event)"
                    />
                    <PersonAutocomplete
                      v-else-if="field.type === 'person-reference-linked'"
                      :model-value="getBulkValue(report.uid, field)"
                      :people="allPeopleForEditor"
                      @update:model-value="setBulkValue(report.uid, field.id, $event)"
                    />
                    <input
                      v-else
                      :value="getBulkValue(report.uid, field)"
                      class="w-full rounded border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 text-sm"
                      @input="setBulkValue(report.uid, field.id, $event.target.value)"
                    >
                  </div>

                  <!-- SINGLE-CELL EDIT MODE -->
                  <div v-else-if="editingCell.uid === report.uid && editingCell.fieldId === field.id" class="relative min-w-[160px]">
                    <ConstrainedAutocomplete
                      v-if="field.type === 'constrained' && field.allowedValues"
                      :model-value="editValue"
                      :options="field.allowedValues"
                      :multi-value="!!field.multiValue"
                      @update:model-value="editValue = $event"
                      @save="saveCell(report.uid, field.id)"
                      @cancel="cancelEdit"
                    />
                    <PersonAutocomplete
                      v-else-if="field.type === 'person-reference-linked'"
                      :model-value="editValue"
                      :people="allPeopleForEditor"
                      @update:model-value="editValue = $event"
                      @save="saveCell(report.uid, field.id)"
                      @cancel="cancelEdit"
                    />
                    <input
                      v-else
                      v-model="editValue"
                      class="w-full rounded border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 text-sm"
                      @keyup.enter="saveCell(report.uid, field.id)"
                      @keyup.escape="cancelEdit"
                    >
                    <div class="flex gap-1.5 mt-1">
                      <button class="px-2 py-0.5 text-xs font-medium text-white bg-primary-600 rounded hover:bg-primary-700 disabled:opacity-50" :disabled="saving" @click="saveCell(report.uid, field.id)">Save</button>
                      <button class="px-2 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600" @click="cancelEdit">Cancel</button>
                    </div>
                  </div>

                  <!-- DISPLAY MODE -->
                  <div v-else class="group flex items-center gap-1.5 cursor-pointer" @click="startCellEdit(report, field)">
                    <template v-if="field.multiValue && field.type === 'constrained'">
                      <div class="flex flex-wrap gap-1">
                        <span
                          v-for="v in displayMultiValues(report, field)"
                          :key="v"
                          class="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                        >{{ v }}</span>
                        <span v-if="displayMultiValues(report, field).length === 0" class="text-gray-400 dark:text-gray-500">—</span>
                      </div>
                    </template>
                    <template v-else-if="field.type === 'person-reference-linked'">
                      <span v-if="resolvePersonName(report.customFields[field.id])" class="text-primary-600 dark:text-primary-400">{{ resolvePersonName(report.customFields[field.id]) }}</span>
                      <span v-else class="text-gray-400 dark:text-gray-500">—</span>
                    </template>
                    <template v-else>
                      <span class="text-gray-900 dark:text-gray-100">{{ displaySingleValue(report, field) }}</span>
                    </template>
                    <svg class="h-3 w-3 text-gray-400 dark:text-gray-500 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- My Teams tab -->
      <div v-if="activeTab === 'teams'">
        <div v-if="teams.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          None of your direct reports are assigned to a team.
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="team in teams"
            :key="team.id"
            class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <div>
                <button
                  @click="navigateToTeamDetail(team)"
                  class="text-primary-600 dark:text-primary-400 hover:underline font-medium"
                >
                  {{ team.name }}
                </button>
                <span class="ml-2 text-xs text-gray-400 dark:text-gray-500">{{ team.orgKey }}</span>
              </div>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ team.directReportUids.length }} of {{ team.totalMemberCount }} members are your reports
              </span>
            </div>

            <!-- Team metadata (read-only) -->
            <div v-if="teamFieldDefs.length > 0 && hasTeamMetadata(team)" class="mt-3 mb-3">
              <div class="grid grid-cols-2 gap-2 text-sm">
                <template v-for="field in visibleTeamFields" :key="field.id">
                  <div v-if="team.metadata[field.id] != null" class="flex items-center gap-2">
                    <span class="text-gray-500 dark:text-gray-400">{{ field.label }}:</span>
                    <span class="text-gray-900 dark:text-gray-100">{{ team.metadata[field.id] }}</span>
                  </div>
                </template>
              </div>
            </div>

            <!-- Team boards (read-only links) -->
            <div v-if="team.boards && team.boards.length > 0" class="mt-2 flex flex-wrap gap-2">
              <a
                v-for="(board, idx) in team.boards"
                :key="idx"
                :href="board.url"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1 text-xs text-primary-600 dark:text-primary-400 hover:underline"
              >
                {{ board.name || 'Board' }}
                <ExternalLink class="w-3 h-3" />
              </a>
            </div>

            <!-- Expand/collapse direct reports on this team -->
            <button
              @click="toggleTeamExpanded(team.id)"
              class="mt-3 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1"
            >
              <ChevronDown
                class="w-3.5 h-3.5 transition-transform"
                :class="expandedTeams[team.id] ? 'rotate-180' : ''"
              />
              {{ expandedTeams[team.id] ? 'Hide' : 'Show' }} your reports on this team
            </button>

            <div v-if="expandedTeams[team.id]" class="mt-3 space-y-3 pl-4 border-l-2 border-gray-200 dark:border-gray-700">
              <div
                v-for="uid in team.directReportUids"
                :key="uid"
                class="bg-gray-50 dark:bg-gray-900 rounded-lg p-3"
              >
                <div class="mb-2">
                  <button
                    @click="navigateToPersonDetail(uid)"
                    class="text-primary-600 dark:text-primary-400 hover:underline font-medium text-sm"
                  >
                    {{ getReportName(uid) }}
                  </button>
                  <span v-if="getReportTitle(uid)" class="ml-2 text-xs text-gray-500 dark:text-gray-400">{{ getReportTitle(uid) }}</span>
                </div>
                <PersonFieldEditor
                  v-if="getReport(uid)"
                  :uid="uid"
                  :custom-fields="getReport(uid).customFields"
                  :field-definitions="personFieldDefs"
                  :can-edit="true"
                  :people="allPeopleForEditor"
                  @updated="handleFieldUpdated"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, inject } from 'vue'
import { ExternalLink, ChevronDown, Pencil } from 'lucide-vue-next'
import { useManagerDashboard } from '../composables/useManagerDashboard'
import { useFieldDefinitions } from '@shared/client/composables/useFieldDefinitions'
import { useRoster } from '@shared/client/composables/useRoster'
import { apiRequest } from '@shared/client/services/api'
import PersonFieldEditor from '../components/PersonFieldEditor.vue'
import ConstrainedAutocomplete from '../components/ConstrainedAutocomplete.vue'
import PersonAutocomplete from '../components/PersonAutocomplete.vue'

const nav = inject('moduleNav', null)

const { directReports, teams, allOrgTeams, fieldDefinitions, loading, error, reason, load, refresh } = useManagerDashboard()
const { updatePersonFields } = useFieldDefinitions()
const { reloadRoster } = useRoster()

const activeTab = ref('reports')
const expandedTeams = ref({})

// Single-cell editing state
const editingCell = ref({ uid: null, fieldId: null })
const editValue = ref(null)
const editingTeamUid = ref(null)
const editTeamValue = ref([])
const saving = ref(false)

// Bulk editing state
const bulkEditing = ref(false)
// Stores pending changes: { "uid:fieldId": newValue }
const bulkChanges = reactive({})
// Stores pending team changes: { "uid": ["teamName1", "teamName2"] }
const bulkTeamChanges = reactive({})

const tabs = computed(() => [
  { id: 'reports', label: 'My Reports', count: directReports.value.length },
  { id: 'teams', label: 'My Teams', count: teams.value.length }
])

const personFieldDefs = computed(() =>
  (fieldDefinitions.value.person || []).filter(f => !f.deleted)
)

const visiblePersonFields = computed(() =>
  personFieldDefs.value.filter(f => f.visible)
)

const teamFieldDefs = computed(() =>
  (fieldDefinitions.value.team || []).filter(f => !f.deleted)
)

const visibleTeamFields = computed(() =>
  teamFieldDefs.value.filter(f => f.visible)
)

const teamById = computed(() => {
  const map = {}
  for (const team of teams.value) {
    map[team.id] = team
  }
  return map
})

const allPeopleForEditor = computed(() =>
  directReports.value.map(r => ({ uid: r.uid, name: r.name }))
)

const allOrgTeamNames = computed(() =>
  allOrgTeams.value.map(t => t.name).sort()
)

const orgTeamNameToId = computed(() => {
  const map = {}
  for (const t of allOrgTeams.value) {
    map[t.name] = t.id
  }
  return map
})

const pendingChangeCount = computed(() => {
  const fieldChanges = Object.keys(bulkChanges).length
  const teamChanges = Object.keys(bulkTeamChanges).length
  return fieldChanges + teamChanges
})

// --- Bulk editing ---

function enterBulkEdit() {
  bulkEditing.value = true
  for (const key of Object.keys(bulkChanges)) delete bulkChanges[key]
  for (const key of Object.keys(bulkTeamChanges)) delete bulkTeamChanges[key]
}

function cancelBulkEdit() {
  bulkEditing.value = false
  for (const key of Object.keys(bulkChanges)) delete bulkChanges[key]
  for (const key of Object.keys(bulkTeamChanges)) delete bulkTeamChanges[key]
}

function bulkKey(uid, fieldId) {
  return `${uid}:${fieldId}`
}

function getBulkValue(uid, field) {
  const key = bulkKey(uid, field.id)
  if (key in bulkChanges) return bulkChanges[key]
  // Return current value from data
  const raw = directReports.value.find(r => r.uid === uid)?.customFields[field.id] ?? null
  if (field.type === 'constrained' && field.multiValue) {
    return Array.isArray(raw) ? raw : (raw ? [raw] : [])
  }
  if (field.type === 'person-reference-linked') {
    return (Array.isArray(raw) ? raw[0] : raw) || ''
  }
  return Array.isArray(raw) ? (raw[0] || '') : (raw || '')
}

function setBulkValue(uid, fieldId, value) {
  const key = bulkKey(uid, fieldId)
  // Check if value differs from original
  const report = directReports.value.find(r => r.uid === uid)
  const original = report?.customFields[fieldId] ?? null
  const field = visiblePersonFields.value.find(f => f.id === fieldId)

  let originalNormalized
  if (field?.type === 'constrained' && field?.multiValue) {
    originalNormalized = Array.isArray(original) ? original : (original ? [original] : [])
  } else if (field?.type === 'person-reference-linked') {
    originalNormalized = (Array.isArray(original) ? original[0] : original) || ''
  } else {
    originalNormalized = Array.isArray(original) ? (original[0] || '') : (original || '')
  }

  // If value matches original, remove from pending changes
  if (JSON.stringify(value) === JSON.stringify(originalNormalized)) {
    delete bulkChanges[key]
  } else {
    bulkChanges[key] = value
  }
}

function teamNamesForUid(uid) {
  const report = directReports.value.find(r => r.uid === uid)
  if (!report || !report.teamIds) return []
  return report.teamIds.map(id => teamById.value[id]?.name).filter(Boolean)
}

function getBulkTeamValue(uid) {
  if (uid in bulkTeamChanges) return bulkTeamChanges[uid]
  return teamNamesForUid(uid)
}

function setBulkTeamValue(uid, names) {
  const original = teamNamesForUid(uid)
  if (JSON.stringify([...names].sort()) === JSON.stringify([...original].sort())) {
    delete bulkTeamChanges[uid]
  } else {
    bulkTeamChanges[uid] = names
  }
}

async function saveTeamChanges(uid, newNames) {
  const report = directReports.value.find(r => r.uid === uid)
  const oldIds = report?.teamIds || []
  const newIds = newNames.map(n => orgTeamNameToId.value[n]).filter(Boolean)
  const toAdd = newIds.filter(id => !oldIds.includes(id))
  const toRemove = oldIds.filter(id => !newIds.includes(id))
  const ops = [
    ...toAdd.map(id =>
      apiRequest(`/modules/team-tracker/structure/teams/${id}/members`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid })
      })
    ),
    ...toRemove.map(id =>
      apiRequest(`/modules/team-tracker/structure/teams/${id}/members/${uid}`, { method: 'DELETE' })
    )
  ]
  await Promise.all(ops)
}

async function saveAllChanges() {
  saving.value = true
  try {
    // Group field changes by uid
    const changesByUid = {}
    for (const [key, value] of Object.entries(bulkChanges)) {
      const [uid, fieldId] = key.split(':')
      if (!changesByUid[uid]) changesByUid[uid] = {}
      const field = visiblePersonFields.value.find(f => f.id === fieldId)
      let valueToSave = value
      if (field?.type !== 'constrained' || !field?.multiValue) {
        valueToSave = valueToSave || null
      }
      changesByUid[uid][fieldId] = valueToSave
    }
    // Save field changes and team changes in parallel
    await Promise.all([
      ...Object.entries(changesByUid).map(([uid, fields]) =>
        updatePersonFields(uid, fields)
      ),
      ...Object.entries(bulkTeamChanges).map(([uid, names]) =>
        saveTeamChanges(uid, names)
      )
    ])
    bulkEditing.value = false
    for (const key of Object.keys(bulkChanges)) delete bulkChanges[key]
    if (Object.keys(bulkTeamChanges).length > 0) reloadRoster()
    for (const key of Object.keys(bulkTeamChanges)) delete bulkTeamChanges[key]
    refresh()
  } finally {
    saving.value = false
  }
}

// --- Single-cell editing ---

function startCellEdit(report, field) {
  const raw = report.customFields[field.id] ?? null
  if (field.type === 'constrained' && field.multiValue) {
    editValue.value = Array.isArray(raw) ? [...raw] : (raw ? [raw] : [])
  } else if (field.type === 'person-reference-linked') {
    editValue.value = (Array.isArray(raw) ? raw[0] : raw) || ''
  } else {
    editValue.value = Array.isArray(raw) ? (raw[0] || '') : (raw || '')
  }
  editingCell.value = { uid: report.uid, fieldId: field.id }
}

async function saveCell(uid, fieldId) {
  saving.value = true
  try {
    const field = visiblePersonFields.value.find(f => f.id === fieldId)
    let valueToSave = editValue.value
    if (field?.type !== 'constrained' || !field?.multiValue) {
      valueToSave = valueToSave || null
    }
    await updatePersonFields(uid, { [fieldId]: valueToSave })
    editingCell.value = { uid: null, fieldId: null }
    refresh()
  } finally {
    saving.value = false
  }
}

function cancelEdit() {
  editingCell.value = { uid: null, fieldId: null }
}

function startTeamEdit(report) {
  editingTeamUid.value = report.uid
  editTeamValue.value = [...teamNamesForUid(report.uid)]
}

async function saveTeamEdit(uid) {
  saving.value = true
  try {
    await saveTeamChanges(uid, editTeamValue.value)
    editingTeamUid.value = null
    reloadRoster()
    refresh()
  } finally {
    saving.value = false
  }
}

function cancelTeamEdit() {
  editingTeamUid.value = null
}

// --- Display helpers ---

function displaySingleValue(report, field) {
  const raw = report.customFields[field.id]
  const val = Array.isArray(raw) ? raw[0] : raw
  return val || '—'
}

function displayMultiValues(report, field) {
  const raw = report.customFields[field.id]
  return Array.isArray(raw) ? raw : (raw ? [raw] : [])
}

function resolvePersonName(rawUid) {
  const uid = Array.isArray(rawUid) ? rawUid[0] : rawUid
  if (!uid) return null
  const person = allPeopleForEditor.value.find(p => p.uid === uid)
  return person ? person.name : null
}

// --- Shared helpers ---

function getReport(uid) {
  return directReports.value.find(r => r.uid === uid)
}

function getReportName(uid) {
  const r = getReport(uid)
  return r ? r.name : uid
}

function getReportTitle(uid) {
  const r = getReport(uid)
  return r ? r.title : null
}

function hasTeamMetadata(team) {
  if (!team.metadata) return false
  return Object.keys(team.metadata).length > 0
}

function toggleTeamExpanded(teamId) {
  expandedTeams.value[teamId] = !expandedTeams.value[teamId]
}

function navigateToPersonDetail(uid) {
  if (nav) nav.navigateTo('person-detail', { uid })
}

function navigateToTeamDetail(team) {
  if (nav) nav.navigateTo('team-detail', { teamKey: `${team.orgKey}::${team.name}` })
}

function handleFieldUpdated() {
  refresh()
}

onMounted(() => {
  load()
})
</script>
