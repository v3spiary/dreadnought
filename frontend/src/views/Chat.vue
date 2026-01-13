<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'
import { Plus, Pin, Sun, Clock, History, Calendar, Archive } from 'lucide-vue-next';

interface Chat {
  id: string;
  name: string;
  is_pinned?: boolean;
  deleted?: boolean;
  created_at?: string;
  latest_messages: any[];
}

const authStore = useAuthStore()
const route = useRoute()
const chatId = route.params.id as string

const messages = ref<Message[]>([])
const newMessage = ref('')
const isWaiting = ref(false)
const pendingAIMessage = ref({ id: '', content: '' as string })
let socket: WebSocket | null = null

const router = useRouter()
const input = ref('')
const sending = ref(false)

const isHistoryExpanded = ref(true)

// Функция для переключения видимости истории
function toggleHistory() {
  isHistoryExpanded.value = !isHistoryExpanded.value
}

const chats = ref<Chat[]>([])
const chats_loading = ref(false)
const error = ref<string | null>(null)

interface Message {
  id: string;
  content: string;
  sender: any | null;
  message_type?: string;
  is_edited?: boolean;
  created_at?: string;
}

onMounted(async () => {
  await loadChat()
  setupWebSocket()
  await fetchChats()
})

onUnmounted(() => {
  if (socket) socket.close()
})

async function loadChat() {
  try {
    const response = await api.get(`/chatbot/chats/${chatId}/messages/`)
    messages.value = response.data.results || []
  } catch (e) {
    console.error('Error loading chat:', e)
  }
}

function setupWebSocket() {
  if (socket) socket.close()
  if (!authStore.token) return
  const wsUrl = import.meta.env.VITE_WS_BASE_URL + `chat/${chatId}/`
  socket = new WebSocket(wsUrl, [authStore.token])

  socket.onmessage = (e) => {
    const data = JSON.parse(e.data)

    // === USER MESSAGE (эхо) ===
    if (data.type === 'user_message') {
      const msg = messages.value.find(m => m.id === pendingAIMessage.value.id || m.id === Date.now().toString())
      if (msg) {
        msg.id = data.message_id
      }
    }

    // === AI CHUNK ===
    if (data.type === 'ai_chunk') {
      if (!pendingAIMessage.value.id) {
        const newId = Date.now().toString()
        pendingAIMessage.value.id = newId
        pendingAIMessage.value.content = ''
        addMessageToHistory({ id: newId, content: '', sender: null })
      }

      pendingAIMessage.value.content += data.chunk
      const last = messages.value[messages.value.length - 1]
      if (last?.id === pendingAIMessage.value.id) {
        last.content = pendingAIMessage.value.content
      }

      nextTick(scrollToBottom)
    }

    // === AI COMPLETE ===
    if (data.type === 'ai_complete') {
      const last = messages.value[messages.value.length - 1]
      if (last?.id === pendingAIMessage.value.id) {
        last.id = data.message_id
      }
      pendingAIMessage.value = { id: '', content: '' }
      isWaiting.value = false
    }
  }

  socket.onclose = () => { isWaiting.value = false }
  socket.onerror = () => { isWaiting.value = false }
}

function addMessageToHistory(message: Message) {
  messages.value.push(message)
  messages.value = [...messages.value]
  nextTick(scrollToBottom)
}

function scrollToBottom() {
  const container = document.querySelector('.messages-container')
  if (container) container.scrollTop = container.scrollHeight
}

function sendMessage() {
  if (newMessage.value.trim() && !isWaiting.value) {
    isWaiting.value = true
    const userMessage = newMessage.value

    // Временный ID
    const tempId = Date.now().toString()
    addMessageToHistory({
      id: tempId,
      content: userMessage,
      sender: authStore.user
    })

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ message: userMessage }))
    } else {
      isWaiting.value = false
    }
    newMessage.value = ''
  }
}

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

const currentChatId = computed(() => route.params.id as string)

const currentChat = computed(() => 
  chats.value.find(chat => chat.id === currentChatId.value)
)

const isCurrentChatPinned = computed(() => 
  currentChat.value?.is_pinned === true
)

// Функция для отправки при нажатии Enter (без Shift)
function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

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
                    :class="{ 'uk-open': pinnedChats.length > 0 && (isCurrentChatPinned || !currentChatId) }" 
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

            <div class="uk-flex uk-flex-column uk-height-viewport uk-padding-remove">
                <div class="messages-container uk-flex-1 uk-overflow-auto uk-padding">
                    <div class="uk-grid-small" uk-grid>
                        <div v-for="msg in messages" :key="msg.id" class="uk-width-1-1 uk-margin-small-bottom">
                            <div class="uk-card uk-card-default uk-card-body uk-card-small"
                                :class="{ 
                                    'uk-background-primary uk-light': msg.sender,
                                    'uk-background-muted': !msg.sender 
                                }"
                                style="border-radius: 12px;"
                            >
                                <div class="uk-text-break" style="white-space: pre-wrap;">
                                    {{ msg.content }}
                                </div>
                            </div>
                        </div>
                      
                        <div 
                          v-if="isWaiting && !pendingAIMessage.content" 
                          class="uk-width-1-1"
                        >
                            <div class="uk-card uk-card-default uk-card-body uk-card-small uk-background-muted">
                                <div class="uk-flex uk-flex-middle">
                                    <div class="uk-margin-small-right" uk-spinner="ratio: 0.6"></div>
                                    <div>Нейросеть печатает...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="uk-padding uk-background-default uk-box-shadow-medium">
                    <form @submit.prevent="sendMessage" class="uk-form-stacked">
                        <div class="uk-grid-small" uk-grid>
                            <div class="uk-width-expand">
                                <div class="uk-inline uk-width-1-1">
                                    <textarea
                                      v-model="newMessage"
                                      @keydown="handleKeyDown"
                                      :disabled="isWaiting"
                                      class="uk-textarea uk-border-rounded"
                                      placeholder="Ask, Search or Chat..."
                                      rows="2"
                                      style="resize: none;"
                                    ></textarea>
                                </div>
                            </div>
                            
                            <div class="uk-width-auto">
                                <div class="uk-flex uk-flex-column uk-flex-between uk-height-1-1">
                                    <div class="uk-flex uk-flex-wrap uk-flex-right">
                                        <button
                                          type="submit"
                                          :disabled="isWaiting || !newMessage.trim()"
                                          class="uk-button uk-button-primary uk-border-rounded"
                                          style="padding: 12px 20px;"
                                        >
                                            <span uk-icon="arrow-up"></span>
                                        </button>
                                    </div>
                              </div>
                            </div>
                        </div>
                    </form>
                </div>

            </div>

        </div>
    </div>

</template>
