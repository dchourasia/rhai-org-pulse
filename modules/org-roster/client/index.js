import { defineAsyncComponent } from 'vue'

export const routes = {
  'home': defineAsyncComponent(() => import('./views/OrgRosterHome.vue')),
  'team-detail': defineAsyncComponent(() => import('./views/TeamDetailView.vue')),
  'org-dashboard': defineAsyncComponent(() => import('./views/OrgDashboardView.vue')),
}
