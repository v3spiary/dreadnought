<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { SunIcon, MoonIcon, MonitorIcon } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const showDeleteDialog = ref(false)

const profileForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const themes: Array<{ value: 'light' | 'dark' | 'system', label: string, icon: any }> = [
  { value: 'light', label: 'Light', icon: SunIcon },
  { value: 'dark', label: 'Dark', icon: MoonIcon },
  { value: 'system', label: 'System', icon: MonitorIcon }
]

const passwordsMatch = computed(() => {
  return passwordForm.value.new_password === passwordForm.value.confirm_password &&
         passwordForm.value.new_password.length > 0
})

const handleProfileUpdate = async () => {
  const result = await authStore.updateProfile(profileForm.value)
  if (result.success) {
    // Profile updated successfully
    console.log('Profile updated')
  }
}

const handlePasswordChange = async () => {
  if (!passwordsMatch.value) {
    return
  }
  
  const result = await authStore.changePassword(
    passwordForm.value.current_password,
    passwordForm.value.new_password
  )
  
  if (result.success) {
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
    console.log('Password changed successfully')
  }
}

const handleDeleteAccount = async () => {
  // TODO: Implement account deletion
  console.log('Account deletion requested')
  showDeleteDialog.value = false
}

const loadUserData = () => {
  if (authStore.user) {
    profileForm.value = {
      username: authStore.user.username,
      email: authStore.user.email,
      first_name: authStore.user.first_name || '',
      last_name: authStore.user.last_name || ''
    }
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<template>
  <div class="uk-container uk-container-large uk-margin-top">
    <!-- Заголовок -->
    <div>
    <h3 class="uk-margin-middle-bottom">Profile Settings</h3>
  </div>
    
    <!-- Основной контент в сетке -->
    <div class="uk-grid uk-grid-medium" uk-grid>
      <!-- Профиль -->
      <div class="uk-width-1-2@m">
        <div class="uk-card uk-card-default uk-card-body">
          <h3 class="uk-card-title uk-margin-remove-bottom">Profile Information</h3>
          <form @submit.prevent="handleProfileUpdate" class="uk-form-stacked uk-margin-top">
            <div class="uk-margin">
              <label class="uk-form-label" for="username">Username</label>
              <div class="uk-form-controls">
                <input
                  id="username"
                  v-model="profileForm.username"
                  class="uk-input"
                  :disabled="authStore.isLoading"
                />
              </div>
            </div>
            
            <div class="uk-margin">
              <label class="uk-form-label" for="email">Email</label>
              <div class="uk-form-controls">
                <input
                  id="email"
                  v-model="profileForm.email"
                  type="email"
                  class="uk-input"
                  :disabled="authStore.isLoading"
                />
              </div>
            </div>
            
            <div class="uk-grid uk-grid-small" uk-grid>
              <div class="uk-width-1-2">
                <div class="uk-margin">
                  <label class="uk-form-label" for="first_name">First Name</label>
                  <div class="uk-form-controls">
                    <input
                      id="first_name"
                      v-model="profileForm.first_name"
                      class="uk-input"
                      :disabled="authStore.isLoading"
                    />
                  </div>
                </div>
              </div>
              <div class="uk-width-1-2">
                <div class="uk-margin">
                  <label class="uk-form-label" for="last_name">Last Name</label>
                  <div class="uk-form-controls">
                    <input
                      id="last_name"
                      v-model="profileForm.last_name"
                      class="uk-input"
                      :disabled="authStore.isLoading"
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <div class="uk-margin-top">
              <button 
                type="submit" 
                class="uk-button uk-button-primary"
                :disabled="authStore.isLoading"
              >
                <span v-if="authStore.isLoading" uk-spinner="ratio: 0.8"></span>
                {{ authStore.isLoading ? 'Updating...' : 'Update Profile' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- Смена пароля -->
      <div class="uk-width-1-2@m">
        <div class="uk-card uk-card-default uk-card-body">
          <h3 class="uk-card-title uk-margin-remove-bottom">Change Password</h3>
          <form @submit.prevent="handlePasswordChange" class="uk-form-stacked uk-margin-top">
            <div class="uk-margin">
              <label class="uk-form-label" for="current_password">Current Password</label>
              <div class="uk-form-controls">
                <input
                  id="current_password"
                  v-model="passwordForm.current_password"
                  type="password"
                  class="uk-input"
                  :disabled="authStore.isLoading"
                />
              </div>
            </div>
            
            <div class="uk-margin">
              <label class="uk-form-label" for="new_password">New Password</label>
              <div class="uk-form-controls">
                <input
                  id="new_password"
                  v-model="passwordForm.new_password"
                  type="password"
                  class="uk-input"
                  :disabled="authStore.isLoading"
                />
              </div>
            </div>
            
            <div class="uk-margin">
              <label class="uk-form-label" for="confirm_password">Confirm New Password</label>
              <div class="uk-form-controls">
                <input
                  id="confirm_password"
                  v-model="passwordForm.confirm_password"
                  type="password"
                  class="uk-input"
                  :disabled="authStore.isLoading"
                />
              </div>
            </div>
            
            <!-- Индикатор совпадения паролей -->
            <div 
              v-if="passwordForm.new_password && passwordForm.confirm_password"
              class="uk-alert uk-alert-small"
              :class="{
                'uk-alert-success': passwordsMatch,
                'uk-alert-danger': !passwordsMatch
              }"
            >
              <span v-if="passwordsMatch">✓ Passwords match</span>
              <span v-else>✗ Passwords do not match</span>
            </div>
            
            <div class="uk-margin-top">
              <button 
                type="submit" 
                class="uk-button uk-button-primary"
                :disabled="authStore.isLoading || !passwordsMatch"
              >
                <span v-if="authStore.isLoading" uk-spinner="ratio: 0.8"></span>
                {{ authStore.isLoading ? 'Changing...' : 'Change Password' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Внешний вид -->
    <!-- <div class="uk-margin-top">
      <div class="uk-card uk-card-default uk-card-body">
        <h3 class="uk-card-title uk-margin-remove-bottom">Appearance</h3>
        <div class="uk-form-stacked uk-margin-top">
          <div class="uk-margin">
            <label class="uk-form-label">Theme</label>
            <div class="uk-flex uk-flex-wrap uk-gap-small">
              <button
                v-for="theme in themes"
                :key="theme.value"
                :class="{
                  'uk-button uk-button-default': themeStore.theme !== theme.value,
                  'uk-button uk-button-primary': themeStore.theme === theme.value
                }"
                @click="themeStore.setTheme(theme.value)"
                class="uk-flex uk-flex-middle uk-flex-center"
                style="min-width: 100px;"
              >
                <component :is="theme.icon" class="uk-margin-small-right" style="width: 16px; height: 16px;" />
                {{ theme.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div> -->
    
    <!-- Действия с аккаунтом -->
    <div class="uk-margin-top">
      <div class="uk-card uk-card-default uk-card-body">
        <h3 class="uk-card-title uk-margin-remove-bottom">Account Actions</h3>
        <div class="uk-flex uk-flex-between uk-flex-middle uk-margin-top">
          <div>
            <h4 class="uk-text-bold uk-margin-remove">Delete Account</h4>
            <p class="uk-text-muted uk-margin-remove-top">
              Permanently delete your account and all associated data
            </p>
          </div>
          <button 
            class="uk-button uk-button-danger"
            @click="showDeleteDialog = true"
          >
            Delete Account
          </button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно удаления аккаунта -->
    <div v-if="showDeleteDialog" id="delete-modal" uk-modal>
      <div class="uk-modal-dialog uk-modal-body">
        <button class="uk-modal-close-default" type="button" uk-close @click="showDeleteDialog = false"></button>
        <h2 class="uk-modal-title uk-text-danger">Delete Account</h2>
        <p class="uk-text-muted">
          Are you sure you want to delete your account? This action cannot be undone.
        </p>
        <div class="uk-flex uk-flex-right uk-margin-top">
          <button 
            class="uk-button uk-button-default uk-margin-small-right" 
            type="button" 
            @click="showDeleteDialog = false"
          >
            Cancel
          </button>
          <button 
            class="uk-button uk-button-danger" 
            type="button"
            @click="handleDeleteAccount"
          >
            Yes, Delete Account
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
