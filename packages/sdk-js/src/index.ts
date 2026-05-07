import type { Organization } from "@foundry/shared-types";

export class FoundryClient {
  constructor(private readonly baseUrl: string) {}

  async health(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/api/v1/health`);
    return response.json();
  }

  async listOrganizations(): Promise<Organization[]> {
    throw new Error("Not implemented");
  }
}