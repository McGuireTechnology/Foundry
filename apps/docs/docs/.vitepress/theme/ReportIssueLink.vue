<template>
  <p class="docs-report-link">
    <a :href="issueUrl" target="_blank" rel="noreferrer">Report an issue with this page</a>
  </p>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vitepress";

const route = useRoute();

const issueUrl = computed(() => {
  const pagePath = route.path || "/";
  const title = `Docs: ${pagePath}`;
  const body = [`Page: ${pagePath}`, "", "Issue:", ""].join("\n");
  const params = new URLSearchParams({
    labels: "documentation",
    title,
    body
  });
  return `https://github.com/McGuireTechnology/Foundry/issues/new?${params.toString()}`;
});
</script>
