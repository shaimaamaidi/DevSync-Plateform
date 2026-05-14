import type { ClickUpList, FolderWithLists, FolderWithListsMetadata } from "@/api/api";

export const FOLDERLESS_MARKER = '__folderless__';

export interface TaskDraft {
  name: string;
  description: string;
  status: string;
  priority: string;
  assignees: string[];
};

export const PRIORITY_CONFIG: Record<string, { badge: string; dot: string }> = {
  urgent: { badge: 'bg-red-50 text-red-700 border-red-100', dot: 'bg-red-500' },
  high: { badge: 'bg-amber-50 text-amber-700 border-amber-100', dot: 'bg-amber-500' },
  medium: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  normal: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  low: { badge: 'bg-muted text-muted-foreground border-border', dot: 'bg-muted-foreground' },
};

export function priorityConfig(p: string) {
  return PRIORITY_CONFIG[p?.toLowerCase()] ?? PRIORITY_CONFIG.normal;
};

export interface LocationWithTasksOption {
  label: string;      // "FolderName / ListName" or "ListName" for folderless
  listId: string;
  list: ClickUpList;
};

export function buildLocationWithTasksOptions(folders: FolderWithLists[]): LocationWithTasksOption[] {
  const options: LocationWithTasksOption[] = [];
  for (const folder of folders) {
    for (const list of folder.lists ?? []) {
      const isFolderless =
        folder.name === FOLDERLESS_MARKER || folder.id === list.id;
      const label = isFolderless
        ? list.name
        : `${folder.name} / ${list.name}`;
      options.push({ label, listId: list.id, list });
    }
  }
  return options;
};

export interface LocationWithMetadataOption {
  listId: string;
  label: string;       // "FolderName / ListName" or "ListName"
  statuses: string[];
  priorities: string[];
};

export function buildLocationWithMetadataOptions(structure: FolderWithListsMetadata[]): LocationWithMetadataOption[] {
  const opts: LocationWithMetadataOption[] = [];
  for (const folder of structure) {
    const isFolderless =
      folder.name === FOLDERLESS_MARKER ||
      folder.id === (folder.lists?.[0]?.id ?? null);
    for (const list of folder.lists ?? []) {
      opts.push({
        listId: list.id,
        label: isFolderless
          ? list.name
          : `${folder.name} / ${list.name}`,
        statuses: list.statuses ?? [],
        priorities: list.priorities ?? [],
      });
    }
  }
  return opts;
};