<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'

const router = useRouter()
const input = ref('')
const sending = ref(false)

async function send() {
  if (!input.value.trim() || sending.value) return
  sending.value = true
  try {
    const res = await api.post('/chatbot/chats/start_chat/', { message: input.value })
    console.log('Chat created:', res.data)
    router.push(`/service/chat/${res.data.chat_id}`)
  } catch (e) {
    console.error(e)
  } finally {
    sending.value = false
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}
</script>

<template>
  <div class="uk-flex uk-flex-center uk-flex-middle" style="min-height: 80vh;">
    <div class="uk-width-1-1 uk-width-large@m uk-padding">
      <!-- Заголовок и статус -->
      <div class="uk-text-center uk-margin-large-bottom">
        <h1 class="uk-heading-medium uk-text-bold uk-margin-remove uk-text-primary">DEADWOOD</h1>
        <p class="uk-text-lead uk-text-muted uk-margin-small-top">
          AI assistant
        </p>
      </div>

      <!-- Форма ввода -->
      <form @submit.prevent="send" class="uk-form-stacked">
        <div class="uk-grid-small" uk-grid>
          <!-- Текстовое поле -->
          <div class="uk-width-expand">
            <div class="uk-inline uk-width-1-1">
              <textarea
                v-model="input"
                @keydown="handleKeyDown"
                :disabled="sending"
                class="uk-textarea uk-border-rounded"
                placeholder="Ask, Search or Chat..."
                rows="3"
                style="resize: none;"
              ></textarea>
            </div>
          </div>
          
          <!-- Кнопки управления -->
          <div class="uk-width-auto">
            <div class="uk-flex uk-flex-column uk-flex-between uk-height-1-1">
              <div class="uk-flex uk-flex-wrap uk-flex-right">
                <!-- Кнопка отправки -->
                <button
                  type="submit"
                  :disabled="sending || !input.trim()"
                  class="uk-button uk-button-primary uk-border-rounded"
                  style="padding: 12px 20px;"
                >
                  <span v-if="sending" uk-spinner="ratio: 0.8"></span>
                  <span v-else uk-icon="arrow-up"></span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
