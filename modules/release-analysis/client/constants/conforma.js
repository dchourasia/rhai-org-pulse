// FIPS is first because it is matched by keyword, not by value prefix.
export const KNOWN_CATEGORIES = [
  'fips', 'hermetic_task', 'test', 'tasks', 'schedule',
  'sbom_spdx', 'rpm_signature', 'cve', 'other'
]

export const CATEGORY_BADGE = {
  fips:                  'bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300',
  hermetic_task:         'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300',
  test:                  'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
  tasks:                 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300',
  schedule:              'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300',
  sbom_spdx:             'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
  rpm_signature:         'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
  cve:                   'bg-pink-100 dark:bg-pink-900/40 text-pink-700 dark:text-pink-300',
  source_image:          'bg-teal-100 dark:bg-teal-900/40 text-teal-700 dark:text-teal-300',
  step_image_registries: 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300',
  other:                 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
}

export const CATEGORY_DOCS = {
  fips:                  'https://conforma.dev/docs/policy/packages/release_test.html',
  hermetic_task:         'https://conforma.dev/docs/policy/packages/release_hermetic_task.html',
  test:                  'https://conforma.dev/docs/policy/packages/release_test.html',
  tasks:                 'https://conforma.dev/docs/policy/packages/release_tasks.html',
  schedule:              'https://conforma.dev/docs/policy/packages/release_schedule.html',
  sbom_spdx:             'https://conforma.dev/docs/policy/packages/release_sbom_spdx.html',
  rpm_signature:         'https://conforma.dev/docs/policy/packages/release_rpm_signature.html',
  cve:                   'https://conforma.dev/docs/policy/packages/release_cve.html',
  source_image:          'https://conforma.dev/docs/policy/packages/release_source_image.html',
  step_image_registries: 'https://conforma.dev/docs/policy/packages/task_step_image_registries.html',
}

export const EXTENSION_JIRA_TEMPLATE_URL = 'https://redhat.atlassian.net/browse/RHOAIENG-62569'

export const ACTIONABLE_DAYS_THRESHOLD = 7

export const AI_CATEGORIES = {
  always_expected: {
    label: 'Always Expected',
    description: 'Cannot be resolved; inherently needed',
    badgeCls: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400',
    color: 'rgba(107,114,128,0.8)',
    borderColor: 'rgb(107,114,128)'
  },
  long_term_fix: {
    label: 'Long-term Fix',
    description: 'Known resolution path, requires significant effort',
    badgeCls: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
    color: 'rgba(59,130,246,0.8)',
    borderColor: 'rgb(59,130,246)'
  },
  quick_fix: {
    label: 'Quick Fix',
    description: 'Straightforward fix available',
    badgeCls: 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300',
    color: 'rgba(16,185,129,0.8)',
    borderColor: 'rgb(16,185,129)'
  },
  already_fixed: {
    label: 'Already Fixed',
    description: 'Root cause addressed; exception likely removable',
    badgeCls: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
    color: 'rgba(139,92,246,0.8)',
    borderColor: 'rgb(139,92,246)'
  }
}

export function extractCategory(value) {
  if (!value) return 'other'
  if (value.toLowerCase().includes('fips')) return 'fips'
  const prefixKnown = ['hermetic_task', 'test', 'tasks', 'schedule', 'sbom_spdx', 'rpm_signature', 'cve', 'source_image', 'step_image_registries']
  const prefix = value.split('.')[0].split(':')[0]
  return prefixKnown.includes(prefix) ? prefix : 'other'
}
