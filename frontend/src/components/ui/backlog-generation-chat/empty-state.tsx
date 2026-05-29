import { Lightbulb } from "lucide-react";

export function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6 py-12 text-center">
      <div className="w-[60px] h-[60px] rounded-2xl bg-slate-900 flex items-center justify-center shadow-[0_8px_24px_rgba(15,23,42,0.2)]">
        <Lightbulb size={27} strokeWidth={1.5} className="text-white" />
      </div>

      <div>
        <p className="text-[18px] font-bold text-slate-900 tracking-tight m-0 mb-1.5">
          Start your backlog generation
        </p>
        <p className="text-[13px] text-slate-400 m-0 max-w-[600px] leading-[1.7]">
          Provide a product idea, system description, or internal tool
          requirement. The agent will analyze it and generate structured market
          insights and an agile backlog.
        </p>
      </div>
    </div>
  );
}