<template>
  <section class="panel auth-panel">
    <div class="auth-wordmark">
      <img class="brand-logo" src="/logo.svg" alt="Foundry logo" />
      <div class="brand-copy">
        <h1>Foundry</h1>
        <p>by McGuire Technology, LLC</p>
      </div>
    </div>
    <h2>Forgot Password</h2>
    <p>Enter your email and we will send reset instructions if an account exists.</p>
    <form class="auth-form" @submit.prevent="submit" @keydown.enter.prevent="submit">
      <label>
        Email
        <input v-model="email" type="email" autocomplete="email" required />
      </label>
      <button type="submit" :disabled="loading">
        {{ loading ? "Submitting..." : "Send Reset Instructions" }}
      </button>
      <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="auth-success">{{ successMessage }}</p>
      <p v-if="resetLink" class="auth-success">
        Dev reset link:
        <RouterLink :to="resetLink">Open Reset Password</RouterLink>
      </p>
    </form>
    <p class="auth-switch">
      Remembered your password?
      <RouterLink to="/signin">Back to Sign In</RouterLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";

import { apiFetch } from "../lib/api";

const email = ref("");
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const resetLink = ref("");

async function submit(): Promise<void> {
  if (loading.value) {
    return;
  }

  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  resetLink.value = "";
  let timeoutId: number | undefined;

  try {
    const controller = new AbortController();
    timeoutId = window.setTimeout(() => controller.abort(), 15000);
    const response = await apiFetch("/auth/forgot-password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Version": "v1"
      },
      signal: controller.signal,
      body: JSON.stringify({
        email: email.value.trim()
      })
    }, { redirectOn401: false });

    if (!response.ok) {
      errorMessage.value = "Unable to process your request right now. Please try again.";
      return;
    }

    const payload = (await response.json()) as { message: string; reset_token?: string | null };
    successMessage.value = payload.message;
    if (payload.reset_token) {
      resetLink.value = `/reset-password?token=${encodeURIComponent(payload.reset_token)}`;
    }
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
</script>
