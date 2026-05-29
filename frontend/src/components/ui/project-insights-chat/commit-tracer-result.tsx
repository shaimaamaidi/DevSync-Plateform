export function CommitTraceResult({ data }: { data: any }) {
  if (!data) 
    return null;
  
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