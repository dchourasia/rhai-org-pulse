import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mount, flushPromises } from '@vue/test-utils'
import ManagerDashboardView from '../../client/views/ManagerDashboardView.vue'

// Mock the composable
const mockLoad = vi.fn()
const mockRefresh = vi.fn()
const mockManager = ref(null)
const mockDirectReports = ref([])
const mockIndirectReports = ref([])
const mockTeams = ref([])
const mockAllOrgTeams = ref([])
const mockFieldDefinitions = ref({ person: [], team: [] })
const mockLoading = ref(false)
const mockError = ref(null)
const mockReason = ref(null)
const mockIncludeIndirect = ref(false)

vi.mock('../../client/composables/useManagerDashboard', () => ({
  useManagerDashboard: () => ({
    manager: mockManager,
    directReports: mockDirectReports,
    indirectReports: mockIndirectReports,
    teams: mockTeams,
    allOrgTeams: mockAllOrgTeams,
    fieldDefinitions: mockFieldDefinitions,
    loading: mockLoading,
    error: mockError,
    reason: mockReason,
    includeIndirect: mockIncludeIndirect,
    load: mockLoad,
    refresh: mockRefresh
  })
}))

// Mock PersonFieldEditor
vi.mock('../../client/components/PersonFieldEditor.vue', () => ({
  default: {
    name: 'PersonFieldEditor',
    template: '<div class="person-field-editor" :data-uid="uid"></div>',
    props: ['uid', 'customFields', 'fieldDefinitions', 'canEdit', 'people'],
    emits: ['updated']
  }
}))

// Mock useFieldDefinitions (needed by PersonFieldEditor)
vi.mock('@shared/client/composables/useFieldDefinitions', () => ({
  useFieldDefinitions: () => ({
    demoToast: ref(null),
    updatePersonFields: vi.fn().mockResolvedValue({})
  })
}))

function mountView() {
  return mount(ManagerDashboardView, {
    global: {
      provide: {
        moduleNav: {
          navigateTo: vi.fn(),
          goBack: vi.fn(),
          params: ref({})
        }
      },
      stubs: {
        ExternalLink: { template: '<span class="external-link-icon" />' },
        ChevronDown: { template: '<span class="chevron-down-icon" />' },
        ConstrainedAutocomplete: { template: '<div />', props: ['modelValue', 'options', 'multiValue'] },
        PersonAutocomplete: { template: '<div />', props: ['modelValue', 'people'] }
      }
    }
  })
}

beforeEach(() => {
  mockManager.value = null
  mockDirectReports.value = []
  mockIndirectReports.value = []
  mockTeams.value = []
  mockAllOrgTeams.value = []
  mockFieldDefinitions.value = { person: [], team: [] }
  mockLoading.value = false
  mockError.value = null
  mockReason.value = null
  mockIncludeIndirect.value = false
  mockLoad.mockClear()
  mockRefresh.mockClear()
})

