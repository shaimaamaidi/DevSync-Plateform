import { useState } from "react";

export function TaskSelectMultiple({ data, onAction }: { data: any; onAction?: (a: string, p?: any) => void }) {
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