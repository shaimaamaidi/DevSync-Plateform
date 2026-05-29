export function ProjectStatusResult({ data }: { data: any }) {
  if (!data) 
    return null;
  
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