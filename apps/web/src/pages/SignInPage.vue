<template>
  <section class="panel auth-panel">
    <div class="auth-wordmark">
      <img class="brand-logo" src="/logo.svg" alt="Foundry logo" />
      <div class="brand-copy">
        <h1>Foundry</h1>
        <p>by McGuire Technology, LLC</p>
      </div>
    </div>
    <h2>Sign In</h2>
    <p>Use your Foundry account credentials to continue.</p>
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
          autocomplete="current-password"
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
      <label class="auth-checkbox">
        <input v-model="rememberMe" type="checkbox" />
        Remember me
      </label>
      <button type="submit" :disabled="loading">
        {{ loading ? "Signing in..." : "Sign In" }}
      </button>
      <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="auth-success">{{ successMessage }}</p>
    </form>
    <p class="auth-switch">
      Need an account?
      <RouterLink to="/signup">Create one</RouterLink>
    </p>
    <p class="auth-switch">
      Forgot your password?
      <RouterLink to="/forgot-password">Reset it</RouterLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import { apiFetch } from "../lib/api";
import { setAuthBanner } from "../lib/authBanner";
import {
  clearRememberedEmail,
  getRememberedEmail,
  rememberEmail,
  setCurrentUserEmail,
  storeTokens
} from "../lib/auth";

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const rememberMe = ref(false);
const showPassword = ref(false);
const capsLockOn = ref(false);
const route = useRoute();
const router = useRouter();

onMounted(() => {
  const rememberedEmail = getRememberedEmail();
  if (rememberedEmail) {
    email.value = rememberedEmail;
    rememberMe.value = true;
  }

  const routeEmail = route.query.email;
  if (typeof routeEmail === "string" && routeEmail.trim().length > 0) {
    email.value = routeEmail.trim();
  }

  if (route.query.created === "1") {
    setAuthBanner("Account created. You can now sign in.");
  } else if (route.query.expired === "1") {
    setAuthBanner("Your session expired. Please sign in again.");
  }
});

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
    const response = await apiFetch("/auth/token", {
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
      if (response.status === 429) {
        const payload = (await response.json()) as { detail?: string };
        errorMessage.value = payload.detail ?? "Too many failed attempts. Please wait and try again.";
      } else {
        errorMessage.value = "Sign in failed. Check your email and password.";
      }
      return;
    }

    const tokens = (await response.json()) as { access_token: string; refresh_token: string };
    storeTokens(tokens);
    setCurrentUserEmail(email.value.trim());
    if (rememberMe.value) {
      rememberEmail(email.value.trim());
    } else {
      clearRememberedEmail();
    }
    const next = typeof route.query.next === "string" ? route.query.next : "";
    const nextPath = next.startsWith("/") ? next : "/dashboard";
    await router.push(nextPath);
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
