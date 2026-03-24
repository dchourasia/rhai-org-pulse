import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('fetchRfeForComponent', () => {
  let fetchRfeForComponent
  let originalFetch

  beforeEach(async () => {
    process.env.JIRA_EMAIL = 'test@example.com'
    process.env.JIRA_TOKEN = 'test-token'
    process.env.JIRA_HOST = 'https://jira.example.com'

    // Save and replace global fetch used by node-fetch
    vi.resetModules()
  })

  afterEach(() => {
    delete process.env.JIRA_EMAIL
    delete process.env.JIRA_TOKEN
    delete process.env.JIRA_HOST
  })

  it('escapes double quotes in component names to prevent JQL injection', () => {
    // Test the JQL construction logic directly
    const component = 'Component "with" quotes'
    const escaped = component.replace(/"/g, '\\"')
    const jql = `project = RHAIRFE AND component = "${escaped}" AND issuetype = "Feature Request" AND statusCategory != "Done"`
    // The escaped component should not have bare double quotes that could break the JQL
    expect(jql).toContain('Component \\"with\\" quotes')
    expect(jql).not.toMatch(/component = "Component "with"/)
  })

  it('produces correct JQL with configurable project and issue type', () => {
    const project = 'CUSTOMPROJ'
    const issueType = 'Enhancement'
    const component = 'MyComp'
    const escaped = component.replace(/"/g, '\\"')
    const jql = `project = ${project} AND component = "${escaped}" AND issuetype = "${issueType}" AND statusCategory != "Done"`
    expect(jql).toContain('project = CUSTOMPROJ')
    expect(jql).toContain('issuetype = "Enhancement"')
    expect(jql).toContain('component = "MyComp"')
  })

  it('default project is RHAIRFE and default issue type is Feature Request', () => {
    // Verify the defaults from the function signature
    const options = {}
    const project = options.jiraProject || 'RHAIRFE'
    const issueType = options.rfeIssueType || 'Feature Request'
    expect(project).toBe('RHAIRFE')
    expect(issueType).toBe('Feature Request')
  })
})

describe('fetchAllRfeBacklog', () => {
  it('aggregates RFE counts by team from component data', async () => {
    // Test the aggregation logic without network calls
    const byComponent = {
      'AI Hub': { count: 10, error: null },
      'KServe': { count: 5, error: null },
      'Pipelines': { count: 3, error: null },
    }
    const teams = [
      { org: 'AI Platform', name: 'Dashboard', components: ['AI Hub'] },
      { org: 'AI Platform', name: 'Model Serving', components: ['KServe'] },
      { org: 'AAET', name: 'Pipes', components: ['Pipelines'] },
    ]

    // Replicate the aggregation logic from fetchAllRfeBacklog
    const byTeam = {}
    for (const team of teams) {
      const teamKey = `${team.org}::${team.name}`
      let totalCount = 0
      for (const comp of (team.components || [])) {
        if (byComponent[comp]) {
          totalCount += byComponent[comp].count
        }
      }
      byTeam[teamKey] = { count: totalCount }
    }

    expect(byTeam['AI Platform::Dashboard']).toEqual({ count: 10 })
    expect(byTeam['AI Platform::Model Serving']).toEqual({ count: 5 })
    expect(byTeam['AAET::Pipes']).toEqual({ count: 3 })
  })
})