describe('ManagerDashboardView', () => {
  it('renders reports tab by default', async () => {
    mockDirectReports.value = [
      { uid: 'alice', name: 'Alice', email: 'alice@example.com', title: 'Engineer', teamIds: ['team_a'], customFields: {} }
    ]
    mockTeams.value = [
      { id: 'team_a', name: 'Alpha', orgKey: 'org1', directReportUids: ['alice'], totalMemberCount: 3, metadata: {}, boards: [] }
    ]

    const wrapper = mountView()
    await flushPromises()

    // Should show My Reports tab as active (default tab is 'reports')
    expect(wrapper.text()).toContain('My Reports')
    expect(wrapper.text()).toContain('Alice')
  })

  it('shows direct reports with editable fields in table view', async () => {
    mockDirectReports.value = [
      { uid: 'alice', name: 'Alice', email: 'alice@example.com', title: 'Engineer', teamIds: [], customFields: { field_f1: 'backend' } }
    ]
    mockFieldDefinitions.value = {
      person: [{ id: 'field_f1', label: 'Focus', type: 'free-text', visible: true, deleted: false }],
      team: []
    }

    const wrapper = mountView()
    await flushPromises()

    // Default is table view — field values should be shown inline as column
    expect(wrapper.text()).toContain('Focus') // column header
    expect(wrapper.text()).toContain('backend') // field value
  })

  it('shows teams tab with "X of Y" member counts', async () => {
    mockDirectReports.value = [
      { uid: 'alice', name: 'Alice', email: 'alice@example.com', title: 'Engineer', teamIds: ['team_a'], customFields: {} }
    ]
    mockTeams.value = [
      { id: 'team_a', name: 'Alpha', orgKey: 'org1', directReportUids: ['alice'], totalMemberCount: 5, metadata: {}, boards: [] }
    ]

    const wrapper = mountView()
    await flushPromises()

    // Switch to teams tab
    const teamsTab = wrapper.findAll('button').find(b => b.text().includes('My Teams'))
    await teamsTab.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('1 of 5 members are your reports')
    expect(wrapper.text()).toContain('Alpha')
  })

  it('handles reason "no-registry-identity" empty state', async () => {
    mockReason.value = 'no-registry-identity'

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.text()).toContain('No Registry Identity')
    expect(wrapper.text()).toContain('not linked to the people registry')
  })

  it('handles reason "no-direct-reports" empty state', async () => {
    mockReason.value = 'no-direct-reports'

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.text()).toContain('No Direct Reports')
    expect(wrapper.text()).toContain('no direct reports in the system')
  })

  it('navigates to person detail on name click', async () => {
    const navMock = { navigateTo: vi.fn(), goBack: vi.fn(), params: ref({}) }
    mockDirectReports.value = [
      { uid: 'alice', name: 'Alice', email: 'alice@example.com', title: 'Engineer', teamIds: [], customFields: {} }
    ]

    const wrapper = mount(ManagerDashboardView, {
      global: {
        provide: { moduleNav: navMock },
        stubs: {
          ExternalLink: { template: '<span />' },
          ChevronDown: { template: '<span />' },
          PersonFieldEditor: { template: '<div />', props: ['uid', 'customFields', 'fieldDefinitions', 'canEdit', 'people'] }
        }
      }
    })
    await flushPromises()

    const nameButton = wrapper.findAll('button').find(b => b.text().includes('Alice'))
    await nameButton.trigger('click')

    expect(navMock.navigateTo).toHaveBeenCalledWith('person-detail', { uid: 'alice' })
  })

  it('navigates to team detail on team name click', async () => {
    const navMock = { navigateTo: vi.fn(), goBack: vi.fn(), params: ref({}) }
    mockDirectReports.value = [
      { uid: 'alice', name: 'Alice', email: 'alice@example.com', title: 'Engineer', teamIds: ['team_a'], customFields: {} }
    ]
    mockTeams.value = [
      { id: 'team_a', name: 'Alpha', orgKey: 'org1', directReportUids: ['alice'], totalMemberCount: 3, metadata: {}, boards: [] }
    ]

    const wrapper = mount(ManagerDashboardView, {
      global: {
        provide: { moduleNav: navMock },
        stubs: {
          ExternalLink: { template: '<span />' },
          ChevronDown: { template: '<span />' },
          PersonFieldEditor: { template: '<div />', props: ['uid', 'customFields', 'fieldDefinitions', 'canEdit', 'people'] }
        }
      }
    })
    await flushPromises()

    // Switch to teams tab
    const teamsTab = wrapper.findAll('button').find(b => b.text().includes('My Teams'))
    await teamsTab.trigger('click')
    await flushPromises()

    const teamButton = wrapper.findAll('button').find(b => b.text().includes('Alpha'))
    await teamButton.trigger('click')

    expect(navMock.navigateTo).toHaveBeenCalledWith('team-detail', { team: 'org1::Alpha' })
  })
})
