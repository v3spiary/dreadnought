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
  <div class="uk-width-1-6">
    <ul class="uk-nav-default" uk-nav>
        <li class="uk-active"><a href="#">New chat</a></li>
        <li class="uk-parent uk-open">
            <a href="#">Pinned <span uk-nav-parent-icon></span></a>
            <ul class="uk-nav-sub">
                <li><a href="#">Здарова</a></li>
            </ul>
        </li>
        <li class="uk-parent">
            <a href="#">History <span uk-nav-parent-icon></span></a>
            <ul class="uk-nav-sub">
                <li><a href="#">Sub item</a></li>
                <li><a href="#">Sub item</a></li>
            </ul>
        </li>
    </ul>
  </div>
</template>
