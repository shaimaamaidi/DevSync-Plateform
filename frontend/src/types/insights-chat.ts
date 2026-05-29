export interface InsightsChatAttachment {
  type:
    | "task_search_result"
    | "task_confirm_single"
    | "task_select_multiple"
    | "task_synthesis_result"
    | "project_status_result"
    | "weekly_summary_result"
    | "commit_trace_result"
    | "rephrase_prompt";
  data?: any;
}

export interface InsightsChatMessageType {
  id: number;
  ts: Date;
  role: "user" | "agent";
  content: string;
  _streaming?: boolean;
  attachment?: InsightsChatAttachment;
  isRejection?: boolean;
  onRetry?: () => void;
}