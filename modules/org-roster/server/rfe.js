/**
 * Jira RFE (Feature Request) backlog queries.
 * Fetches open Feature Requests per Jira component.
 */

const fetch = require('node-fetch');

const STORY_POINTS_FIELD = process.env.JIRA_STORY_POINTS_FIELD || 'customfield_10028';

function getJiraAuth() {
  const token = process.env.JIRA_TOKEN;
  const email = process.env.JIRA_EMAIL;
  if (!token || !email) {
    throw new Error('JIRA_TOKEN and JIRA_EMAIL environment variables must be set.');
  }
  return Buffer.from(`${email}:${token}`).toString('base64');
}

async function jiraRequest(path) {
  const auth = getJiraAuth();
  const host = process.env.JIRA_HOST || 'https://redhat.atlassian.net';
  const MAX_RETRIES = 3;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    const response = await fetch(`${host}${path}`, {
      headers: {
        'Authorization': `Basic ${auth}`,
        'Accept': 'application/json'
      }
    });

    if (response.status === 429 && attempt < MAX_RETRIES) {
      const retryAfter = parseInt(response.headers.get('retry-after'), 10);
      const delay = (!isNaN(retryAfter) && retryAfter > 0) ? retryAfter * 1000 : Math.pow(2, attempt + 1) * 1000;
      console.warn(`[org-roster rfe] Rate limited, retrying in ${delay / 1000}s`);
      await new Promise(resolve => setTimeout(resolve, delay));
      continue;
    }

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Jira API error (${response.status}): ${text}`);
    }

    return response.json();
  }
}

/**
 * Fetch open RFE count for a single Jira component.
 * @param {string} component - Jira component name
 * @param {object} [options] - Optional overrides for project and issue type
 * @param {string} [options.jiraProject] - Jira project key (default: RHAIRFE)
 * @param {string} [options.rfeIssueType] - Issue type name (default: Feature Request)
 */
async function fetchRfeForComponent(component, options = {}) {
  const project = options.jiraProject || 'RHAIRFE';
  const issueType = options.rfeIssueType || 'Feature Request';
  // Escape double quotes in component name to prevent JQL injection
  const escaped = component.replace(/"/g, '\\"');
  const jql = encodeURIComponent(
    `project = ${project} AND component = "${escaped}" AND issuetype = "${issueType}" AND statusCategory != "Done"`
  );
  const fields = `summary,${STORY_POINTS_FIELD}`;
  const params = `jql=${jql}&fields=${fields}&maxResults=1`;

  try {
    const data = await jiraRequest(`/rest/api/3/search/jql?${params}`);
    return { count: data.total || 0 };
  } catch (err) {
    console.warn(`[org-roster rfe] Failed to fetch RFEs for component "${component}": ${err.message}`);
    return { count: 0, error: err.message };
  }
}

/**
 * Fetch RFE backlog for all components.
 * Batches requests with delays to avoid rate limiting.
 */
async function fetchAllRfeBacklog(components, teams, options = {}) {
  const BATCH_SIZE = 5;
  const BATCH_DELAY = 1000;

  const byComponent = {};
  const componentList = [...new Set(components)];

  for (let i = 0; i < componentList.length; i += BATCH_SIZE) {
    const batch = componentList.slice(i, i + BATCH_SIZE);

    const results = await Promise.all(
      batch.map(async (comp) => {
        const result = await fetchRfeForComponent(comp, options);
        return { component: comp, ...result };
      })
    );

    for (const result of results) {
      byComponent[result.component] = {
        count: result.count,
        error: result.error || null
      };
    }

    if (i + BATCH_SIZE < componentList.length) {
      await new Promise(resolve => setTimeout(resolve, BATCH_DELAY));
    }
  }

  // Aggregate by team
  const byTeam = {};
  if (teams) {
    for (const team of teams) {
      const teamKey = `${team.org}::${team.name}`;
      let totalCount = 0;
      for (const comp of (team.components || [])) {
        if (byComponent[comp]) {
          totalCount += byComponent[comp].count;
        }
      }
      byTeam[teamKey] = { count: totalCount };
    }
  }

  return { byComponent, byTeam };
}

module.exports = {
  fetchRfeForComponent,
  fetchAllRfeBacklog
};
