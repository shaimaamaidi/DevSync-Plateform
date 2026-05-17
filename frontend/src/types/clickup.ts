import type { ClickUpList } from "@/api/api";

export interface TaskDraft {
  name: string;
  description: string;
  status: string;
  priority: string;
  assignees: string[];
};

export interface LocationWithTasksOption {
  label: string;
  listId: string;
  list: ClickUpList;
};

export interface LocationWithMetadataOption {
  listId: string;
  label: string;
  statuses: string[];
  priorities: string[];
};
