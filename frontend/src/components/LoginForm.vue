<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { HTMLAttributes } from "vue"

const props = defineProps<{
  class?: HTMLAttributes["class"]
}>()

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  console.log('Form data before login:', form.value)
  console.log('Form data keys:', Object.keys(form.value))
  console.log('Username value:', form.value.username)
  console.log('Password value:', form.value.password)
  
  const result = await authStore.login(form.value)
  if (result.success) {
    router.push('/service/tracker')
  }
}

onMounted(() => {
  // Redirect if already authenticated
  if (authStore.isAuthenticated) {
    router.push('/service/tracker')
  }
})
</script>

<template>
  <div class="uk-flex uk-flex-center uk-flex-middle" :class="props.class" style="min-height: 100vh;">
    <div class="uk-card uk-card-default uk-card-body uk-box-shadow-medium">
      <div class="uk-text-center uk-margin-medium-bottom">
        <img src="/logo.svg" width="70px" height="70px"/>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="uk-margin">
          <div class="uk-inline">
            <span class="uk-form-icon" uk-icon="icon: user"></span>
            <input
              id="username"
              v-model="form.username"
              class="uk-input"
              type="text"
              placeholder=""
              autocomplete="username"
              required
              :disabled="authStore.isLoading"
            >
          </div>
        </div>

        <div class="uk-margin">
          <div class="uk-inline">
            <span class="uk-form-icon" uk-icon="icon: lock"></span>
            <input
              id="password"
              v-model="form.password"
              class="uk-input"
              type="password"
              placeholder=""
              autocomplete="current-password"
              required
              :disabled="authStore.isLoading"
            >
          </div>
        </div>

        <div class="uk-margin" style="text-align: center;">
          <button
            type="submit"
            class="uk-button uk-button-primary"
            :disabled="authStore.isLoading"
          >
            <span v-if="authStore.isLoading" class="uk-margin-small-right" uk-spinner="ratio: 0.8"></span>
            Login
          </button>
        </div>

        <div
          v-if="authStore.error"
          class="uk-alert uk-alert-danger uk-margin-top"
          uk-alert
        >
          <p>{{ authStore.error }}</p>
        </div>
      </form>
    </div>
  </div>
</template>
