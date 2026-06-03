<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">Conforma Insights</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Policy exceptions approved for each RHOAI release, sourced from Enterprise Contract Policy YAMLs.
        </p>
      </div>
      <div class="flex flex-col items-end gap-2">
        <span v-if="state.fetchedAt" class="text-xs text-gray-400 dark:text-gray-500">
          Updated {{ formatDateTime(state.fetchedAt) }}
        </span>
        <div v-if="allReleases.length" class="flex items-center gap-2">
          <label class="text-xs font-bold uppercase tracking-widest text-blue-600 dark:text-blue-400 whitespace-nowrap">
            Release
          </label>
          <div class="relative">
            <select
              v-model="selectedVersion"
              class="appearance-none pl-4 pr-10 py-2.5 text-sm font-semibold rounded-xl border-2 border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-sm cursor-pointer min-w-[230px]"
            >
              <option v-for="r in allReleases" :key="r.version" :value="r.version">
                {{ r.version }} (GA: {{ r.gaDate }})
              </option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-3 flex items-center">
              <svg class="w-4 h-4 text-blue-500 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="state.loading" class="text-sm text-gray-500 dark:text-gray-400">
      Loading conforma data…
    </div>

    <!-- Error / no data -->
    <div v-else-if="state.error" class="rounded-lg border border-amber-300 dark:border-amber-700/60 bg-amber-50 dark:bg-amber-900/20 px-4 py-3 text-sm text-amber-800 dark:text-amber-300">
      {{ state.error }}
    </div>

    <div v-else-if="selectedRelease" :key="selectedVersion" class="space-y-6">

      <!-- Version banner -->
      <div class="rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 dark:from-blue-700 dark:via-indigo-700 dark:to-violet-700 px-6 py-5 shadow-lg text-white">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p class="text-xs font-bold uppercase tracking-widest text-blue-200 mb-1">Viewing Release</p>
            <h3 class="text-3xl font-extrabold tracking-tight leading-none">{{ selectedRelease.version }}</h3>
          </div>
          <div class="flex flex-wrap gap-3">
            <div class="flex flex-col items-center bg-white/15 backdrop-blur-sm rounded-xl px-5 py-2.5 min-w-[90px]">
              <span class="text-[10px] font-semibold uppercase tracking-wider text-blue-200 mb-0.5">GA Date</span>
              <span class="text-sm font-bold">{{ selectedRelease.gaDate }}</span>
            </div>
            <div v-if="selectedRelease.codeFreezeDate" class="flex flex-col items-center bg-white/15 backdrop-blur-sm rounded-xl px-5 py-2.5 min-w-[90px]">
              <span class="text-[10px] font-semibold uppercase tracking-wider text-blue-200 mb-0.5">Code Freeze</span>
              <span class="text-sm font-bold">{{ selectedRelease.codeFreezeDate }}</span>
            </div>
            <div class="flex flex-col items-center rounded-xl px-5 py-2.5 min-w-[90px]"
              :class="selectedRelease.gaDate <= todayStr ? 'bg-emerald-500/30' : 'bg-amber-500/30'">
              <span class="text-[10px] font-semibold uppercase tracking-wider text-blue-200 mb-0.5">Status</span>
              <span class="text-sm font-bold">{{ selectedRelease.gaDate <= todayStr ? 'Shipped' : 'Upcoming' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div
          v-for="card in summaryCards"
          :key="card.label"
          class="rounded-xl border px-4 py-4"
          :class="card.cls"
        >
          <p class="text-[11px] font-semibold uppercase tracking-wider mb-1" :class="card.labelCls">{{ card.label }}</p>
          <p class="text-3xl font-bold tabular-nums" :class="card.valueCls">{{ card.value }}</p>
          <p v-if="card.sub" class="text-xs mt-1 opacity-70" :class="card.labelCls">{{ card.sub }}</p>
        </div>
      </div>

      <!-- Charts row 1 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Horizontal bar: exceptions by category -->
        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/60 p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">Exceptions by Rule Category</h3>
            <ConformaHelpText
              good="Low total count across categories"
              attention="High counts in test/tasks categories may indicate systemic build issues"
              action="Review exception references for resolution paths"
            />
          </div>
          <div v-if="categoryChartData" style="height: 300px; position: relative;">
            <Bar :key="`bar-${chartKey}`" :data="categoryChartData" :options="categoryChartOptions" />
          </div>
          <p v-else class="text-sm text-gray-400 py-8 text-center">No exception data</p>
        </div>

        <!-- Donut: FBC vs Registry + volatile vs permanent -->
        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/60 p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">Exception Distribution</h3>
            <ConformaHelpText
              good="Balanced split with low volatile ratio"
              attention="High volatile ratio means more time-bound risk before GA"
              action="Focus on reducing volatile exceptions through permanent fixes"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-center text-gray-500 dark:text-gray-400 mb-2">FBC vs Components</p>
              <div style="height: 180px; position: relative;">
                <Doughnut :key="`policy-donut-${chartKey}`" :data="policyFileDonutData" :options="donutOptions" />
              </div>
            </div>
            <div>
              <p class="text-xs text-center text-gray-500 dark:text-gray-400 mb-2">By Exception Type</p>
              <div style="height: 180px; position: relative;">
                <Doughnut :key="`type-donut-${chartKey}`" :data="typeDonutData" :options="donutOptions" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts row 2 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Trend across releases -->
        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/60 p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">Exception Trend Across Releases</h3>
            <ConformaHelpText
              good="Decreasing trend across releases"
              attention="Increasing trend means growing technical debt"
              action="Investigate new exceptions added since last release"
            />
          </div>
          <p class="text-xs text-gray-400 dark:text-gray-500 mb-3">All tracked releases, sorted by GA date</p>
          <div v-if="trendChartData" style="height: 240px; position: relative;">
            <Line :key="`line-${chartKey}`" :data="trendChartData" :options="trendChartOptions" />
          </div>
          <p v-else class="text-sm text-gray-400 py-8 text-center">Not enough releases for trend</p>
        </div>

        <!-- Expiry scatter for volatile exceptions -->
        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/60 p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">Volatile Exception Expiry Timeline</h3>
            <div class="flex items-center gap-3">
              <label
                v-if="isLatestUnshipped && actionableCount > 0"
                class="flex items-center gap-1.5 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  v-model="actionableOnly"
                  class="w-3.5 h-3.5 rounded border-red-400 text-red-600 focus:ring-red-500 focus:ring-offset-0 cursor-pointer"
                />
                <span class="text-xs font-semibold text-red-600 dark:text-red-400">
                  Actionable only ({{ actionableCount }})
                </span>
              </label>
              <ConformaHelpText
                good="All dots are green (expire >60 days after GA)"
                attention="Amber/red dots expire near or before GA — these need immediate extension"
                action="Click actionable dots to create or view Jira extension issues"
              />
            </div>
          </div>
          <p class="text-xs text-gray-400 dark:text-gray-500 mb-3">
            <span class="inline-flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-green-500 inline-block"></span>Expires &gt;60d after GA</span>
            &nbsp;
            <span class="inline-flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-400 inline-block"></span>0–60d</span>
            &nbsp;
            <span class="inline-flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-500 inline-block"></span>Before GA</span>
          </p>
          <div v-if="volatileExceptions.length" style="height: 240px; position: relative;">
            <Scatter :key="`scatter-${chartKey}`" :data="scatterChartData" :options="scatterChartOptions" />

            <!-- Hover-triggered persistent tooltip for actionable exceptions -->
            <div
              v-if="hoveredDotTooltip.visible"
              :style="{
                left: `${hoveredDotTooltip.x + 14}px`,
                top: `${Math.max(4, Math.min(hoveredDotTooltip.y - 60, 100))}px`
              }"
              class="absolute z-10 w-80 max-h-[200px] flex flex-col rounded-lg shadow-lg border border-gray-600/30 bg-gray-800/95 dark:bg-gray-900/95 backdrop-blur text-xs text-gray-200"
            >
              <div class="flex items-center justify-between px-3 py-2 border-b border-gray-600/30 shrink-0">
                <span class="font-semibold text-gray-100">
                  {{ hoveredDotTooltip.exceptions.length }} Exception{{ hoveredDotTooltip.exceptions.length === 1 ? '' : 's' }}
                </span>
                <button
                  @click="dismissHoveredTooltip"
                  class="text-gray-400 hover:text-white transition-colors leading-none text-base"
                  title="Close"
                >&times;</button>
              </div>
              <div class="overflow-y-auto divide-y divide-gray-600/30">
                <div
                  v-for="(ex, idx) in hoveredDotTooltip.exceptions"
                  :key="idx"
                  class="px-3 py-2 space-y-1"
                >
                  <div class="flex items-start gap-2">
                    <span
                      :class="CATEGORY_BADGE[ex.category] || CATEGORY_BADGE.other"
                      class="px-1.5 py-0.5 rounded text-[10px] font-medium whitespace-nowrap shrink-0 mt-px"
                    >{{ ex.category }}</span>
                    <span class="text-gray-100 break-all leading-snug">{{ ex.value }}</span>
                  </div>
                  <div class="flex items-center justify-between pl-0.5">
                    <span class="text-gray-400">
                      {{ ex.policyFile === 'fbc' ? 'FBC' : 'Components' }}
                      &middot; Expires {{ new Date(ex.effectiveUntil).toISOString().slice(0, 10) }}
                      <span
                        :class="ex.daysAfterGa <= 0 ? 'text-red-400' : 'text-amber-400'"
                        class="font-medium"
                      >({{ ex.daysAfterGa }}d)</span>
                    </span>
                    <a
                      v-if="ex.extensionJiraUrl"
                      :href="ex.extensionJiraUrl"
                      target="_blank"
                      rel="noopener"
                      @click.stop
                      class="text-blue-400 hover:text-blue-300 font-medium whitespace-nowrap transition-colors"
                    >{{ ex.extensionJiraKey }} &rarr;</a>
                    <button
                      v-else
                      @click.stop="handleCreateJira"
                      class="text-blue-400 hover:text-blue-300 font-medium whitespace-nowrap transition-colors"
                    >Create Jira &rarr;</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-gray-400 py-8 text-center">No volatile exceptions for this release</p>

        </div>
      </div>

      <!-- AI Category Chart (full-width, only for releases with AI data) -->
      <ConformaAiCategoryChart
        v-if="hasAiData"
        :exceptions="flatExceptions"
        :chart-key="chartKey"
      />

      <!-- Detailed exceptions table -->
      <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/60 overflow-hidden">
        <!-- Table header + toolbar -->
        <div class="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">
              All Exceptions for {{ selectedVersion }}
            </h3>
            <span class="text-xs text-gray-400 dark:text-gray-500">
              {{ filteredSortedExceptions.length === flatExceptions.length
                  ? `${flatExceptions.length} total`
                  : `${filteredSortedExceptions.length} of ${flatExceptions.length}` }}
            </span>
          </div>

          <!-- Search + filters -->
          <div class="flex flex-wrap items-center gap-2">
            <!-- Actionable toggle -->
            <button
              v-if="isLatestUnshipped && actionableCount > 0"
              @click="actionableOnly = !actionableOnly"
              :class="actionableOnly
                ? 'bg-red-600 text-white border-red-600 shadow-md'
                : 'bg-white dark:bg-gray-800 text-red-600 border-red-300 dark:border-red-700 hover:bg-red-50 dark:hover:bg-red-900/20'"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
              </svg>
              Actionable ({{ actionableCount }})
            </button>

            <!-- Search -->
            <div class="relative flex-1 min-w-[180px]">
              <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
              </svg>
              <input
                v-model="tableSearch"
                type="text"
                placeholder="Search rule value, reference, comment…"
                class="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Policy filter -->
            <select
              v-model="tableFilterPolicy"
              class="text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Policies</option>
              <option value="fbc">FBC</option>
              <option value="registry">Components</option>
            </select>

            <!-- Type filter -->
            <select
              v-model="tableFilterType"
              class="text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="volatile">Volatile</option>
              <option value="permanent">Permanent</option>
            </select>

            <!-- Category filter -->
            <select
              v-model="tableFilterCategory"
              class="text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option v-for="cat in activeCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>

            <!-- AI Category filter -->
            <select
              v-if="hasAiData"
              v-model="tableFilterAiCategory"
              class="text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All AI Assessments</option>
              <option v-for="(info, key) in AI_CATEGORIES" :key="key" :value="key">{{ info.label }}</option>
            </select>

            <!-- Target release filter -->
            <select
              v-if="hasAiData"
              v-model="tableFilterTargetRelease"
              class="text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Targets</option>
              <option v-for="t in TARGET_RELEASES" :key="t" :value="t">{{ TARGET_RELEASE_LABELS[t]?.label || t }}</option>
            </select>

            <!-- ProdSec policy filter -->
            <select
              v-if="hasAiData"
              v-model="tableFilterPolicyMapped"
              class="text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All ProdSec</option>
              <option value="yes">Policy Mapped</option>
              <option value="no">Not Mapped</option>
            </select>

            <!-- Clear filters -->
            <button
              v-if="hasActiveFilters"
              class="text-xs px-2.5 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              @click="clearTableFilters"
            >
              Clear
            </button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr class="bg-gray-50 dark:bg-gray-800/60 text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                <th
                  v-for="col in TABLE_COLUMNS"
                  :key="col.key"
                  class="px-4 py-3 text-left font-semibold select-none"
                  :class="[col.sortable ? 'cursor-pointer hover:text-gray-700 dark:hover:text-gray-200' : '', col.width || '']"
                  @click="col.sortable && toggleSort(col.key)"
                >
                  <span class="inline-flex items-center gap-1">
                    {{ col.label }}
                    <span v-if="col.sortable" class="text-[10px] leading-none">
                      <template v-if="tableSortKey === col.key">
                        {{ tableSortDir === 'asc' ? '▲' : '▼' }}
                      </template>
                      <template v-else>
                        <span class="text-gray-300 dark:text-gray-600">⇅</span>
                      </template>
                    </span>
                  </span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700/60">
              <tr
                v-for="(ex, idx) in filteredSortedExceptions"
                :key="idx"
                class="hover:bg-gray-50 dark:hover:bg-gray-800/40 transition-colors"
                :class="rowClass(ex)"
              >
                <!-- Policy -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span
                    class="px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase"
                    :class="ex.policyFile === 'fbc' ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300' : 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300'"
                  >{{ ex.policyFile === 'fbc' ? 'FBC' : 'Components' }}</span>
                </td>
                <!-- Type -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span
                    class="px-1.5 py-0.5 rounded text-[10px] font-medium"
                    :class="ex.type === 'volatile' ? 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'"
                  >{{ ex.type }}</span>
                </td>
                <!-- Rule Value -->
                <td class="px-4 py-3 font-mono text-gray-700 dark:text-gray-300 max-w-xs">
                  <span class="block truncate" :title="ex.value">{{ ex.value }}</span>
                </td>
                <!-- Category -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span class="px-1.5 py-0.5 rounded text-[10px] font-medium" :class="categoryBadgeCls(ex.category)">
                    {{ ex.category }}
                  </span>
                </td>
                <!-- AI Assessment -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span
                    v-if="ex.aiCategory && AI_CATEGORIES[ex.aiCategory]"
                    class="px-1.5 py-0.5 rounded text-[10px] font-medium cursor-help"
                    :class="AI_CATEGORIES[ex.aiCategory].badgeCls"
                    :title="ex.aiCategoryReasoning || ''"
                  >{{ AI_CATEGORIES[ex.aiCategory].label }}</span>
                  <span v-else class="text-gray-300 dark:text-gray-600">—</span>
                </td>
                <!-- Target Release -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span
                    v-if="ex.targetRelease && TARGET_RELEASE_LABELS[ex.targetRelease]"
                    class="px-1.5 py-0.5 rounded text-[10px] font-medium"
                    :class="TARGET_RELEASE_LABELS[ex.targetRelease].badgeCls"
                  >{{ TARGET_RELEASE_LABELS[ex.targetRelease].label }}</span>
                  <span v-else class="text-gray-300 dark:text-gray-600">—</span>
                </td>
                <!-- ProdSec Policy Mapped -->
                <td class="px-4 py-3 whitespace-nowrap text-center">
                  <span
                    v-if="ex.policyMapped === true"
                    class="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300"
                    title="Maps to ProdSec policy — compliance blocking"
                  >Yes</span>
                  <span
                    v-else-if="ex.policyMapped === false"
                    class="text-gray-400 dark:text-gray-500 text-[10px]"
                  >No</span>
                  <span v-else class="text-gray-300 dark:text-gray-600">—</span>
                </td>
                <!-- Image -->
                <td class="px-4 py-3 font-mono text-gray-500 dark:text-gray-400 max-w-[180px]">
                  <span class="block truncate" :title="ex.imageUrl || ''">
                    {{ ex.imageUrl ? ex.imageUrl.split('/').pop() : '—' }}
                  </span>
                </td>
                <!-- Effective Until -->
                <td class="px-4 py-3 whitespace-nowrap text-gray-600 dark:text-gray-400">
                  {{ ex.effectiveUntil ? ex.effectiveUntil.slice(0, 10) : '—' }}
                </td>
                <!-- Days After GA -->
                <td class="px-4 py-3 whitespace-nowrap text-center font-semibold" :class="daysAfterGaCls(ex.daysAfterGa)">
                  {{ ex.daysAfterGa !== null ? ex.daysAfterGa : '—' }}
                </td>
                <!-- Reference -->
                <td class="px-4 py-3">
                  <a
                    v-if="ex.reference"
                    :href="ex.reference"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-blue-600 dark:text-blue-400 hover:underline truncate block max-w-[140px]"
                    :title="ex.reference"
                  >{{ refLabel(ex.reference) }}</a>
                  <span v-else class="text-gray-400">—</span>
                </td>
                <!-- Action -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <template v-if="ex.isActionable">
                    <a
                      v-if="ex.extensionJiraKey"
                      :href="ex.extensionJiraUrl"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-200 dark:hover:bg-emerald-900/60 transition-colors"
                      :title="`Extension Jira: ${ex.extensionJiraKey}`"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                      {{ ex.extensionJiraKey }}
                    </a>
                    <button
                      v-else
                      @click="handleCreateJira"
                      class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-900/60 transition-colors cursor-pointer"
                      title="Create extension Jira issue"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>
                      Extend
                    </button>
                  </template>
                  <span v-else class="text-gray-300 dark:text-gray-600">—</span>
                </td>
                <!-- Docs -->
                <td class="px-4 py-3 text-center">
                  <a
                    v-if="CATEGORY_DOCS[ex.category]"
                    :href="CATEGORY_DOCS[ex.category]"
                    target="_blank"
                    rel="noopener noreferrer"
                    :title="`Conforma docs: ${ex.category}`"
                    class="inline-flex items-center justify-center w-6 h-6 rounded text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                    </svg>
                  </a>
                  <span v-else class="text-gray-300 dark:text-gray-600">—</span>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Empty state -->
          <div v-if="!filteredSortedExceptions.length" class="px-5 py-8 text-sm text-gray-400 text-center">
            <template v-if="hasActiveFilters">
              No exceptions match the current filters.
              <button class="ml-1 text-blue-500 hover:underline" @click="clearTableFilters">Clear filters</button>
            </template>
            <template v-else>
              No exceptions recorded for this release.
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state when no releases at all -->
    <div v-else-if="!state.loading && !state.error && !allReleases.length" class="rounded-lg border border-gray-200 dark:border-gray-700 px-6 py-10 text-center">
      <p class="text-sm text-gray-500 dark:text-gray-400">No shipped releases found. Run the ingestion pipeline to populate.</p>
    </div>
  </div>

  <!-- Security Policy Compliance Warning Dialog -->
  <div
    v-if="showJiraWarning"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click.self="showJiraWarning = false"
  >
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden" role="alertdialog" aria-modal="true">
      <div class="flex items-start gap-3 px-6 pt-5 pb-3">
        <div class="shrink-0 mt-0.5 w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Security Policy Compliance Notice</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Per Chris Wright's directive (May 2026)</p>
        </div>
      </div>

      <div class="px-6 pb-4 space-y-3 text-sm text-gray-700 dark:text-gray-300">
        <ul class="space-y-2">
          <li class="flex items-start gap-2">
            <span class="shrink-0 mt-1 w-1.5 h-1.5 rounded-full bg-red-500"></span>
            <span><strong class="text-gray-900 dark:text-gray-100">ProdSec no longer grants exceptions.</strong> Products not meeting security requirements do not ship.</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="shrink-0 mt-1 w-1.5 h-1.5 rounded-full bg-amber-500"></span>
            <span><strong class="text-gray-900 dark:text-gray-100">VP-level sign-off required.</strong> Exceptions must be tracked as risks in the <strong>PRODSECRM</strong> Jira project (not PSX).</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="shrink-0 mt-1 w-1.5 h-1.5 rounded-full bg-blue-500"></span>
            <span>Engage your <strong>Product Security representative</strong> first. Clearly articulate the risk, impact, and mitigations.</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="shrink-0 mt-1 w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            <span>Existing exceptions valid until expiration. Exceptions expiring before <strong>Jun 12, 2026</strong> are auto-extended 2 weeks.</span>
          </li>
        </ul>
      </div>

      <div class="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 dark:bg-gray-800/80 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="showJiraWarning = false"
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
        >Cancel</button>
        <button
          @click="confirmCreateJira"
          class="px-4 py-2 text-sm font-medium text-white bg-amber-600 hover:bg-amber-700 rounded-lg transition-colors"
        >Continue to Jira</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { Bar, Doughnut, Line, Scatter } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

import { useConformaExceptions } from '../composables/useConformaExceptions'
import ConformaHelpText from '../components/ConformaHelpText.vue'
import ConformaAiCategoryChart from '../components/ConformaAiCategoryChart.vue'
import {
  KNOWN_CATEGORIES, CATEGORY_BADGE, CATEGORY_DOCS,
  AI_CATEGORIES, TARGET_RELEASES, TARGET_RELEASE_LABELS,
  EXTENSION_JIRA_TEMPLATE_URL, ACTIONABLE_DAYS_THRESHOLD,
  extractCategory
} from '../constants/conforma'

ChartJS.register(
  CategoryScale, LinearScale,
  BarElement, PointElement, LineElement, ArcElement,
  Tooltip, Legend, Filler
)

// ─── Table column definitions ────────────────────────────────────────────────

const TABLE_COLUMNS = [
  { key: 'policyFile',    label: 'Policy',        sortable: true },
  { key: 'type',          label: 'Type',           sortable: true },
  { key: 'value',         label: 'Rule Value',     sortable: true },
  { key: 'category',      label: 'Category',       sortable: true },
  { key: 'aiCategory',    label: 'AI Assessment',  sortable: true },
  { key: 'targetRelease', label: 'Target',         sortable: true },
  { key: 'policyMapped',  label: 'ProdSec',        sortable: true, width: 'w-16' },
  { key: 'imageUrl',      label: 'Image',          sortable: false },
  { key: 'effectiveUntil',label: 'Effective Until',sortable: true },
  { key: 'daysAfterGa',   label: 'Days After GA',  sortable: true, width: 'w-20' },
  { key: 'reference',     label: 'Reference',      sortable: true },
  { key: 'action',        label: 'Action',         sortable: false, width: 'w-24' },
  { key: 'docs',          label: 'Docs',           sortable: false, width: 'w-12' }
]

// ─── Data ───────────────────────────────────────────────────────────────────

const state = useConformaExceptions()
const selectedVersion = ref(null)
const chartKey = ref(0)
const todayStr = new Date().toLocaleDateString('sv-SE') // YYYY-MM-DD in local time

const allReleases = computed(() => {
  const releases = (state.releases || []).filter(r => r.gaDate)
  const shipped = releases
    .filter(r => r.gaDate <= todayStr)
    .sort((a, b) => b.gaDate.localeCompare(a.gaDate))
  const upcoming = releases
    .filter(r => r.gaDate > todayStr)
    .sort((a, b) => a.gaDate.localeCompare(b.gaDate))
  return [...upcoming, ...shipped]
})

watch(allReleases, (list) => {
  if (list.length && !selectedVersion.value) {
    selectedVersion.value = list[0].version
  }
}, { immediate: true })

const selectedRelease = computed(() =>
  allReleases.value.find(r => r.version === selectedVersion.value) || null
)

// ─── Actionable exceptions ─────────────────────────────────────────────────

const isLatestUnshipped = computed(() => {
  const r = selectedRelease.value
  return r && r.gaDate > todayStr
})

const actionableOnly = ref(false)
const hoveredDotTooltip = ref({ visible: false, x: 0, y: 0, exceptions: [] })
const showJiraWarning = ref(false)

function handleCreateJira() {
  showJiraWarning.value = true
}

function confirmCreateJira() {
  showJiraWarning.value = false
  window.open(EXTENSION_JIRA_TEMPLATE_URL, '_blank', 'noopener')
}

function dismissHoveredTooltip() {
  hoveredDotTooltip.value = { visible: false, x: 0, y: 0, exceptions: [] }
}

watch([actionableOnly, () => selectedVersion.value], dismissHoveredTooltip)

// ─── AI categorization ──────────────────────────────────────────────────────

const aiCategoryMap = computed(() => {
  const map = {}
  const aiData = selectedRelease.value?.aiCategorization?.exceptions || []
  for (const entry of aiData) {
    map[entry.fullName] = {
      category: entry.category,
      reasoning: entry.reasoning,
      targetRelease: entry.targetRelease || null,
      policyMapped: entry.policyMapped ?? null
    }
  }
  return map
})

const hasAiData = computed(() =>
  Object.keys(aiCategoryMap.value).length > 0
)

// ─── Flat exception list (all, used by charts) ───────────────────────────────

const flatExceptions = computed(() => {
  if (!selectedRelease.value) return []
  const r = selectedRelease.value
  const gaMs = r.gaDate ? new Date(r.gaDate).getTime() : null
  const isUpcoming = r.gaDate > todayStr
  const aiMap = aiCategoryMap.value
  const result = []

  for (const policyFile of ['fbc', 'registry']) {
    const exc = r.exceptions?.[policyFile]
    if (!exc) continue

    for (const v of exc.configExcludes || []) {
      const aiInfo = aiMap[v] || null
      result.push({
        policyFile, type: 'permanent', value: v,
        fullName: v,
        category: extractCategory(v),
        imageUrl: null, effectiveUntil: null,
        reference: null, comment: null, daysAfterGa: null,
        extensionJiraKey: null, extensionJiraUrl: null,
        isActionable: false,
        aiCategory: aiInfo?.category || null,
        aiCategoryReasoning: aiInfo?.reasoning || null,
        targetRelease: aiInfo?.targetRelease || null,
        policyMapped: aiInfo?.policyMapped ?? null
      })
    }

    for (const ex of exc.volatileExcludes || []) {
      let daysAfterGa = null
      if (gaMs && ex.effectiveUntil) {
        daysAfterGa = Math.round((new Date(ex.effectiveUntil).getTime() - gaMs) / 86400000)
      }
      const fullName = ex.imageUrl ? `${ex.value}:${ex.imageUrl}` : ex.value
      const isActionable = isUpcoming && daysAfterGa !== null && daysAfterGa <= ACTIONABLE_DAYS_THRESHOLD
      const aiInfo = aiMap[fullName] || aiMap[ex.value] || null
      result.push({
        policyFile, type: 'volatile',
        value: ex.value,
        fullName,
        category: extractCategory(ex.value),
        imageUrl: ex.imageUrl || null,
        effectiveUntil: ex.effectiveUntil || null,
        reference: ex.reference || null,
        comment: ex.comment || null,
        daysAfterGa,
        extensionJiraKey: ex.extensionJiraKey || null,
        extensionJiraUrl: ex.extensionJiraUrl || null,
        isActionable,
        aiCategory: aiInfo?.category || null,
        aiCategoryReasoning: aiInfo?.reasoning || null,
        targetRelease: aiInfo?.targetRelease || null,
        policyMapped: aiInfo?.policyMapped ?? null
      })
    }
  }
  return result
})

const volatileExceptions = computed(() =>
  flatExceptions.value.filter(e => e.type === 'volatile' && e.effectiveUntil)
)

const actionableCount = computed(() =>
  flatExceptions.value.filter(e => e.isActionable).length
)

const actionableExceptions = computed(() =>
  flatExceptions.value
    .filter(e => e.isActionable)
    .sort((a, b) => (a.daysAfterGa ?? 0) - (b.daysAfterGa ?? 0))
)

// ─── Table: search / filter / sort state ────────────────────────────────────

const tableSearch = ref('')
const tableFilterPolicy = ref('')
const tableFilterType = ref('')
const tableFilterCategory = ref('')
const tableFilterAiCategory = ref('')
const tableFilterTargetRelease = ref('')
const tableFilterPolicyMapped = ref('')
const tableSortKey = ref('')
const tableSortDir = ref('asc')

// Reset table controls and force chart remount whenever the selected release changes
watch(selectedVersion, async () => {
  tableSearch.value = ''
  tableFilterPolicy.value = ''
  tableFilterType.value = ''
  tableFilterCategory.value = ''
  tableFilterAiCategory.value = ''
  tableFilterTargetRelease.value = ''
  tableFilterPolicyMapped.value = ''
  tableSortKey.value = ''
  tableSortDir.value = 'asc'
  actionableOnly.value = false
  await nextTick()
  chartKey.value++
})

const hasActiveFilters = computed(() =>
  tableSearch.value.trim() !== '' ||
  tableFilterPolicy.value !== '' ||
  tableFilterType.value !== '' ||
  tableFilterCategory.value !== '' ||
  tableFilterAiCategory.value !== '' ||
  tableFilterTargetRelease.value !== '' ||
  tableFilterPolicyMapped.value !== '' ||
  actionableOnly.value
)

function clearTableFilters() {
  tableSearch.value = ''
  tableFilterPolicy.value = ''
  tableFilterType.value = ''
  tableFilterCategory.value = ''
  tableFilterAiCategory.value = ''
  tableFilterTargetRelease.value = ''
  tableFilterPolicyMapped.value = ''
  actionableOnly.value = false
}

function toggleSort(key) {
  if (tableSortKey.value === key) {
    tableSortDir.value = tableSortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    tableSortKey.value = key
    tableSortDir.value = 'asc'
  }
}

// Categories present in the current release (for the filter dropdown)
const activeCategories = computed(() => {
  const seen = new Set(flatExceptions.value.map(e => e.category))
  return KNOWN_CATEGORIES.filter(c => seen.has(c))
})

const filteredSortedExceptions = computed(() => {
  const needle = tableSearch.value.trim().toLowerCase()
  let rows = flatExceptions.value

  // Actionable filter
  if (actionableOnly.value) rows = rows.filter(e => e.isActionable)

  // Filters
  if (tableFilterPolicy.value) rows = rows.filter(e => e.policyFile === tableFilterPolicy.value)
  if (tableFilterType.value)   rows = rows.filter(e => e.type === tableFilterType.value)
  if (tableFilterCategory.value) rows = rows.filter(e => e.category === tableFilterCategory.value)
  if (tableFilterAiCategory.value) rows = rows.filter(e => e.aiCategory === tableFilterAiCategory.value)
  if (tableFilterTargetRelease.value) rows = rows.filter(e => e.targetRelease === tableFilterTargetRelease.value)
  if (tableFilterPolicyMapped.value) rows = rows.filter(e => tableFilterPolicyMapped.value === 'yes' ? e.policyMapped : e.policyMapped === false)

  if (needle) {
    rows = rows.filter(e =>
      (e.value || '').toLowerCase().includes(needle) ||
      (e.reference || '').toLowerCase().includes(needle) ||
      (e.comment || '').toLowerCase().includes(needle) ||
      (e.imageUrl || '').toLowerCase().includes(needle) ||
      (e.category || '').toLowerCase().includes(needle)
    )
  }

  // Sort — actionable mode auto-sorts by daysAfterGa ascending
  if (actionableOnly.value && !tableSortKey.value) {
    rows = [...rows].sort((a, b) => (a.daysAfterGa ?? 999) - (b.daysAfterGa ?? 999))
  } else if (tableSortKey.value) {
    const dir = tableSortDir.value === 'asc' ? 1 : -1
    rows = [...rows].sort((a, b) => {
      const av = a[tableSortKey.value]
      const bv = b[tableSortKey.value]
      if (av === null && bv === null) return 0
      if (av === null) return dir
      if (bv === null) return -dir
      if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir
      return String(av).localeCompare(String(bv)) * dir
    })
  }

  return rows
})

// ─── Summary cards ──────────────────────────────────────────────────────────

const summaryCards = computed(() => {
  const all = flatExceptions.value
  const fbc = all.filter(e => e.policyFile === 'fbc').length
  const registry = all.filter(e => e.policyFile === 'registry').length
  const volatile = all.filter(e => e.type === 'volatile').length
  return [
    {
      label: 'Total Exceptions', value: all.length,
      cls: 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/60',
      labelCls: 'text-gray-500 dark:text-gray-400',
      valueCls: 'text-gray-900 dark:text-gray-100'
    },
    {
      label: 'FBC Policy', value: fbc,
      cls: 'border-blue-200 dark:border-blue-700/50 bg-blue-50/60 dark:bg-blue-900/20',
      labelCls: 'text-blue-600 dark:text-blue-400',
      valueCls: 'text-blue-700 dark:text-blue-300'
    },
    {
      label: 'Components Policy', value: registry,
      cls: 'border-emerald-200 dark:border-emerald-700/50 bg-emerald-50/60 dark:bg-emerald-900/20',
      labelCls: 'text-emerald-600 dark:text-emerald-400',
      valueCls: 'text-emerald-700 dark:text-emerald-300'
    },
    {
      label: 'Volatile (Time-bound)', value: volatile,
      sub: `${all.length - volatile} permanent`,
      cls: 'border-amber-200 dark:border-amber-700/50 bg-amber-50/60 dark:bg-amber-900/20',
      labelCls: 'text-amber-600 dark:text-amber-400',
      valueCls: 'text-amber-700 dark:text-amber-300'
    }
  ]
})

// ─── Category horizontal bar chart ──────────────────────────────────────────

const categoryChartData = computed(() => {
  const all = flatExceptions.value
  if (!all.length) return null

  const fbcCounts = {}
  const regCounts = {}
  for (const cat of KNOWN_CATEGORIES) { fbcCounts[cat] = 0; regCounts[cat] = 0 }

  for (const e of all) {
    const cat = KNOWN_CATEGORIES.includes(e.category) ? e.category : 'other'
    if (e.policyFile === 'fbc') fbcCounts[cat]++
    else regCounts[cat]++
  }

  const chartCategories = KNOWN_CATEGORIES.filter(c => (fbcCounts[c] || 0) + (regCounts[c] || 0) > 0)

  return {
    labels: chartCategories,
    datasets: [
      {
        label: 'FBC',
        data: chartCategories.map(c => fbcCounts[c]),
        backgroundColor: 'rgba(59,130,246,0.75)',
        borderColor: 'rgb(59,130,246)',
        borderWidth: 1,
        borderRadius: 3
      },
      {
        label: 'Components',
        data: chartCategories.map(c => regCounts[c]),
        backgroundColor: 'rgba(16,185,129,0.75)',
        borderColor: 'rgb(16,185,129)',
        borderWidth: 1,
        borderRadius: 3
      }
    ]
  }
})

const categoryChartOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12 } }, tooltip: { mode: 'index' } },
  scales: {
    x: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, grid: { color: 'rgba(156,163,175,0.15)' } },
    y: { stacked: true, grid: { display: false } }
  }
}

