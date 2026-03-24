<template>
  <div class="space-y-6">
    <h3 class="text-lg font-semibold text-gray-900">Org Roster Settings</h3>

    <!-- Sync Status -->
    <div class="bg-white border border-gray-200 rounded-lg p-4">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Sync Status</h4>
      <div v-if="syncStatus" class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-500">Last sync:</span>
          <span class="text-gray-800">{{ syncStatus.lastSyncAt ? new Date(syncStatus.lastSyncAt).toLocaleString() : 'Never' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">Status:</span>
          <span
            :class="{
              'text-green-600': syncStatus.status === 'success',
              'text-red-600': syncStatus.status === 'error',
              'text-gray-500': syncStatus.status === 'never'
            }"
          >
            {{ syncStatus.status }}
          </span>
        </div>
        <div v-if="syncStatus.teamCount" class="flex justify-between">
          <span class="text-gray-500">Teams:</span>
          <span class="text-gray-800">{{ syncStatus.teamCount }}</span>
        </div>
        <div v-if="syncStatus.peopleCount" class="flex justify-between">
          <span class="text-gray-500">People:</span>
          <span class="text-gray-800">{{ syncStatus.peopleCount }}</span>
        </div>
        <div v-if="syncStatus.error" class="mt-2 text-red-600 text-xs bg-red-50 p-2 rounded">
          {{ syncStatus.error }}
        </div>
      </div>
      <div v-else class="text-sm text-gray-500">Loading...</div>
    </div>

    <!-- Manual Sync -->
    <div class="bg-white border border-gray-200 rounded-lg p-4">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Manual Sync</h4>
      <div class="flex gap-2">
        <select
          v-model="syncType"
          :disabled="syncing"
          class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white disabled:opacity-50"
        >
          <option value="full">Full Sync (Sheets + RFE)</option>
          <option value="sheets">Sheets Only</option>
          <option value="rfe">RFE Only</option>
        </select>
        <button
          @click="handleSync"
          :disabled="syncing"
          class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ syncing ? 'Syncing...' : 'Run Sync' }}
        </button>
      </div>
      <p v-if="syncMessage" class="mt-2 text-sm" :class="syncError ? 'text-red-600' : 'text-green-600'">
        {{ syncMessage }}
      </p>
    </div>

    <!-- Configuration -->
    <div class="bg-white border border-gray-200 rounded-lg p-4">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Configuration</h4>
      <div class="space-y-3">
        <div>
          <label class="block text-xs text-gray-500 mb-1">Team Boards Tab Name</label>
          <input
            v-model="config.teamBoardsTab"
            type="text"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Components Tab Name</label>
          <input
            v-model="config.componentsTab"
            type="text"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Jira Project (for RFE queries)</label>
          <input
            v-model="config.jiraProject"
            type="text"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">RFE Issue Type</label>
          <input
            v-model="config.rfeIssueType"
            type="text"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>
    </div>

    <!-- Org Name Mapping -->
    <div class="bg-white border border-gray-200 rounded-lg p-4">
      <div class="flex items-center justify-between mb-1">
        <h4 class="text-sm font-medium text-gray-700">Org Name Mapping</h4>
        <button
          @click="handleDetectOrgs"
          :disabled="detectingOrgs"
          class="text-xs text-primary-600 hover:text-primary-700 disabled:opacity-50"
        >
          {{ detectingOrgs ? 'Detecting...' : 'Detect from Sheet' }}
        </button>
      </div>
      <p class="text-xs text-gray-400 mb-3">Maps org names from the spreadsheet to configured org display names. Only teams in configured orgs are synced.</p>

      <div v-if="orgMappingRows.length > 0" class="space-y-2">
        <!-- Auto-matched orgs -->
        <div
          v-for="row in autoMatchedOrgs"
          :key="'matched-' + row.sheetOrg"
          class="flex gap-2 items-center px-3 py-2 bg-green-50 border border-green-200 rounded-lg"
        >
          <span class="flex-1 text-sm text-green-800">{{ row.sheetOrg }}</span>
          <span class="text-green-400 text-sm">→</span>
          <span class="flex-1 text-sm text-green-800">{{ row.sheetOrg }}</span>
          <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-green-100 text-green-700">matched</span>
        </div>

        <!-- Suggested / unmatched orgs -->
        <div
          v-for="row in unmatchedOrgs"
          :key="'unmatched-' + row.sheetOrg"
          class="rounded-lg"
          :class="row.isSuggestion && row.selectedOrg ? 'bg-amber-50 border border-amber-200 p-3' : ''"
        >
          <div class="flex gap-2 items-center">
            <span class="flex-1 px-3 py-1.5 text-sm bg-gray-50 border border-gray-200 rounded-lg text-gray-700">{{ row.sheetOrg }}</span>
            <span class="text-gray-400 text-sm">→</span>
            <select
              v-model="row.selectedOrg"
              class="flex-1 px-3 py-1.5 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              :class="row.isSuggestion && row.selectedOrg ? 'border-amber-300 bg-white' : 'border-gray-300'"
              @change="row.isSuggestion && (row.isSuggestion = false)"
            >
              <option value="">— skip (don't sync) —</option>
              <option v-for="org in configuredOrgs" :key="org" :value="org">{{ org }}</option>
            </select>
          </div>
          <div v-if="row.isSuggestion && row.selectedOrg" class="flex items-center justify-between mt-2">
            <span class="text-xs text-amber-700">Suggested match — does this look right?</span>
            <div class="flex gap-2">
              <button
                @click="row.isSuggestion = false"
                class="px-2.5 py-1 text-xs font-medium text-white bg-green-600 rounded hover:bg-green-700 transition-colors"
              >
                Accept
              </button>
              <button
                @click="row.selectedOrg = ''; row.isSuggestion = false"
                class="px-2.5 py-1 text-xs font-medium text-gray-600 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!detectingOrgs" class="text-xs text-gray-400 py-2">
        Click "Detect from Sheet" to discover org names from the spreadsheet.
      </div>

      <p v-if="detectError" class="mt-2 text-xs text-red-600">{{ detectError }}</p>
    </div>

    <!-- Save All -->
    <div class="flex items-center gap-3">
      <button
        @click="handleSaveConfig"
        class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
      >
        Save All Settings
      </button>
      <p v-if="configMessage" class="text-sm" :class="configError ? 'text-red-600' : 'text-green-600'">
        {{ configMessage }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useOrgRoster } from '../composables/useOrgRoster'

const { loadSyncStatus, triggerSync, triggerSheetsSync, triggerRfeSync, loadSheetOrgs, loadConfiguredOrgs, loadConfig, saveConfig } = useOrgRoster()

const syncStatus = ref(null)
const syncing = ref(false)
const syncType = ref('full')
const syncMessage = ref('')
const syncError = ref(false)
const config = ref({
  teamBoardsTab: 'Scrum Team Boards',
  componentsTab: 'Summary: components per team',
  jiraProject: 'RHAIRFE',
  rfeIssueType: 'Feature Request',
  orgNameMapping: {}
})
const configMessage = ref('')
const configError = ref(false)

// Org mapping state
const orgMappingRows = ref([])   // [{ sheetOrg, selectedOrg, isSuggestion, isExactMatch }]
const configuredOrgs = ref([])
const detectingOrgs = ref(false)
const detectError = ref('')

const autoMatchedOrgs = computed(() => orgMappingRows.value.filter(r => r.isExactMatch))
const unmatchedOrgs = computed(() => orgMappingRows.value.filter(r => !r.isExactMatch))

async function refreshStatus() {
  try {
    syncStatus.value = await loadSyncStatus()
  } catch {
    // ignore
  }
}

async function handleSync() {
  syncing.value = true
  syncMessage.value = ''
  syncError.value = false
  try {
    const labels = { full: 'Full sync', sheets: 'Sheets sync', rfe: 'RFE sync' }
    if (syncType.value === 'sheets') await triggerSheetsSync()
    else if (syncType.value === 'rfe') await triggerRfeSync()
    else await triggerSync()
    syncMessage.value = `${labels[syncType.value]} started. Data will update shortly.`
    setTimeout(refreshStatus, 5000)
  } catch (err) {
    syncMessage.value = err.message
    syncError.value = true
  } finally {
    syncing.value = false
  }
}

function findBestMatch(sheetOrg, configured) {
  const lower = sheetOrg.toLowerCase()
  // Check if any configured name is a substring of the sheet name or vice versa
  for (const org of configured) {
    const orgLower = org.toLowerCase()
    if (lower.includes(orgLower) || orgLower.includes(lower)) {
      return org
    }
  }
  // Check word overlap
  const sheetWords = new Set(lower.split(/\s+/))
  let bestOrg = null
  let bestOverlap = 0
  for (const org of configured) {
    const orgWords = org.toLowerCase().split(/\s+/)
    const overlap = orgWords.filter(w => sheetWords.has(w)).length
    if (overlap > bestOverlap && overlap >= Math.ceil(orgWords.length / 2)) {
      bestOverlap = overlap
      bestOrg = org
    }
  }
  return bestOrg
}

async function handleDetectOrgs() {
  detectingOrgs.value = true
  detectError.value = ''
  try {
    const [sheetData, configData] = await Promise.all([
      loadSheetOrgs(),
      loadConfiguredOrgs()
    ])
    const sheetOrgs = sheetData.sheetOrgs || []
    configuredOrgs.value = configData.configuredOrgs || []
    const savedMapping = config.value.orgNameMapping || {}
    const configuredSet = new Set(configuredOrgs.value)

    orgMappingRows.value = sheetOrgs.map(sheetOrg => {
      // Exact match to a configured org
      if (configuredSet.has(sheetOrg)) {
        return { sheetOrg, selectedOrg: sheetOrg, isSuggestion: false, isExactMatch: true }
      }
      // Already saved mapping
      if (savedMapping[sheetOrg] && configuredSet.has(savedMapping[sheetOrg])) {
        return { sheetOrg, selectedOrg: savedMapping[sheetOrg], isSuggestion: false, isExactMatch: false }
      }
      // Try fuzzy match
      const suggestion = findBestMatch(sheetOrg, configuredOrgs.value)
      return { sheetOrg, selectedOrg: suggestion || '', isSuggestion: !!suggestion, isExactMatch: false }
    })
  } catch (err) {
    detectError.value = err.message
  } finally {
    detectingOrgs.value = false
  }
}

async function handleSaveConfig() {
  configMessage.value = ''
  configError.value = false
  try {
    // Build mapping from rows (only non-exact-match rows that have a selection)
    const mapping = {}
    for (const row of orgMappingRows.value) {
      if (!row.isExactMatch && row.selectedOrg) {
        mapping[row.sheetOrg] = row.selectedOrg
      }
    }
    await saveConfig({ ...config.value, orgNameMapping: mapping })
    // Clear suggestion flags after saving
    for (const row of orgMappingRows.value) {
      if (row.selectedOrg) row.isSuggestion = false
    }
    configMessage.value = 'Configuration saved.'
  } catch (err) {
    configMessage.value = err.message
    configError.value = true
  }
}

async function loadConfigData() {
  try {
    const data = await loadConfig()
    if (data) {
      config.value = { ...config.value, ...data }
    }
  } catch {
    // Use defaults
  }
}

onMounted(async () => {
  await Promise.all([refreshStatus(), loadConfigData()])
  // Auto-detect orgs so the full mapping (including exact matches) is visible
  await handleDetectOrgs()
})
</script>
