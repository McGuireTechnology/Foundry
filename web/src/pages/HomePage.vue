<template>
  <section class="dashboard-shell">
    <header class="dashboard-header">
      <div>
        <h2 class="dashboard-title">Dashboard</h2>
        <p class="dashboard-subtitle" v-if="currentUserEmail">Signed in as {{ currentUserEmail }}</p>
      </div>
      <button class="ui-button ui-button-outline" type="button" @click="reloadAll" :disabled="isLoading">
        Refresh
      </button>
    </header>

    <p v-if="errorMessage" class="ui-alert ui-alert-error">{{ errorMessage }}</p>

    <div class="dashboard-grid">
      <section class="ui-card">
        <header class="ui-card-header">
          <h3>Applications</h3>
          <p>Create and manage low-code applications.</p>
        </header>
        <form class="ui-form" @submit.prevent="submitApplication">
          <label class="ui-field">
            <span>Name</span>
            <input v-model.trim="applicationForm.name" required maxlength="120" placeholder="CRM" />
          </label>
          <label class="ui-field">
            <span>Slug</span>
            <input v-model.trim="applicationForm.slug" required maxlength="120" placeholder="crm" />
          </label>
          <label class="ui-field">
            <span>Description</span>
            <textarea v-model.trim="applicationForm.description" rows="3" maxlength="500" placeholder="Customer workflows and pipeline data." />
          </label>
          <button class="ui-button" type="submit" :disabled="isCreatingApplication">
            {{ isCreatingApplication ? "Creating..." : "Create Application" }}
          </button>
        </form>

        <div class="ui-table-wrap">
          <table class="ui-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Slug</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td>{{ app.name }}</td>
                <td><code>{{ app.slug }}</code></td>
                <td>{{ app.is_active ? "Active" : "Inactive" }}</td>
              </tr>
              <tr v-if="applications.length === 0">
                <td colspan="3" class="ui-empty">No applications yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="ui-card">
        <header class="ui-card-header">
          <h3>Databases</h3>
          <p>Create internal Vortex databases for app data domains.</p>
        </header>
        <form class="ui-form" @submit.prevent="submitDatabase">
          <label class="ui-field">
            <span>Name</span>
            <input v-model.trim="databaseForm.name" required maxlength="120" placeholder="Customer Data" />
          </label>
          <label class="ui-field">
            <span>Slug</span>
            <input v-model.trim="databaseForm.slug" required maxlength="120" placeholder="customer-data" />
          </label>
          <button class="ui-button" type="submit" :disabled="isCreatingDatabase">
            {{ isCreatingDatabase ? "Creating..." : "Create Database" }}
          </button>
        </form>

        <div class="ui-table-wrap">
          <table class="ui-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Slug</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="db in databases" :key="db.id">
                <td>{{ db.name }}</td>
                <td><code>{{ db.slug }}</code></td>
              </tr>
              <tr v-if="databases.length === 0">
                <td colspan="2" class="ui-empty">No internal databases yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

import { getCurrentUserEmail } from "../lib/auth";
import {
  createApplication,
  createDatabase,
  listApplications,
  listDatabases,
  type Application,
  type Database
} from "../lib/dashboardApi";

const currentUserEmail = computed(() => getCurrentUserEmail());
const applications = ref<Application[]>([]);
const databases = ref<Database[]>([]);
const isLoading = ref(false);
const isCreatingApplication = ref(false);
const isCreatingDatabase = ref(false);
const errorMessage = ref("");

const applicationForm = reactive({
  name: "",
  slug: "",
  description: ""
});

const databaseForm = reactive({
  name: "",
  slug: ""
});

async function reloadAll(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const [appList, dbList] = await Promise.all([listApplications(), listDatabases()]);
    applications.value = appList;
    databases.value = dbList;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Failed to load dashboard data.";
  } finally {
    isLoading.value = false;
  }
}

async function submitApplication(): Promise<void> {
  isCreatingApplication.value = true;
  errorMessage.value = "";
  try {
    await createApplication({
      name: applicationForm.name,
      slug: applicationForm.slug,
      description: applicationForm.description || undefined
    });
    applicationForm.name = "";
    applicationForm.slug = "";
    applicationForm.description = "";
    await reloadAll();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Failed to create application.";
  } finally {
    isCreatingApplication.value = false;
  }
}

async function submitDatabase(): Promise<void> {
  isCreatingDatabase.value = true;
  errorMessage.value = "";
  try {
    await createDatabase({
      name: databaseForm.name,
      slug: databaseForm.slug
    });
    databaseForm.name = "";
    databaseForm.slug = "";
    await reloadAll();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Failed to create database.";
  } finally {
    isCreatingDatabase.value = false;
  }
}

onMounted(async () => {
  await reloadAll();
});
</script>
