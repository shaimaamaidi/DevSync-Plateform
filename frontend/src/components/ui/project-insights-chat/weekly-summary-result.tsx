export function WeeklySummaryResult({ data }: { data: any }) {
  if (!data) 
    return null;
  
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