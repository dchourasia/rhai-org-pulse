<template>
  <div class="overflow-x-auto">
    <!-- Filter by role -->
    <div v-if="uniqueRoles.length > 1" class="mb-4 flex flex-wrap gap-2">
      <button
        @click="roleFilter = null"
        class="px-3 py-1 rounded text-xs font-medium transition-colors border"
        :class="!roleFilter
          ? 'bg-primary-600 text-white border-primary-600'
          : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'"
      >
        All roles
      </button>
      <button
        v-for="role in uniqueRoles"
        :key="role"
        @click="roleFilter = role"
        class="px-3 py-1 rounded text-xs font-medium transition-colors border"
        :class="roleFilter === role
          ? 'bg-primary-600 text-white border-primary-600'
          : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'"
      >
        {{ role }}
      </button>
    </div>

    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:text-gray-700"
            @click="toggleSort(col.key)"
          >
            {{ col.label }}
            <span v-if="sortKey === col.key" class="ml-1">{{ sortAsc ? '↑' : '↓' }}</span>
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr
          v-for="member in sortedMembers"
          :key="member.name"
          class="hover:bg-gray-50"
          :class="{ 'opacity-50': getStatus(member) === 'Not Confirmed' }"
        >
          <td class="px-4 py-3 text-sm whitespace-nowrap">
            <a
              :href="personLink(member.name)"
              class="text-primary-600 hover:underline"
              @click.stop
            >
              {{ member.name }}
            </a>
            <span
              v-if="getStatus(member) === 'Not Confirmed'"
              class="ml-1 inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-yellow-100 text-yellow-800"
            >
              Unconfirmed
            </span>
          </td>
          <td class="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">{{ member.managerUid || member.manager || '—' }}</td>
          <td class="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">{{ getSpecialty(member) }}</td>
          <td class="px-4 py-3 text-sm text-gray-600">{{ getComponent(member) }}</td>
          <td class="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">{{ member.geo || member.region || '—' }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="sortedMembers.length === 0" class="text-center py-8 text-gray-500 text-sm">
      No members found.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useModuleLink } from '@shared/client/composables/useModuleLink'

const { linkTo } = useModuleLink()

const props = defineProps({
  members: { type: Array, required: true }
})

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'manager', label: 'Manager' },
  { key: 'specialty', label: 'Role' },
  { key: 'component', label: 'Component' },
  { key: 'geo', label: 'Location' },
]

function personLink(name) {
  return linkTo('team-tracker', 'person-detail', { person: name })
}

function getSpecialty(member) {
  return member.engineeringSpeciality || member.specialty || member.title || '—'
}

function getStatus(member) {
  return member.status || member.customFields?.status || 'Confirmed'
}

function getComponent(member) {
  return member.component || '—'
}

const sortKey = ref('name')
const sortAsc = ref(true)
const roleFilter = ref(null)

function toggleSort(key) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

const uniqueRoles = computed(() => {
  const roles = new Set()
  for (const m of props.members) {
    const spec = getSpecialty(m)
    if (spec && spec !== '—') roles.add(spec)
  }
  return [...roles].sort()
})

const sortedMembers = computed(() => {
  let result = props.members
  if (roleFilter.value) {
    result = result.filter(m => getSpecialty(m) === roleFilter.value)
  }

  return [...result].sort((a, b) => {
    let aVal, bVal
    if (sortKey.value === 'specialty') {
      aVal = getSpecialty(a)
      bVal = getSpecialty(b)
    } else if (sortKey.value === 'component') {
      aVal = getComponent(a)
      bVal = getComponent(b)
    } else if (sortKey.value === 'manager') {
      aVal = a.managerUid || a.manager
      bVal = b.managerUid || b.manager
    } else if (sortKey.value === 'geo') {
      aVal = a.geo || a.region
      bVal = b.geo || b.region
    } else {
      aVal = a[sortKey.value]
      bVal = b[sortKey.value]
    }
    aVal = (aVal || '').toString().toLowerCase()
    bVal = (bVal || '').toString().toLowerCase()
    const cmp = aVal.localeCompare(bVal)
    return sortAsc.value ? cmp : -cmp
  })
})
</script>
