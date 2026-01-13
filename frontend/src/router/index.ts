import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/layouts/MainLayout.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/auth',
      meta: { requiresGuest: true },
      children: [
        { path: 'login', component: () => import('@/views/Login.vue') },
        // { path: 'register', component: () => import('@/views/Register.vue') },
        // { path: 'reset-password', component: () => import('@/views/Reset.vue') },
        // { path: 'reset-password-confirm/:uid/:token', component: () => import('@/views/ResetConfirm.vue') },
      ],
    },
    {
      path: '/service',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        { path: 'tracker', component: () => import('@/views/Tracker.vue'), meta: { title: 'Tracker' } },
        { path: 'collector', component: () => import('@/views/Collector.vue'), meta: { title: 'Collector' } },
        { path: 'startup', component: () => import('@/views/Startup.vue'), meta: { title: 'Startup' } },
        { path: 'reader', component: () => import('@/views/Reader.vue'), meta: { title: 'Reader' } },
        { path: 'transcription', component: () => import('@/views/Transcription.vue'), meta: { title: 'Transcription' } },
        { path: 'chat', component: () => import('@/views/NewChat.vue'), meta: { title: 'Chat' } },
        { path: 'chat/:id', component: () => import('@/views/Chat.vue'), meta: { title: 'Loading...' } },
        { path: 'profile', component: () => import('@/views/Profile.vue'), meta: { title: 'Profile' } },
      ],
    },
    { path: '/', redirect: '/auth/login' },
    { path: '/:pathMatch(.*)*', component: () => import('@/views/NotFound.vue') },
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth store if not already done
  if (!authStore.isAuthenticated && localStorage.getItem('access_token')) {
    await authStore.init()
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/auth/login')
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/service/tracker')
    return
  }
  
  next()
})

export default router
