<template>
  <section class="panel auth-panel">
    <div class="auth-wordmark">
      <img class="brand-logo" src="/logo.svg" alt="Vortex logo" />
      <div class="brand-copy">
        <h1>Vortex</h1>
        <p>by McGuire Technology, LLC</p>
      </div>
    </div>
    <h2>Sign Out</h2>
    <p v-if="signedOut" class="auth-success">You have been signed out.</p>
    <p v-else>Signing you out...</p>
    <p class="auth-switch">
      <RouterLink to="/signin">Go to Sign In</RouterLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { clearTokens } from "../lib/auth";

const signedOut = ref(false);

onMounted(() => {
  clearTokens();
  signedOut.value = true;
});
</script>
