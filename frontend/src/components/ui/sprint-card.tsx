import { useState } from "react";
import { ChevronDown, ChevronRight, Clock, ListTodo, Target, Zap } from "lucide-react";
import type { UiSprint, UiSprintStory, UiTaskEstimate } from "@/types/backlog";

const SPRINT_PALETTE = [
  { bg: "bg-blue-50", fg: "text-blue-600", border: "border-blue-200", fgHex: "#2563eb" },
  { bg: "bg-purple-50", fg: "text-purple-700", border: "border-purple-200", fgHex: "#7e22ce" },
  { bg: "bg-cyan-50", fg: "text-cyan-700", border: "border-cyan-200", fgHex: "#0e7490" },
  { bg: "bg-teal-50", fg: "text-teal-700", border: "border-teal-200", fgHex: "#0f766e" },
  { bg: "bg-indigo-50", fg: "text-indigo-700", border: "border-indigo-200", fgHex: "#4338ca" },
];

interface SprintCardProps {
  data: UiSprint[];
}

export function SprintCard({ data }: SprintCardProps) {
  const [openSprints, setOpenSprints]  = useState<Record<string, boolean>>({});
  const [openStories, setOpenStories]  = useState<Record<string, boolean>>({});

  const totalHours = data.reduce((a, s) => a + s.totalEstimatedHours, 0);
  const totalStories = data.reduce((a, s) => a + s.stories.length, 0);

  return (
    <div className="flex flex-col gap-2.5 mt-2.5">

      <div className="flex gap-2">
        {[
          { Icon: Zap,      val: data.length,     label: "Sprints",    color: "#7c3aed", iconBg: "#7c3aed18" },
          { Icon: ListTodo, val: totalStories,     label: "Stories",    color: "#16a34a", iconBg: "#16a34a18" },
          { Icon: Clock,    val: `${totalHours}h`, label: "Total est.", color: "#d97706", iconBg: "#d9770618" },
        ].map(({ Icon, val, label, color, iconBg }) => (
          <div key={label} className="flex-1 flex items-center gap-1.5 sm:gap-2.5 px-2 sm:px-3 py-2 sm:py-2.5 bg-slate-50 rounded-xl border border-slate-100 min-w-0">
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: iconBg }}>
              <Icon size={13} strokeWidth={1.8} style={{ color }} />
            </div>
            <div className="min-w-0">
              <p className="m-0 text-[17px] sm:text-[19px] font-extrabold text-slate-900 leading-none tracking-tight">{val}</p>
              <p className="m-0 mt-0.5 text-[9px] sm:text-[10px] text-slate-400 uppercase tracking-[0.06em] font-semibold truncate">{label}</p>
            </div>
          </div>
        ))}
      </div>

      {data.map((sprint, idx) => {
        const color  = SPRINT_PALETTE[idx % SPRINT_PALETTE.length];
        const isOpen = !!openSprints[sprint.id];

        return (
          <div key={sprint.id} className="rounded-xl border border-slate-200 bg-white overflow-hidden">

            <button
              onClick={() => setOpenSprints((s) => ({ ...s, [sprint.id]: !s[sprint.id] }))}
              className="w-full flex items-center gap-2 sm:gap-[11px] px-3 sm:px-[15px] py-[13px] bg-transparent border-none cursor-pointer text-left"
            >
              <div className={`w-[30px] h-[30px] sm:w-[34px] sm:h-[34px] rounded-[9px] flex items-center justify-center shrink-0 ${color.bg} border-[1.5px] ${color.border}`}>
                <span className={`text-[8px] sm:text-[9px] font-extrabold tracking-wide ${color.fg}`}>{sprint.id}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="m-0 text-[13px] sm:text-[14px] font-semibold text-slate-900 truncate">{sprint.name}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <Target size={10} strokeWidth={2} className="text-slate-400 shrink-0" />
                  <p className="m-0 text-[10px] sm:text-[11px] text-slate-400 truncate">{sprint.goal}</p>
                </div>
              </div>
              <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
                <span className="hidden xs:inline-flex text-[10px] sm:text-[10.5px] text-slate-400 px-[7px] sm:px-[9px] py-[2px] bg-slate-50 rounded-full border border-slate-100 font-medium">
                  {sprint.totalEstimatedHours}h
                </span>
                <span className="text-[10px] sm:text-[10.5px] text-slate-400 px-[7px] sm:px-[9px] py-[2px] bg-slate-50 rounded-full border border-slate-100 font-medium">
                  {sprint.stories.length} stories
                </span>
                {isOpen
                  ? <ChevronDown  size={14} strokeWidth={2} className="text-slate-400" />
                  : <ChevronRight size={14} strokeWidth={2} className="text-slate-400" />}
              </div>
            </button>

            {isOpen && (
              <div className="border-t border-slate-100 px-2.5 sm:px-3.5 pt-2.5 pb-3.5 flex flex-col gap-1.5">
                {sprint.stories.map((story: UiSprintStory) => {
                  const isStoryOpen = !!openStories[story.id];
                  return (
                    <div key={story.id} className="rounded-[10px] border border-slate-100 bg-slate-50/70 overflow-hidden">
                      <button
                        onClick={() => setOpenStories((s) => ({ ...s, [story.id]: !s[story.id] }))}
                        className="w-full flex items-start gap-2 px-2.5 sm:px-3 py-2.5 bg-transparent border-none cursor-pointer text-left"
                      >
                        <div className={`w-[24px] h-[24px] sm:w-[26px] sm:h-[26px] rounded-[7px] flex items-center justify-center shrink-0 mt-px ${color.bg} border ${color.border}`}>
                          <span className={`text-[7px] font-extrabold ${color.fg}`}>{story.id.split(".")[1]}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="m-0 text-[12px] sm:text-[13px] font-medium text-slate-900 truncate">{story.title}</p>
                          <p className="m-0 mt-0.5 text-[10px] sm:text-[11px] text-slate-400 leading-relaxed line-clamp-2">
                            As a <em className={`not-italic font-semibold ${color.fg}`}>{story.as_a}</em>
                            {" — "}{story.i_want}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
                          <span className="hidden xs:inline-flex text-[10px] sm:text-[10.5px] text-slate-400 px-[7px] sm:px-[9px] py-[2px] bg-slate-50 rounded-full border border-slate-100 font-medium">
                            {story.tasks.length} tasks
                          </span>
                          {isStoryOpen
                            ? <ChevronDown  size={13} strokeWidth={2} className="text-slate-400" />
                            : <ChevronRight size={13} strokeWidth={2} className="text-slate-400" />}
                        </div>
                      </button>

                      {isStoryOpen && (
                        <div className="border-t border-slate-100 px-2.5 sm:px-3 pt-2.5 pb-3">
                          <p className="m-0 mb-[9px] text-[10.5px] sm:text-[11.5px] text-slate-400 leading-relaxed">
                            <span className="font-semibold text-slate-500">So that</span> {story.so_that}
                          </p>
                          <div className="flex flex-col gap-[5px]">
                            {story.tasks.map((task: UiTaskEstimate) => (
                              <div key={task.id} className="flex items-center gap-2 px-2 sm:px-2.5 py-[7px] bg-white rounded-lg border border-slate-100">
                                <ListTodo size={12} strokeWidth={1.8} className="text-slate-400 shrink-0" />
                                <div className="flex-1 min-w-0">
                                  <p className="m-0 text-[12px] text-gray-700 truncate">{task.title}</p>
                                  {task.description && (
                                    <p className="m-0 text-[11px] text-slate-400 truncate">{task.description}</p>
                                  )}
                                </div>
                                <div className="flex items-center gap-1 px-1.5 sm:px-2 py-0.5 bg-slate-50 rounded-full border border-slate-100 text-[10px] sm:text-[11px] text-slate-500 font-medium shrink-0">
                                  <Clock size={10} strokeWidth={2} />
                                  <span>{task.estimatedHours}h</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}