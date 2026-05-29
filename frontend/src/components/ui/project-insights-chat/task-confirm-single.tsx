import { useState } from "react";

export function TaskConfirmSingle({ data, onAction }: { data: any; onAction?: (a: string, p?: any) => void }) {
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
