import { BotMessageSquare, CircleUser, RefreshCcw, AlertTriangle } from "lucide-react";
import { useState } from "react";

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

interface Props {
  message: InsightsChatMessageType;
  streamingText?: string;
  onAttachmentAction?: (action: string, payload?: any) => void;
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-[5px] py-[3px]">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-[7px] h-[7px] rounded-full bg-slate-300 animate-bounce"
          style={{ animationDelay: `${i * 0.18}s` }}
        />
      ))}
    </div>
  );
}

function MessageBubble({ isUser, isRejection, content }: { isUser: boolean; isRejection?: boolean; content: string }) {
  return (
    <div
      className={[
        "px-3.5 py-2.5 text-[13px] leading-[1.7] rounded-xl",
        "bg-slate-50 text-slate-800 border border-slate-100",
        isUser ? "rounded-tr-[3px]" : "rounded-tl-[3px]",
        isRejection ? "bg-red-500/[0.06] border-red-500/[0.18] text-red-700" : "",
      ].join(" ")}
    >
      {isRejection && (
        <div className="flex items-center gap-1.5 mb-2 pb-2 border-b border-red-500/[0.18]">
          <AlertTriangle size={12} strokeWidth={2} className="text-red-500" />
          <span className="text-[10px] font-bold text-red-500 uppercase tracking-[0.08em]">Notice</span>
        </div>
      )}
      {content}
    </div>
  );
}


