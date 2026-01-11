<script setup lang="ts">
const goBack = () => {
  window.history.back()
}
</script>

<template>
  <div class="uk-flex uk-flex-center uk-flex-middle" style="min-height: 100vh;">
    <div class="uk-text-center uk-width-large">
      <div class="uk-margin-medium-bottom">
        <h1>404 Not Found</h1>
        <p>
          The page you're looking for doesn't exist.
        </p>
      </div>
      
      <div class="uk-margin">
        <a 
          href="javascript:void(0)" 
          @click="goBack"
          class="uk-button uk-button-primary"
        >
          Go back
        </a>
      </div>
    </div>
  </div>
</template>
