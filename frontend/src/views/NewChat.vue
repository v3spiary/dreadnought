<script setup lang="ts">
import { useRouter, useRoute } from "vue-router"
import { api } from '@/lib/api'
import { ref, onMounted, computed, watch } from 'vue'
import { Plus, Pin, Sun, Clock, History, Calendar, Archive } from 'lucide-vue-next';

interface Chat {
  id: string;
  name: string;
  is_pinned?: boolean;
  deleted?: boolean;
  created_at?: string;
  latest_messages: any[];
}

const currentChatId = computed(() => route.params.id as string)

const router = useRouter()
const route = useRoute()
const input = ref('')
const sending = ref(false)

const chats = ref<Chat[]>([])
const chats_loading = ref(false)
const error = ref<string | null>(null)

async function fetchChats() {
  try {
    chats_loading.value = true
    error.value = null
    console.log('Fetching chats from API...')
    
    // Проверьте URL в браузере: 
    // Откройте DevTools -> Network и посмотрите, уходит ли запрос
    const response = await api.get('/chatbot/chats/')
    console.log('API Response:', response)
    console.log('Response data:', response.data)
    
    // Проверьте структуру ответа
    if (response.data && response.data.results) {
      chats.value = response.data.results || []
      console.log('Loaded chats:', chats.value.length, 'chats')
    } else if (Array.isArray(response.data)) {
      // Если API возвращает просто массив
      chats.value = response.data
      console.log('Loaded chats (array):', chats.value.length, 'chats')
    } else {
      console.warn('Unexpected API response structure:', response.data)
      chats.value = []
    }
  } catch (e: any) {
    console.error('Error fetching chats:', e)
    error.value = e.message || 'Failed to load chats'
    
    // Детальная отладка
    if (e.response) {
      console.error('Response status:', e.response.status)
      console.error('Response data:', e.response.data)
      error.value = `API Error: ${e.response.status} - ${JSON.stringify(e.response.data)}`
    }
  } finally {
    chats_loading.value = false
  }
}

const pinnedChats = computed(() => 
  chats.value.filter(chat => chat.is_pinned && !chat.deleted)
)

const historyChats = computed(() => 
  chats.value.filter(chat => !chat.is_pinned && !chat.deleted)
)

