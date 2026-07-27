import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/welcome' },
  { path: '/welcome', name: 'welcome', component: () => import('../views/WelcomeView.vue') },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/search', name: 'search', component: () => import('../views/SearchView.vue') },
  { path: '/document/:id', name: 'document', component: () => import('../views/DocumentView.vue') },
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  { path: '/register', name: 'register', component: () => import('../views/RegisterView.vue') },
  { path: '/forgot_password', name: 'forgot_password', component: () => import('../views/ForgotPasswordView.vue') },
  { path: '/upload', name: 'upload', component: () => import('../views/UploadView.vue') },
  { path: '/my_documents', name: 'my_documents', component: () => import('../views/MyDocumentsView.vue') },
  { path: '/edit_document/:id', name: 'edit_document', component: () => import('../views/EditDocumentView.vue') },
  { path: '/favorites', name: 'favorites', component: () => import('../views/FavoritesView.vue') },
  { path: '/history', name: 'history', component: () => import('../views/HistoryView.vue') },
  { path: '/stats', name: 'stats', component: () => import('../views/StatsView.vue') },
  { path: '/profile', name: 'profile', component: () => import('../views/ProfileView.vue') },
  { path: '/citation/:id', name: 'citation', component: () => import('../views/CitationView.vue') },
  { path: '/typhoon', name: 'typhoon', component: () => import('../views/TyphoonView.vue') },
  { path: '/typhoon/:id', name: 'typhoon_detail', component: () => import('../views/TyphoonDetail.vue') },
  { path: '/earthquake', name: 'earthquake', component: () => import('../views/EarthquakeView.vue') },
  { path: '/earthquake/:id', name: 'earthquake_detail', component: () => import('../views/EarthquakeDetail.vue') },
  { path: '/tornado', name: 'tornado', component: () => import('../views/TornadoView.vue') },
  { path: '/tornado/:id', name: 'tornado_detail', component: () => import('../views/TornadoDetail.vue') },
  { path: '/:pathMatch(.*)*', name: 'not_found', component: () => import('../views/ErrorView.vue') },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _from, next) => {
  const pub = ['/welcome', '/login', '/register', '/forgot_password']
  const t = localStorage.getItem('token')
  if (!t && !pub.includes(to.path)) next('/welcome')
  else if (t && pub.includes(to.path)) next('/dashboard')
  else next()
})

export default router
