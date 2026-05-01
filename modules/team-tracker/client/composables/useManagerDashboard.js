import { ref } from 'vue'
import { apiRequest } from '@shared/client/services/api'

const manager = ref(null)
const directReports = ref([])
const teams = ref([])
const allOrgTeams = ref([])
const fieldDefinitions = ref({ person: [], team: [] })
const loading = ref(false)
const error = ref(null)
const reason = ref(null)

export function useManagerDashboard() {
  async function load() {
    loading.value = true
    error.value = null
    reason.value = null
    try {
      const data = await apiRequest('/modules/team-tracker/manager/dashboard')
      manager.value = data.manager || null
      directReports.value = data.directReports || []
      teams.value = data.teams || []
      allOrgTeams.value = data.allOrgTeams || []
      fieldDefinitions.value = data.fieldDefinitions || { person: [], team: [] }
      reason.value = data.reason || null
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function refresh() {
    return load()
  }

  return {
    manager,
    directReports,
    teams,
    allOrgTeams,
    fieldDefinitions,
    loading,
    error,
    reason,
    load,
    refresh
  }
}
