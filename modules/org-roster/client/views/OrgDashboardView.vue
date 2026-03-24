<template>
  <div>
    <!-- Org selector (shown when accessed directly or to switch orgs) -->
    <div v-if="orgs.length > 0" class="mb-6">
      <OrgSelector :orgs="orgs" :modelValue="selectedOrg" @select="handleOrgSelect" />
    </div>

    <!-- No org selected prompt (shouldn't normally show since we auto-load All) -->
    <div v-if="!selectedOrg && !summary && !loading" class="text-center py-12">
      <p class="text-gray-500">Select an organization above to view its dashboard.</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-700 text-sm">{{ error }}</p>
    </div>

    <template v-else-if="summary">
      <!-- Header -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900">{{ summary.org }} Dashboard</h2>
        <p class="text-sm text-gray-500 mt-1">Org-level summary</p>
      </div>

      <!-- Stats cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p class="text-3xl font-bold text-primary-600">{{ summary.teamCount }}</p>
          <p class="text-sm text-gray-500">Teams</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p class="text-3xl font-bold text-primary-600">{{ summary.headcount }}</p>
          <p class="text-sm text-gray-500">People</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p class="text-3xl font-bold text-primary-600">{{ summary.components?.length || 0 }}</p>
          <p class="text-sm text-gray-500">Components</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p class="text-3xl font-bold text-amber-600">{{ summary.totalRfeCount || 0 }}</p>
          <p class="text-sm text-gray-500">Open RFEs</p>
        </div>
      </div>

      <!-- Role Breakdown -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Headcount by Role</h3>
        <HeadcountChart :headcount="roleHeadcount" />
      </div>

      <!-- Teams -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Teams</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Team</th>
                <th v-if="isAllView" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Org</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Members</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Open RFEs</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr
                v-for="t in sortedTeams"
                :key="(t.org || '') + '::' + t.name"
                class="hover:bg-gray-50 cursor-pointer"
                @click="goToTeam(t)"
              >
                <td class="px-4 py-3">
                  <span class="text-primary-600 hover:text-primary-800 hover:underline font-medium">{{ t.name }}</span>
                </td>
                <td v-if="isAllView" class="px-4 py-3 text-gray-500 text-sm">{{ t.org }}</td>
                <td class="px-4 py-3 text-right text-gray-600">{{ t.memberCount }}</td>
                <td class="px-4 py-3 text-right">
                  <span
                    v-if="t.rfeCount > 0"
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800"
                  >
                    {{ t.rfeCount }}
                  </span>
                  <span v-else class="text-gray-400">0</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- RFE by Component (top 10) -->
      <div v-if="topRfeComponents.length > 0" class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Top RFE Backlog by Component</h3>
        <div class="space-y-2">
          <div
            v-for="comp in topRfeComponents"
            :key="comp.name"
            class="flex items-center gap-3"
          >
            <span class="text-sm text-gray-700 w-48 truncate">{{ comp.name }}</span>
            <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
              <div
                class="bg-amber-400 h-full rounded-full"
                :style="{ width: `${(comp.count / maxRfeCount) * 100}%` }"
              ></div>
            </div>
            <span class="text-sm font-medium text-gray-700 w-10 text-right">{{ comp.count }}</span>
          </div>
        </div>
      </div>

      <!-- Components -->
      <div v-if="summary.components && summary.components.length > 0" class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Components ({{ summary.components.length }})</h3>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="comp in summary.components"
            :key="comp"
            class="inline-flex items-center px-2.5 py-1 rounded text-sm bg-blue-50 text-blue-700"
          >
            {{ comp }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import HeadcountChart from '../components/HeadcountChart.vue'
import OrgSelector from '../components/OrgSelector.vue'
import { useOrgRoster } from '../composables/useOrgRoster'

const nav = inject('moduleNav')
const { loadOrgSummary, loadOrgs, orgs } = useOrgRoster()

const summary = ref(null)
const selectedOrg = ref(null)
const loading = ref(false)
const error = ref(null)

const roleHeadcount = computed(() => {
  if (!summary.value) return {}
  return {
    byRole: summary.value.roleBreakdown || {},
    byRoleFte: summary.value.roleFteBreakdown || {},
    totalHeadcount: summary.value.headcount || 0,
    totalFte: Object.values(summary.value.roleFteBreakdown || {}).reduce((a, b) => a + b, 0)
  }
})

const sortedTeams = computed(() => {
  if (!summary.value?.teams) return []
  return [...summary.value.teams].sort((a, b) => (b.memberCount || 0) - (a.memberCount || 0))
})

const topRfeComponents = computed(() => {
  if (!summary.value?.rfeByComponent) return []
  return Object.entries(summary.value.rfeByComponent)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
})

const maxRfeCount = computed(() => {
  if (topRfeComponents.value.length === 0) return 1
  return topRfeComponents.value[0].count
})

const isAllView = computed(() => !selectedOrg.value)

function goToTeam(team) {
  const org = team.org || summary.value.org
  nav.navigateTo('team-detail', { teamKey: `${org}::${team.name}` })
}

async function handleOrgSelect(orgName) {
  selectedOrg.value = orgName
  loading.value = true
  error.value = null
  try {
    // null means "All" — load aggregate via _all
    summary.value = await loadOrgSummary(orgName || '_all')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadOrgs()
  const orgName = nav.params.value?.org
  // Load either the requested org or the aggregate view
  await handleOrgSelect(orgName || null)
})
</script>
