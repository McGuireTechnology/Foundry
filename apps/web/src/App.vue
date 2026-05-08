<template>
  <div v-if="isAuthLayout" class="auth-layout">
    <p v-if="authBanner" class="global-auth-banner">{{ authBanner }}</p>
    <main class="auth-main">
      <RouterView />
    </main>
  </div>
  <div v-else class="layout">
    <header class="topbar">
      <img class="brand-logo" src="/logo.svg" alt="Foundry logo" />
      <div class="brand-copy">
        <h1>Foundry</h1>
        <p>by McGuire Technology, LLC</p>
      </div>
      <nav class="topnav">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <RouterLink v-if="!isSignedIn" to="/signin">Sign In</RouterLink>
        <RouterLink v-if="!isSignedIn" to="/signup">Sign Up</RouterLink>
        <RouterLink v-if="isSignedIn" to="/signout">Sign Out</RouterLink>
      </nav>
    </header>
    <p v-if="authBanner" class="global-auth-banner">{{ authBanner }}</p>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { hasAccessToken } from "./lib/auth";
import { popAuthBanner } from "./lib/authBanner";

const route = useRoute();
const isAuthLayout = computed(() => route.meta.layout === "auth");
const isSignedIn = ref(false);
const authBanner = ref("");

function syncAuthState(): void {
  isSignedIn.value = hasAccessToken();
}

function syncBanner(): void {
  const value = popAuthBanner();
  if (value) {
    authBanner.value = value;
  }
}

onMounted(() => {
  syncAuthState();
  syncBanner();
  window.addEventListener("foundry-auth-changed", syncAuthState);
  window.addEventListener("foundry-auth-banner", syncBanner);
  window.addEventListener("storage", syncAuthState);
});

watch(
  () => route.fullPath,
  () => {
    syncBanner();
  }
);

onUnmounted(() => {
  window.removeEventListener("foundry-auth-changed", syncAuthState);
  window.removeEventListener("foundry-auth-banner", syncBanner);
  window.removeEventListener("storage", syncAuthState);
});
</script>
