export function TaskSynthesisResult({ data }: { data: any }) {
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