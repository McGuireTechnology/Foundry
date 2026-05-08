<template>
  <section class="panel">
    <h2 v-if="currentUserEmail">Welcome, {{ currentUserEmail }}!</h2>
    <h3 v-if="currentUserEmail">Project Bootstrap Complete</h3>
    <h2 v-else>Project Bootstrap Complete</h2>
    <p>This workspace now includes API, web builder, and docs scaffolding.</p>
    <ul>
      <li>Define data models</li>
      <li>Build page schema and renderer</li>
      <li>Add workflow/actions engine</li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

import { getCurrentUserEmail } from "../lib/auth";

const currentUserEmail = computed(() => getCurrentUserEmail());
</script>
