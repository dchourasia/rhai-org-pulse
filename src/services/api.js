/**
 * API Service
 * Handles communication with the backend
 * Automatically includes Firebase ID token in requests
 */

import { useAuth } from '../composables/useAuth'

const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || '/api'

/**
 * Get Firebase ID token for authentication
 */
async function getAuthToken() {
  const { getIdToken, loading } = useAuth()

  if (loading.value) {
    await new Promise((resolve) => {
      const checkLoading = setInterval(() => {
        if (!loading.value) {
          clearInterval(checkLoading)
          resolve()
        }
      }, 50)
      setTimeout(() => {
        clearInterval(checkLoading)
        resolve()
      }, 10000)
    })
  }

  try {
    return await getIdToken()
  } catch (error) {
    console.error('Failed to get auth token:', error)
    throw new Error('Authentication required. Please sign in again.')
  }
}

async function apiRequest(path, options = {}) {
  const token = await getAuthToken()
  const response = await fetch(`${API_ENDPOINT}${path}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    if (response.status === 401) {
      throw new Error('Authentication failed. Please sign in again.')
    }
    throw new Error(errorData.error || `HTTP ${response.status}`)
  }

  return response.json()
}

export async function refreshData({ hardRefresh = false } = {}) {
  return apiRequest('/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hardRefresh })
  })
}

export async function refreshDataForeground({ hardRefresh = false, onProgress, onComplete, onError, signal } = {}) {
  const token = await getAuthToken()
  const params = hardRefresh ? '?hardRefresh=true' : ''

  const response = await fetch(`${API_ENDPOINT}/refresh/stream${params}`, {
    headers: { 'Authorization': `Bearer ${token}` },
    signal
  })

  if (!response.ok) {
    const msg = `HTTP ${response.status}`
    if (onError) onError(new Error(msg))
    throw new Error(msg)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      try {
        const event = JSON.parse(line.slice(6))
        if (event.type === 'complete') {
          if (onComplete) onComplete(event)
        } else if (event.type === 'error') {
          if (onError) onError(new Error(event.message))
        } else {
          if (onProgress) onProgress(event)
        }
      } catch {
        // skip malformed lines
      }
    }
  }
}

export async function discoverBoards() {
  return apiRequest('/discover-boards', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ projectKey: 'RHOAIENG' })
  })
}

export async function getBoards() {
  return apiRequest('/boards')
}

export async function getSprintsForBoard(boardId) {
  return apiRequest(`/boards/${boardId}/sprints`)
}

export async function getSprintData(sprintId) {
  return apiRequest(`/sprints/${sprintId}`)
}

export async function getBoardTrend(boardId) {
  return apiRequest(`/boards/${boardId}/trend`)
}

export async function getAggregateTrend(boardIds) {
  return apiRequest(`/trend?boardIds=${boardIds.join(',')}`)
}

export async function getDashboardSummary() {
  return apiRequest('/dashboard-summary')
}

export async function getTeams() {
  return apiRequest('/teams')
}

export async function saveTeams(teams) {
  return apiRequest('/teams', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ teams })
  })
}

export async function getSprintAnnotations(sprintId) {
  return apiRequest(`/sprints/${sprintId}/annotations`)
}

export async function saveAnnotation(sprintId, { assignee, text }) {
  return apiRequest(`/sprints/${sprintId}/annotations`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ assignee, text })
  })
}

export async function deleteAnnotation(sprintId, assignee, annotationId) {
  return apiRequest(`/sprints/${sprintId}/annotations/${encodeURIComponent(assignee)}/${annotationId}`, {
    method: 'DELETE'
  })
}
