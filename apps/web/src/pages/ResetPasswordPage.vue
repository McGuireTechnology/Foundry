<template>
  <section class="panel auth-panel">
    <div class="auth-wordmark">
      <img class="brand-logo" src="/logo.svg" alt="Foundry logo" />
      <div class="brand-copy">
        <h1>Foundry</h1>
        <p>by McGuire Technology, LLC</p>
      </div>
    </div>
    <h2>Reset Password</h2>
    <p>Enter your reset token and choose a new password.</p>
    <form class="auth-form" @submit.prevent="submit" @keydown.enter.prevent="submit">
      <label>
        Reset Token
        <input v-model="token" type="text" autocomplete="off" required />
      </label>
      <label>
        New Password
        <input
          v-model="newPassword"
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
        {{ loading ? "Resetting..." : "Reset Password" }}
      </button>
      <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="auth-success">{{ successMessage }}</p>
    </form>
    <p class="auth-switch">
      <RouterLink to="/signin">Back to Sign In</RouterLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import { apiFetch } from "../lib/api";
import { setAuthBanner } from "../lib/authBanner";

const token = ref("");
const newPassword = ref("");
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const showPassword = ref(false);
const capsLockOn = ref(false);
const route = useRoute();
const router = useRouter();

onMounted(() => {
  const queryToken = route.query.token;
  if (typeof queryToken === "string" && queryToken.trim().length > 0) {
    token.value = queryToken.trim();
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
    const response = await apiFetch(
      "/auth/reset-password",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Version": "v1"
        },
        signal: controller.signal,
        body: JSON.stringify({
          token: token.value.trim(),
          new_password: newPassword.value
        })
      },
      { redirectOn401: false }
    );

    if (!response.ok) {
      errorMessage.value = "Unable to reset password. Verify your token and try again.";
      return;
    }

    setAuthBanner("Password reset complete. You can now sign in.");
    await router.push("/signin");
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
