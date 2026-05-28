export type AssigneeDialogStateForGeneration =
  | { open: false }
  | { open: true; type: 'names'; items: string[] }
  | { open: true; type: 'mails'; items: string[] };

export type AssigneeDialogStateForConsultation =
  | { open: false }
  | { open: true; type: 'mails'; items: string[] };