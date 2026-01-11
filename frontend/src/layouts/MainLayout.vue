<script setup lang="ts">
import { useRoute } from 'vue-router';
const route = useRoute();
import { Activity, Container, Rocket, BookOpen, MicVocal, BrainCircuit, User } from 'lucide-vue-next';
</script>

<template>
  <div class="uk-flex uk-flex-column" style="min-height: 100vh;">

    <!-- <nav class="uk-navbar-container uk-box-shadow-small" uk-navbar>
      <div class="uk-navbar-left">
        <img src="/logo.svg" width="70px" height="70px"/>
      </div>
      
      <div class="uk-navbar-right">
        <ul class="uk-navbar-nav">
          <li><a href="" @click="authStore.logout">Logout</a></li>
        </ul>
      </div>
    </nav> -->

    <div class="uk-background-primary">
        <nav class="uk-navbar-container uk-navbar-transparent uk-light">
            <div class="uk-container">
                <div uk-navbar>

                    <div class="uk-navbar-left">
                        <a class="uk-navbar-item uk-logo" href="#" aria-label="Back to Home"><img src="/logo.svg" style="filter: invert(1);" width="42px" height="42px"/></a>
                    </div>

                    <div class="uk-navbar-right">

                        <ul class="uk-navbar-nav">
                            <li v-if="$route.path === '/service/tracker'" class="uk-active">
                                <a href="/service/tracker">
                                    <Activity :size="20" class="icon" style="padding-right: 3px;" /> Tracker
                                </a>
                            </li>
                            <li v-else>
                                <a href="/service/tracker">
                                    <Activity :size="20" class="icon" style="padding-right: 3px;" /> Tracker
                                </a>
                            </li>
                            <li v-if="$route.path === '/service/collector'" class="uk-active">
                                <a href="/service/collector">
                                    <Container :size="20" class="icon" style="padding-right: 3px;" /> Collector
                                </a>
                            </li>
                            <li v-else>
                                <a href="/service/collector">
                                    <Container :size="20" class="icon" style="padding-right: 3px;" /> Collector
                                </a>
                            </li>
                            <li v-if="$route.path === '/service/startup'" class="uk-active">
                                <a href="/service/startup">
                                    <Rocket :size="20" class="icon" style="padding-right: 3px;" /> Startup
                                </a>
                            </li>
                            <li v-else>
                                <a href="/service/startup">
                                    <Rocket :size="20" class="icon" style="padding-right: 3px;" /> Startup
                                </a>
                            </li>
                            <li v-if="$route.path === '/service/reader'" class="uk-active">
                                <a href="/service/reader">
                                    <BookOpen :size="20" class="icon" style="padding-right: 3px;" /> Reader
                                </a>
                            </li>
                            <li v-else>
                                <a href="/service/reader">
                                    <BookOpen :size="20" class="icon" style="padding-right: 3px;" /> Reader
                                </a>
                            </li>
                            <li v-if="$route.path === '/service/transcription'" class="uk-active">
                                <a href="/service/transcription">
                                    <MicVocal :size="20" class="icon" style="padding-right: 3px;" /> Transcription
                                </a>
                            </li>
                            <li v-else>
                                <a href="/service/transcription">
                                    <MicVocal :size="20" class="icon" style="padding-right: 3px;" /> Transcription
                                </a>
                            </li>
                            <li v-if="$route.path === '/service/chat'" class="uk-active">
                                <a href="/service/chat">
                                    <BrainCircuit :size="20" class="icon" style="padding-right: 3px;" /> AI Assistant
                                </a>
                            </li>
                            <li v-else>
                                <a href="/service/chat">
                                    <BrainCircuit :size="20" class="icon" style="padding-right: 3px;" /> AI Assistant
                                </a>
                            </li>
                            <li v-if="$route.path === '/service/profile'" class="uk-active">
                                <a href="/service/profile">
                                    <User :size="20" class="icon" style="padding-right: 3px;" /> Profile
                                </a>
                            </li>
                            <li v-else>
                                <a href="/service/profile">
                                    <User :size="20" class="icon" style="padding-right: 3px;" /> Profile
                                </a>
                            </li>
                        </ul>

                    </div>

                </div>
            </div>
        </nav>
    </div>

    <main class="uk-flex-1 uk-padding">
      <router-view />
    </main>
  </div>
</template>
