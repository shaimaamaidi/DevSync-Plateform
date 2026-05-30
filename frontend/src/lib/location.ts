import type { FolderWithListsAndEstimation, FolderWithListsMetadata } from "@/api/api";
import {  type LocationWithMetadataOption, type LocationWithTasksOption } from "../types/clickup";

export const FOLDERLESS_MARKER = '__folderless__';

export function buildLocationWithTasksOptions(folders: FolderWithListsAndEstimation[]): LocationWithTasksOption[] {
  const options: LocationWithTasksOption[] = [];
  for (const folder of folders) {
    for (const list of folder.lists ?? []) {
      const isFolderless = folder.name === FOLDERLESS_MARKER || folder.id === list.id;
      const label = isFolderless ? list.name : `${folder.name} / ${list.name}`;
      options.push({ label, listId: list.id, list });
    }
  }
  return options;
}

export function buildLocationWithMetadataOptions(structure: FolderWithListsMetadata[]): LocationWithMetadataOption[] {
  const opts: LocationWithMetadataOption[] = [];
  for (const folder of structure) {
    const isFolderless = folder.name === FOLDERLESS_MARKER || folder.id === (folder.lists?.[0]?.id ?? null);
    for (const list of folder.lists ?? []) {
      opts.push({
        listId: list.id,
        label: isFolderless ? list.name : `${folder.name} / ${list.name}`,
        statuses: list.statuses ?? [],
        priorities: list.priorities ?? [],
      });
    }
  }
  return opts;
}