function TaskConfirmSingle({ data, onAction }: { data: any; onAction?: (a: string, p?: any) => void }) {
  const task = data?.task;
  const [confirmed, setConfirmed] = useState<boolean | null>(null);

  if (!task) return null;

  const handleYes = () => {
    setConfirmed(true);
    onAction?.("confirm_yes", task);
  };

  const handleNo = () => {
    setConfirmed(false);
    onAction?.("confirm_no");
  };

  return (
    <div className="mt-2 rounded-xl border border-slate-200 bg-white p-3 space-y-3">
      <div className="text-[12px] font-semibold text-slate-700 uppercase tracking-wide">Found Task</div>
      <div className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2 space-y-0.5">
        <p className="text-[13px] font-semibold text-slate-800">{task.name}</p>
        {task.description && <p className="text-[12px] text-slate-500">{task.description}</p>}
        <div className="flex gap-2 mt-1 flex-wrap">
          {task.status && <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 text-slate-600">{task.status}</span>}
          {task.priority && <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">{task.priority}</span>}
        </div>
      </div>
      {confirmed === null && (
        <>
          <p className="text-[12px] text-slate-500">Is this the task you are referring to?</p>
          <div className="flex gap-2">
            <button
              onClick={handleYes}
              className="flex-1 py-1.5 rounded-lg bg-slate-900 text-white text-[12px] font-medium hover:bg-slate-700 transition"
            >
              Yes, analyze it
            </button>
            <button
              onClick={handleNo}
              className="flex-1 py-1.5 rounded-lg border border-slate-200 text-slate-600 text-[12px] font-medium hover:bg-slate-50 transition"
            >
              No, rephrase
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function TaskSelectMultiple({ data, onAction }: { data: any; onAction?: (a: string, p?: any) => void }) {
  const tasks: any[] = data?.tasks ?? [];
  const [selected, setSelected] = useState<string | null>(null);

  const handleSelect = (task: any) => {
    setSelected(task.id);
    onAction?.("select_task", task);
  };

  const handleNone = () => {
    setSelected("none");
    onAction?.("confirm_no");
  };

  return (
    <div className="mt-2 rounded-xl border border-slate-200 bg-white p-3 space-y-2">
      <div className="text-[12px] font-semibold text-slate-700 uppercase tracking-wide">Multiple matches found</div>
      {selected === null && (
        <p className="text-[12px] text-slate-500">Select the task you are referring to, or choose "None of these".</p>
      )}
      <div className="space-y-2">
        {tasks.map((task) => {
          if (selected !== null && selected !== task.id) return null;
          return (
            <button
              key={task.id}
              onClick={() => selected === null && handleSelect(task)}
              disabled={selected !== null}
              className={`w-full text-left rounded-lg bg-slate-50 border px-3 py-2 transition space-y-0.5 ${
                selected === task.id
                  ? "border-slate-400 bg-white cursor-default"
                  : "border-slate-100 hover:border-slate-300 hover:bg-white cursor-pointer"
              }`}
            >
              <p className="text-[13px] font-semibold text-slate-800">{task.name}</p>
              {task.description && <p className="text-[11px] text-slate-500 line-clamp-1">{task.description}</p>}
              <div className="flex gap-2 mt-1 flex-wrap">
                {task.status && <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 text-slate-600">{task.status}</span>}
              </div>
            </button>
          );
        })}
        {selected === null && (
          <button
            onClick={handleNone}
            className="w-full py-1.5 rounded-lg border border-dashed border-slate-300 text-slate-500 text-[12px] font-medium hover:bg-slate-50 transition"
          >
            None of these — rephrase
          </button>
        )}
      </div>
    </div>
  );
}

function TaskSynthesisResult({ data }: { data: any }) {
  if (!data) return null;
  const { is_completed, confidence, summary, evidence } = data;
  return (
    <div className="mt-2 rounded-xl border border-slate-200 bg-white p-3 space-y-3">
      <div className="flex items-center gap-2">
        <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full ${is_completed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
          {is_completed ? "Completed" : "Not Completed"}
        </span>
        <span className="text-[11px] text-slate-400">Confidence: {confidence}</span>
      </div>
      <p className="text-[13px] text-slate-700 leading-relaxed">{summary}</p>
      {evidence?.length > 0 && (
        <div className="space-y-1">
          <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">Evidence</p>
          <ul className="space-y-1">
            {evidence.map((e: string, i: number) => (
              <li key={i} className="text-[12px] text-slate-600 flex gap-2">
                <span className="text-slate-300 shrink-0">—</span>
                {e}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ProjectStatusResult({ data }: { data: any }) {
  if (!data) return null;
  const { message, total_tasks, tasks_summary, last_commit, last_deployment, stale_tasks, unverified_done_tasks, overdue_todo_tasks } = data;
  return (
    <div className="mt-2 rounded-xl border border-slate-200 bg-white p-4 space-y-4">

      <p className="text-[13px] text-slate-700 leading-relaxed">{message}</p>

      <div className="rounded-lg border border-slate-200 overflow-hidden">
        <div className="px-3 py-2 bg-slate-50 border-b border-slate-200">
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide">Overview</p>
        </div>
        <div className="divide-y divide-slate-100">
          <div className="flex items-center justify-between px-3 py-2.5">
            <span className="text-[12px] text-slate-500">Total tasks</span>
            <span className="text-[13px] font-bold text-slate-800">{total_tasks}</span>
          </div>
          {last_commit && (
            <div className="flex items-center justify-between px-3 py-2.5">
              <span className="text-[12px] text-slate-500">Last commit</span>
              <span className="text-[12px] font-semibold text-slate-700">{last_commit}</span>
            </div>
          )}
          {last_deployment && (
            <div className="flex items-center justify-between px-3 py-2.5">
              <span className="text-[12px] text-slate-500">Last deployment</span>
              <span className="text-[12px] font-semibold text-slate-700">{last_deployment}</span>
            </div>
          )}
        </div>
      </div>

      {tasks_summary?.length > 0 && (
        <div className="rounded-lg border border-slate-200 overflow-hidden">
          <div className="px-3 py-2 bg-slate-50 border-b border-slate-200">
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide">Tasks by status</p>
          </div>
          <table className="w-full">
            <tbody className="divide-y divide-slate-100">
              {tasks_summary.map((s: any, i: number) => (
                <tr key={i}>
                  <td className="px-3 py-2.5 text-[12px] text-slate-600">{s.status}</td>
                  <td className="px-3 py-2.5 text-right">
                    <span className="text-[12px] font-semibold text-slate-800">{s.percentage}%</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {stale_tasks?.length > 0 && (
        <div className="rounded-lg border border-amber-200 overflow-hidden">
          <div className="px-3 py-2 bg-amber-50 border-b border-amber-200">
            <p className="text-[10px] font-semibold text-amber-700 uppercase tracking-wide">⚠️ Stale tasks ({stale_tasks.length})</p>
          </div>
          <div className="divide-y divide-amber-100">
            {stale_tasks.map((t: any) => (
              <div key={t.task_id} className="px-3 py-2.5 flex items-start justify-between gap-3">
                <span className="text-[12px] text-amber-900 font-medium">{t.task_name}</span>
                <span className="text-[11px] text-amber-500 shrink-0">{t.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {unverified_done_tasks?.length > 0 && (
        <div className="rounded-lg border border-red-200 overflow-hidden">
          <div className="px-3 py-2 bg-red-50 border-b border-red-200">
            <p className="text-[10px] font-semibold text-red-700 uppercase tracking-wide">⚠️ Done without commit ({unverified_done_tasks.length})</p>
          </div>
          <div className="divide-y divide-red-100">
            {unverified_done_tasks.map((t: any) => (
              <div key={t.task_id} className="px-3 py-2.5">
                <span className="text-[12px] text-red-900 font-medium">{t.task_name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {overdue_todo_tasks?.length > 0 && (
        <div className="rounded-lg border border-orange-200 overflow-hidden">
          <div className="px-3 py-2 bg-orange-50 border-b border-orange-200">
            <p className="text-[10px] font-semibold text-orange-700 uppercase tracking-wide">⚠️ Overdue todo ({overdue_todo_tasks.length})</p>
          </div>
          <div className="divide-y divide-orange-100">
            {overdue_todo_tasks.map((t: any) => (
              <div key={t.task_id} className="px-3 py-2.5 flex items-start justify-between gap-3">
                <span className="text-[12px] text-orange-900 font-medium">{t.task_name}</span>
                <span className="text-[11px] text-orange-500 shrink-0">{t.days_waiting}d waiting</span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}

function WeeklySummaryResult({ data }: { data: any }) {
  if (!data) return null;
  const { message, created_tasks, in_progress_tasks, done_tasks, commits_summary, deployments_summary, last_7_days_commits, last_7_days_deployments } = data;
  return (
    <div className="mt-2 rounded-xl border border-slate-200 bg-white p-3 space-y-3">
      <p className="text-[13px] text-slate-700 leading-relaxed">{message}</p>
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: "Created", tasks: created_tasks, color: "bg-blue-50 border-blue-100 text-blue-700" },
          { label: "In Progress", tasks: in_progress_tasks, color: "bg-amber-50 border-amber-100 text-amber-700" },
          { label: "Done", tasks: done_tasks, color: "bg-green-50 border-green-100 text-green-700" },
        ].map(({ label, tasks, color }) => (
          <div key={label} className={`rounded-lg border px-2 py-2 text-center ${color}`}>
            <p className="text-[18px] font-bold">{tasks?.length ?? 0}</p>
            <p className="text-[10px] font-medium uppercase tracking-wide">{label}</p>
          </div>
        ))}
      </div>
      {commits_summary && (
        <div className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2">
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide mb-1">Commits this week ({last_7_days_commits?.length ?? 0})</p>
          <p className="text-[12px] text-slate-700">{commits_summary}</p>
        </div>
      )}
      {deployments_summary && (
        <div className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2">
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide mb-1">Deployments this week ({last_7_days_deployments?.length ?? 0})</p>
          <p className="text-[12px] text-slate-700">{deployments_summary}</p>
        </div>
      )}
    </div>
  );
}

function CommitTraceResult({ data }: { data: any }) {
  if (!data) return null;
  const { message, task } = data;
  return (
    <div className="mt-2 rounded-xl border border-slate-200 bg-white p-3 space-y-3">
      <p className="text-[13px] text-slate-700 leading-relaxed">{message}</p>
      {task && (
        <div className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2 space-y-1">
          <p className="text-[13px] font-semibold text-slate-800">{task.name}</p>
          {task.description && <p className="text-[12px] text-slate-500">{task.description}</p>}
          <div className="flex gap-2 flex-wrap mt-1">
            {task.status && <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 text-slate-600">{task.status}</span>}
            {task.priority && <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">{task.priority}</span>}
          </div>
        </div>
      )}
    </div>
  );
}

function AttachmentRenderer({ attachment, onAction }: { attachment: InsightsChatAttachment; onAction?: (a: string, p?: any) => void }) {
  switch (attachment.type) {
    case "task_confirm_single": return <TaskConfirmSingle data={attachment.data} onAction={onAction} />;
    case "task_select_multiple": return <TaskSelectMultiple data={attachment.data} onAction={onAction} />;
    case "task_synthesis_result": return <TaskSynthesisResult data={attachment.data} />;
    case "project_status_result": return <ProjectStatusResult data={attachment.data} />;
    case "weekly_summary_result": return <WeeklySummaryResult data={attachment.data} />;
    case "commit_trace_result": return <CommitTraceResult data={attachment.data} />;
    default: return null;
  }
}


export function InsightsChatMessage({ message, streamingText = "", onAttachmentAction }: Props) {
  const isUser = message.role === "user";
  const isStreaming = message._streaming;
  const hasCard = message.attachment;

  return (
    <div className={`flex flex-col gap-1 animate-[msg-in_0.22s_ease-out_both] ${isUser ? "items-end" : "items-start"}`}>
      <div className={`flex items-start gap-2 sm:gap-2.5 ${isUser ? "flex-row-reverse" : ""} ${hasCard ? "max-w-full w-full" : "max-w-[90%] sm:max-w-[76%]"}`}>
        <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-[9px] flex-shrink-0 flex items-center justify-center bg-slate-900">
          {isUser
            ? <CircleUser size={13} strokeWidth={2} className="text-white" />
            : <BotMessageSquare size={13} strokeWidth={2} className="text-white" />
          }
        </div>
        <div className="flex-1 min-w-0">
          {isStreaming ? (
            <div className="px-3 sm:px-3.5 py-2.5 text-[13px] leading-[1.7] rounded-xl bg-slate-50 text-slate-800 border border-slate-100 rounded-tl-[3px]">
              {streamingText || <TypingIndicator />}
            </div>
          ) : (
            <MessageBubble isUser={isUser} isRejection={message.isRejection} content={message.content} />
          )}
          {!isStreaming && message.onRetry && (
            <div className="mt-2">
              <button
                onClick={message.onRetry}
                className="flex items-center gap-1.5 px-2.5 py-1.5 text-[12px] font-medium text-slate-500 hover:text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg border border-slate-200 transition-colors cursor-pointer"
              >
                <RefreshCcw size={12} strokeWidth={2} />
                Try again
              </button>
            </div>
          )}
          {!isStreaming && message.attachment && (
            <AttachmentRenderer attachment={message.attachment} onAction={onAttachmentAction} />
          )}
        </div>
      </div>
      <p className={`text-[10px] text-slate-200 m-0 ${isUser ? "pr-[36px] sm:pr-[42px]" : "pl-[36px] sm:pl-[42px]"}`}>
        {isUser ? "You" : "Agent"} · {message.ts?.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
      </p>
    </div>
  );
}