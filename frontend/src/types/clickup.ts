import type { ClickUpListWithEstimation, GeneratedTaskFromBacklog, GeneratedTaskFromSummary, VerifiedTaskFromBacklog, VerifiedTaskFromSummary } from "@/api/api";


export type TaskGenerationDTO = GeneratedTaskFromSummary | GeneratedTaskFromBacklog;

export type TaskVerificationDTO = VerifiedTaskFromSummary | VerifiedTaskFromBacklog;


export interface TaskDraft {
  name: string;
  description: string;
  status: string;
  priority: string;
  assignees: string[];
  estimation: number | null;
};

export interface LocationWithTasksOption {
  label: string;
  listId: string;
  list: ClickUpListWithEstimation;
};

export interface LocationWithMetadataOption {
  listId: string;
  label: string;
  statuses: string[];
  priorities: string[];
};

export const DEFAULT_PRIORITIES = ['urgent', 'high', 'normal', 'low'];