// ─── Donut charts ────────────────────────────────────────────────────────────

const donutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 10, padding: 8, font: { size: 10 } } },
    tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}` } }
  },
  cutout: '62%'
}

const policyFileDonutData = computed(() => {
  const all = flatExceptions.value
  const fbc = all.filter(e => e.policyFile === 'fbc').length
  const reg = all.filter(e => e.policyFile === 'registry').length
  return {
    labels: ['FBC', 'Components'],
    datasets: [{
      data: [fbc, reg],
      backgroundColor: ['rgba(59,130,246,0.8)', 'rgba(16,185,129,0.8)'],
      borderColor: ['rgb(59,130,246)', 'rgb(16,185,129)'],
      borderWidth: 2
    }]
  }
})

const typeDonutData = computed(() => {
  const all = flatExceptions.value
  const vol = all.filter(e => e.type === 'volatile').length
  const perm = all.filter(e => e.type === 'permanent').length
  return {
    labels: ['Volatile', 'Permanent'],
    datasets: [{
      data: [vol, perm],
      backgroundColor: ['rgba(245,158,11,0.8)', 'rgba(107,114,128,0.7)'],
      borderColor: ['rgb(245,158,11)', 'rgb(107,114,128)'],
      borderWidth: 2
    }]
  }
})

// ─── Trend line chart ────────────────────────────────────────────────────────

const trendChartData = computed(() => {
  const sorted = [...allReleases.value].sort((a, b) => a.gaDate.localeCompare(b.gaDate))
  if (sorted.length < 2) return null

  const labels = sorted.map(r => r.version.replace('rhoai-', ''))
  function countFor(r, filter) {
    const all = []
    for (const pf of ['fbc', 'registry']) {
      const exc = r.exceptions?.[pf]
      if (!exc) continue
      for (const v of exc.configExcludes || []) all.push({ type: 'permanent', policyFile: pf, value: v, category: extractCategory(v) })
      for (const ex of exc.volatileExcludes || []) all.push({ type: 'volatile', policyFile: pf, value: ex.value, category: extractCategory(ex.value) })
    }
    return filter ? all.filter(filter).length : all.length
  }

  return {
    labels,
    datasets: [
      {
        label: 'Total',
        data: sorted.map(r => countFor(r)),
        borderColor: 'rgb(139,92,246)',
        backgroundColor: 'rgba(139,92,246,0.1)',
        tension: 0.3, fill: false, pointRadius: 4
      },
      {
        label: 'FIPS',
        data: sorted.map(r => countFor(r, e => e.category === 'fips')),
        borderColor: 'rgb(6,182,212)',
        backgroundColor: 'transparent',
        tension: 0.3, fill: false, pointRadius: 3, borderDash: [3, 2]
      },
      {
        label: 'FBC',
        data: sorted.map(r => countFor(r, e => e.policyFile === 'fbc')),
        borderColor: 'rgb(59,130,246)',
        backgroundColor: 'transparent',
        tension: 0.3, fill: false, pointRadius: 3
      },
      {
        label: 'Components',
        data: sorted.map(r => countFor(r, e => e.policyFile === 'registry')),
        borderColor: 'rgb(16,185,129)',
        backgroundColor: 'transparent',
        tension: 0.3, fill: false, pointRadius: 3
      },
      {
        label: 'Volatile',
        data: sorted.map(r => countFor(r, e => e.type === 'volatile')),
        borderColor: 'rgb(245,158,11)',
        backgroundColor: 'transparent',
        tension: 0.3, fill: false, pointRadius: 3, borderDash: [4, 3]
      }
    ]
  }
})

const trendChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 10, font: { size: 10 } } }, tooltip: { mode: 'index' } },
  scales: {
    y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: 'rgba(156,163,175,0.15)' } },
    x: { grid: { display: false }, ticks: { maxRotation: 35, font: { size: 9 } } }
  }
}

// ─── Scatter (expiry timeline) ───────────────────────────────────────────────

const scatterChartData = computed(() => {
  if (!selectedRelease.value) return { datasets: [] }
  const gaMs = selectedRelease.value.gaDate ? new Date(selectedRelease.value.gaDate).getTime() : 0
  const catIndex = Object.fromEntries(KNOWN_CATEGORIES.map((c, i) => [c, i]))

  const sourceExceptions = actionableOnly.value
    ? volatileExceptions.value.filter(e => e.isActionable)
    : volatileExceptions.value

  const green = [], orange = [], red = [], actionable = []
  for (const ex of sourceExceptions) {
    const expMs = new Date(ex.effectiveUntil).getTime()
    const daysAfter = (expMs - gaMs) / 86400000
    const y = catIndex[ex.category] ?? catIndex['other'] ?? 0
    const point = {
      x: expMs, y, label: ex.value, ref: ex.reference,
      extensionJiraKey: ex.extensionJiraKey,
      extensionJiraUrl: ex.extensionJiraUrl,
      isActionable: ex.isActionable,
      daysAfterGa: ex.daysAfterGa
    }
    if (ex.isActionable) {
      actionable.push(point)
    } else if (daysAfter < 0) {
      red.push(point)
    } else if (daysAfter <= 60) {
      orange.push(point)
    } else {
      green.push(point)
    }
  }

  const datasets = [
    { label: '>60d after GA', data: green, backgroundColor: 'rgba(16,185,129,0.85)', pointRadius: 7 },
    { label: '0-60d after GA', data: orange, backgroundColor: 'rgba(245,158,11,0.85)', pointRadius: 7 },
    { label: 'Before GA', data: red, backgroundColor: 'rgba(239,68,68,0.85)', pointRadius: 7 }
  ]
  if (actionable.length) {
    datasets.push({
      label: 'Actionable',
      data: actionable,
      backgroundColor: 'rgba(239,68,68,0.95)',
      borderColor: 'rgb(239,68,68)',
      borderWidth: 2,
      pointRadius: 10,
      pointStyle: 'rectRounded'
    })
  }
  return { datasets }
})

function onScatterClick(_event, elements) {
  if (!elements.length) return
  const el = elements[0]
  const ds = scatterChartData.value.datasets[el.datasetIndex]
  if (!ds) return
  const point = ds.data[el.index]
  if (!point) return
  if (point.isActionable) return
  if (point.extensionJiraUrl) {
    window.open(point.extensionJiraUrl, '_blank', 'noopener')
  }
}

function onScatterHover(_event, elements, chart) {
  if (!elements.length) return
  const el = elements[0]
  const ds = scatterChartData.value.datasets[el.datasetIndex]
  if (!ds) return
  const point = ds.data[el.index]
  if (!point || !point.isActionable) return

  const matches = actionableExceptions.value.filter(e =>
    new Date(e.effectiveUntil).getTime() === point.x &&
    e.category === KNOWN_CATEGORIES[point.y]
  )
  if (!matches.length) return

  const meta = chart.getDatasetMeta(el.datasetIndex)
  const elem = meta.data[el.index]

  hoveredDotTooltip.value = {
    visible: true,
    x: elem.x,
    y: elem.y,
    exceptions: matches
  }
}

const scatterChartOptions = computed(() => {
  const actionablePoints = actionableOnly.value
    ? volatileExceptions.value.filter(e => e.isActionable)
    : null

  const xScale = {
    type: 'linear',
    grid: { color: 'rgba(156,163,175,0.15)' },
    ticks: {
      callback: (v) => {
        const d = new Date(v)
        return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
      },
      maxTicksLimit: 8
    }
  }

  if (actionablePoints && actionablePoints.length) {
    const times = actionablePoints.map(e => new Date(e.effectiveUntil).getTime())
    const gaMs = selectedRelease.value?.gaDate ? new Date(selectedRelease.value.gaDate).getTime() : 0
    const minT = Math.min(...times, gaMs) - 86400000 * 3
    const maxT = Math.max(...times) + 86400000 * 7
    xScale.min = minT
    xScale.max = maxT
  }

  return {
    responsive: true,
    maintainAspectRatio: false,
    onClick: onScatterClick,
    onHover: actionableOnly.value ? onScatterHover : undefined,
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10, padding: 8, font: { size: 10 } } },
      tooltip: {
        enabled: !actionableOnly.value,
        maxWidth: 420,
        bodyFont: { size: 11 },
        callbacks: {
          title: () => '',
          label: ctx => {
            const p = ctx.raw
            const date = new Date(p.x).toISOString().slice(0, 10)
            const lines = [`${p.label}`, `Expires: ${date}`]
            if (p.daysAfterGa !== null && p.daysAfterGa !== undefined) {
              lines.push(`Days after GA: ${p.daysAfterGa}`)
            }
            if (p.isActionable) {
              lines.push(p.extensionJiraKey
                ? `Jira: ${p.extensionJiraKey} (click to open)`
                : 'Click to create extension Jira')
            }
            return lines
          }
        }
      }
    },
    scales: {
      x: xScale,
      y: {
        ticks: { callback: (v) => KNOWN_CATEGORIES[v] || v, stepSize: 1 },
        min: -0.5,
        max: KNOWN_CATEGORIES.length - 0.5,
        grid: { color: 'rgba(156,163,175,0.10)' }
      }
    }
  }
})

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatDateTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function refLabel(url) {
  if (!url) return ''
  const m = url.match(/\/browse\/([A-Z]+-\d+)/)
  if (m) return m[1]
  try { return new URL(url).pathname.split('/').filter(Boolean).pop() || url } catch { return url }
}

function rowClass(ex) {
  if (ex.daysAfterGa !== null && ex.daysAfterGa < 0) return 'bg-red-50/60 dark:bg-red-900/10'
  if (ex.daysAfterGa !== null && ex.daysAfterGa < 30) return 'bg-amber-50/40 dark:bg-amber-900/10'
  return ''
}

function daysAfterGaCls(days) {
  if (days === null) return 'text-gray-400'
  if (days < 0) return 'text-red-600 dark:text-red-400'
  if (days < 30) return 'text-amber-600 dark:text-amber-400'
  return 'text-emerald-600 dark:text-emerald-400'
}

function categoryBadgeCls(cat) {
  return CATEGORY_BADGE[cat] || CATEGORY_BADGE.other
}
</script>
