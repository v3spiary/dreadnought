<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'

const router = useRouter()
const input = ref('')
const sending = ref(false)

</script>

<template>
  <div>
    <h3 class="uk-margin-middle-bottom">Information Collector</h3>
  </div>
</template>