async function send() {
  if (!input.value.trim() || sending.value) return
  sending.value = true
  try {
    console.log('Sending message:', input.value)
    const res = await api.post('/chatbot/chats/start_chat/', { 
      message: input.value 
    })
    console.log('Chat created:', res.data)
    
    if (res.data.chat_id) {
      router.push(`/service/chat/${res.data.chat_id}`)
      // Обновляем список чатов после создания нового
      await fetchChats()
    }
  } catch (e: any) {
    console.error('Error creating chat:', e)
    if (e.response) {
      console.error('Response:', e.response.status, e.response.data)
    }
  } finally {
    sending.value = false
    input.value = '' // Очищаем поле ввода
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

onMounted(async () => {
  console.log('Component mounted')
  await fetchChats()
})


function parseCustomDate(dateStr: string): Date {
  // Формат: "13.01.2026 07:13"
  const [datePart, timePart] = dateStr.split(' ');
  const [day, month, year] = datePart.split('.').map(Number);
  const [hours, minutes] = timePart.split(':').map(Number);
  return new Date(year, month - 1, day, hours, minutes);
}

const groupedHistoryChats = computed(() => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const weekAgo = new Date(today);
  weekAgo.setDate(weekAgo.getDate() - 7);
  const monthAgo = new Date(today);
  monthAgo.setMonth(monthAgo.getMonth() - 1);
  const yearAgo = new Date(today);
  yearAgo.setFullYear(yearAgo.getFullYear() - 1);

  const groups: Record<string, Chat[]> = {
    today: [],
    yesterday: [],
    week: [],
    month: [],
    year: [],
    older: []
  };

  historyChats.value.forEach(chat => {
    if (!chat.created_at) {
      groups.older.push(chat);
      return;
    }

    const chatDate = parseCustomDate(chat.created_at);
    const chatDay = new Date(chatDate.getFullYear(), chatDate.getMonth(), chatDate.getDate());

    if (chatDay.getTime() === today.getTime()) {
      groups.today.push(chat);
    } else if (chatDay.getTime() === yesterday.getTime()) {
      groups.yesterday.push(chat);
    } else if (chatDate >= weekAgo) {
      groups.week.push(chat);
    } else if (chatDate >= monthAgo) {
      groups.month.push(chat);
    } else if (chatDate >= yearAgo) {
      groups.year.push(chat);
    } else {
      groups.older.push(chat);
    }
  });

  // Сортируем чаты внутри групп (новые сверху)
  Object.keys(groups).forEach(key => {
    groups[key].sort((a, b) => {
      const dateA = a.created_at ? parseCustomDate(a.created_at).getTime() : 0;
      const dateB = b.created_at ? parseCustomDate(b.created_at).getTime() : 0;
      return dateB - dateA;
    });
  });

  return groups;
});

const visibleHistoryGroups = computed(() => {
  const groups = [];
  if (groupedHistoryChats.value.today.length > 0) {
    groups.push({ label: 'Сегодня', key: 'today', icon: 'sun' });
  }
  if (groupedHistoryChats.value.yesterday.length > 0) {
    groups.push({ label: 'Вчера', key: 'yesterday', icon: 'history' });
  }
  if (groupedHistoryChats.value.week.length > 0) {
    groups.push({ label: 'За неделю', key: 'week', icon: 'calendar' });
  }
  if (groupedHistoryChats.value.month.length > 0) {
    groups.push({ label: 'За месяц', key: 'month', icon: 'calendar' });
  }
  if (groupedHistoryChats.value.year.length > 0) {
    groups.push({ label: 'За год', key: 'year', icon: 'calendar' });
  }
  if (groupedHistoryChats.value.older.length > 0) {
    groups.push({ label: 'Больше года', key: 'older', icon: 'archive' });
  }
  return groups;
});

const historyGroupCounts = computed(() => {
  return {
    today: groupedHistoryChats.value.today.length,
    yesterday: groupedHistoryChats.value.yesterday.length,
    week: groupedHistoryChats.value.week.length,
    month: groupedHistoryChats.value.month.length,
    year: groupedHistoryChats.value.year.length,
    older: groupedHistoryChats.value.older.length
  };
});

watch(() => route.path, async (newPath) => {
  console.log('Route changed to:', newPath)
  // Обновляем чаты только если мы не на странице чата
  if (!newPath.includes('/service/chat/')) {
    await fetchChats()
  }
})
</script>

<template>
  <div class="uk-text-center" uk-grid>
    <div class="uk-width-1-6@m">
            <!-- Индикатор загрузки -->
            <div v-if="chats_loading" class="uk-text-muted uk-text-small">
                Loading chats...
            </div>
            
            <!-- Сообщение об ошибке -->
            <div v-if="error" class="uk-alert-danger uk-alert-small" uk-alert>
                <p class="uk-text-small">{{ error }}</p>
            </div>

            <ul class="uk-nav-default" uk-nav v-if="!chats_loading && !error">
                <li>
                    <a href="#" @click.prevent="router.push('/service/chat')"><Plus :size="20" stroke-width="1.5" style="padding-right: 5px;" /> New chat</a>
                </li>

                <!-- Pinned chats -->
                <li class="uk-parent" 
                    v-if="pinnedChats.length > 0">
                    <a href="#"><Pin :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Pinned <span class="uk-badge">{{ pinnedChats.length }}</span><span uk-nav-parent-icon></span></a>
                    <ul class="uk-nav-sub">
                        <li v-for="chat in pinnedChats" :key="chat.id" 
                            :class="{ 'uk-active': chat.id === currentChatId }">
                            <a :href="`/service/chat/${chat.id}`">
                                {{ chat.name?.length > 20 ? chat.name.substring(0, 15) + '...' : chat.name || `Chat ${chat.id.slice(0, 8)}` }}
                            </a>
                        </li>
                    </ul>
                </li>

                <!-- History chats -->
                <template v-for="group in visibleHistoryGroups" :key="group.key">
                    <li class="uk-parent" 
                        :class="{ 'uk-open': groupedHistoryChats[group.key].some(c => c.id === currentChatId) }">
                        <a href="#">
                            <Sun v-if="group.icon === 'sun'" :size="20" stroke-width="1.5" style="padding-right: 5px;" />
                            <History v-else-if="group.icon === 'history'" :size="20" stroke-width="1.5" style="padding-right: 5px;" />
                            <Calendar v-else-if="group.icon === 'calendar'" :size="20" stroke-width="1.5" style="padding-right: 5px;" />
                            <Archive v-else-if="group.icon === 'archive'" :size="20" stroke-width="1.5" style="padding-right: 5px;" />

                            {{ group.label }}
                            <span class="uk-text-muted uk-text-small" style="float: right; padding-right: 10px;">
                                <span class="uk-badge">{{ groupedHistoryChats[group.key].length }}</span>
                            </span>
                            <span uk-nav-parent-icon></span>
                        </a>
                        <ul class="uk-nav-sub">
                            <li v-for="chat in groupedHistoryChats[group.key]" :key="chat.id"
                                :class="{ 'uk-active': chat.id === currentChatId }">
                                <a :href="`/service/chat/${chat.id}`">
                                    {{ chat.name?.length > 20 ? chat.name.substring(0, 15) + '...' : chat.name || `Чат ${chat.id.slice(0, 8)}` }}
                                </a>
                            </li>
                        </ul>
                    </li>
                </template>
                
            </ul>
        </div>
    
    <div class="uk-width-expand@m">
      <div>
        <div class="uk-animation-toggle" tabindex="0">
          <img 
            class="uk-animation-stroke" 
            src="/logo.svg" 
            width="200" 
            height="200" 
            alt="" 
            uk-svg="stroke-animation: true"
          >
        </div>
      </div>

      <h4 class="header">DΞΛDWOOD</h4>

      <div class="uk-flex uk-flex-center uk-flex-middle">
        <form 
          @submit.prevent="send" 
          class="uk-form-stacked uk-width-2xlarge"
        >
          <div class="uk-card uk-card-default uk-card-body uk-border-rounded uk-padding-small">
            <textarea 
              class="uk-textarea" 
              v-model="input"
              @keydown="handleKeyDown"
              :disabled="sending"
              rows="5" 
              style="resize: none; border: none !important; box-shadow: none !important;"
              placeholder="Ask, Search or Chat..."
            ></textarea>
            
            <div class="uk-flex uk-flex-between uk-flex-middle uk-margin-small-top">
              <div class="uk-button-group">
                <button 
                  class="uk-button uk-button-small uk-button-default uk-border-rounded uk-margin-small-right"
                  type="button"
                >
                  Агент
                </button>
                <button 
                  class="uk-button uk-button-small uk-button-default uk-border-rounded uk-margin-small-right"
                  type="button"
                >
                  RAG
                </button>
              </div>
              <button 
                class="uk-button uk-button-primary uk-button-small uk-border-rounded"
                type="submit"
                :disabled="sending || !input.trim()"
              >
                <span v-if="sending">Sending...</span>
                <span v-else>Отправить</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
  @font-face {
    font-family: namu;
    src: url('/fonts/namu.ttf');
  }

  .header {
    font-family: namu;
    letter-spacing: 13px;
  }
  
  /* Стили для ссылок */
  .uk-nav-sub a {
    text-decoration: none;
  }
  
  .uk-nav-sub a:hover {
    text-decoration: underline;
  }
</style>
