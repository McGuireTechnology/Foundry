export type FoundryId = string;

export interface Organization {
  id: FoundryId;
  name: string;
  createdAt: string;
}

export interface Project {
  id: FoundryId;
  organizationId: FoundryId;
  name: string;
  createdAt: string;
}