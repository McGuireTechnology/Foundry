import { apiFetch } from "./api";

export type Application = {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type Database = {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
};

type ApiError = {
  detail?: string;
};

async function parseError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as ApiError;
    return payload.detail ?? `Request failed with status ${response.status}`;
  } catch {
    return `Request failed with status ${response.status}`;
  }
}

export async function listApplications(): Promise<Application[]> {
  const response = await apiFetch("/applications");
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return (await response.json()) as Application[];
}

export async function createApplication(payload: {
  name: string;
  slug: string;
  description?: string;
  is_active?: boolean;
}): Promise<Application> {
  const response = await apiFetch("/applications", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return (await response.json()) as Application;
}

export async function listDatabases(): Promise<Database[]> {
  const response = await apiFetch("/databases");
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return (await response.json()) as Database[];
}

export async function createDatabase(payload: {
  name: string;
  slug: string;
}): Promise<Database> {
  const response = await apiFetch("/databases", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return (await response.json()) as Database;
}
