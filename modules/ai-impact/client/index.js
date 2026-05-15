import { defineAsyncComponent } from 'vue'

const ComingSoonView = defineAsyncComponent(() => import('./components/ComingSoonPlaceholder.vue'))

export const routes = {
  'rfe-review': defineAsyncComponent(() => import('./views/RFEReviewView.vue')),
  'feature-review': defineAsyncComponent(() => import('./views/FeatureReviewView.vue')),
  'autofix': defineAsyncComponent(() => import('./views/AutofixView.vue')),
  'ai-factory-guide': defineAsyncComponent(() => import('./views/AIFactoryGuideView.vue')),
  'implementation': ComingSoonView,
  'qe-validation': ComingSoonView,
  'security': ComingSoonView,
  'build-release': defineAsyncComponent(() => import('./views/BuildReleaseView.vue')),
  'documentation': defineAsyncComponent(() => import('./views/DocumentationView.vue')),
}
