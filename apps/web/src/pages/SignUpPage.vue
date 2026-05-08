<template>
  <section class="panel auth-panel">
    <div class="auth-wordmark">
      <img class="brand-logo" src="/logo.svg" alt="Foundry logo" />
      <div class="brand-copy">
        <h1>Foundry</h1>
        <p>by McGuire Technology, LLC</p>
      </div>
    </div>
    <h2>Sign Up</h2>
    <p>Create your Foundry account.</p>
    <form class="auth-form" @submit.prevent="submit" @keydown.enter.prevent="submit">
      <label>
        Email
        <input v-model="email" type="email" autocomplete="email" required />
      </label>
      <label>
        Password
        <input
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          autocomplete="new-password"
          minlength="8"
          required
          @keyup="updateCapsLockState"
          @keydown="updateCapsLockState"
        />
      </label>
      <label class="auth-checkbox">
        <input v-model="showPassword" type="checkbox" />
        Show password
      </label>
      <p v-if="capsLockOn" class="auth-error">Caps Lock appears to be on.</p>
      <button type="submit" :disabled="loading">
        {{ loading ? "Creating account..." : "Create Account" }}
      </button>
      <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="auth-success">{{ successMessage }}</p>
    </form>
    <p class="auth-switch">
      Already registered?
      <RouterLink to="/signin">Sign in</RouterLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { apiFetch } from "../lib/api";

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const router = useRouter();
const showPassword = ref(false);
const capsLockOn = ref(false);

async function submit(): Promise<void> {
  if (loading.value) {
    return;
  }

  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  let timeoutId: number | undefined;

  try {
    const controller = new AbortController();
    timeoutId = window.setTimeout(() => controller.abort(), 15000);
    const response = await apiFetch("/users", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Version": "v1"
      },
      signal: controller.signal,
      body: JSON.stringify({
        email: email.value.trim(),
        password: password.value
      })
    }, { redirectOn401: false });

    if (!response.ok) {
      if (response.status === 409) {
        errorMessage.value = "An account with this email already exists. Please sign in instead, or use a different email.";
      } else {
        errorMessage.value = "Sign up failed. Please review your input.";
      }
      return;
    }

    await router.push({
      path: "/signin",
      query: { email: email.value.trim(), created: "1" }
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      errorMessage.value = "Request timed out. Please make sure the API is running and try again.";
    } else {
      errorMessage.value = "Unable to reach the API. Please try again.";
    }
  } finally {
    if (timeoutId !== undefined) {
      window.clearTimeout(timeoutId);
    }
    loading.value = false;
  }
}

function updateCapsLockState(event: KeyboardEvent): void {
  capsLockOn.value = event.getModifierState("CapsLock");
}
</script>
