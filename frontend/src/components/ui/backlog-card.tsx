import { useEffect, useState } from "react";
import {
  ChevronDown, ChevronRight, Layers, BookOpen, ListTodo,
  Plus, Check, X, Trash2, FlagTriangleRight,
} from "lucide-react";
import type { UiEpic, UiStory, UiTask } from "@/types/backlog";
import { areBacklogsEqual, cloneBacklog, normalizeBacklog, uiToBacklog } from "@/utils/backlog.mapper";
import { EditableText } from "./editable-text";

const EPIC_PALETTE = [
  { bg: "bg-blue-50", fg: "text-blue-600", border: "border-blue-200", dot: "#3b82f6", fgHex: "#2563eb" },
  { bg: "bg-green-50", fg: "text-green-700", border: "border-green-200", dot: "#22c55e", fgHex: "#15803d" },
  { bg: "bg-amber-50", fg: "text-amber-700", border: "border-amber-200", dot: "#f59e0b", fgHex: "#b45309" },
  { bg: "bg-purple-50", fg: "text-purple-700", border: "border-purple-200", dot: "#a855f7", fgHex: "#7e22ce" },
  { bg: "bg-rose-50", fg: "text-rose-700", border: "border-rose-200", dot: "#f43f5e", fgHex: "#be123c" },
];

interface BacklogCardProps {
  data: UiEpic[];
  readonly editable: boolean;
  onSubmit: (epics: UiEpic[]) => void;
}

type BacklogErrors = {
  epic: Partial<Record<"title" | "description", string>>;
  story: Partial<Record<"title" | "as_a" | "i_want" | "so_that", string>>;
  task: Partial<Record<"title" | "description", string>>;
};

type DeleteErrors = Record<string, string>;

export function BacklogCard({ data, editable, onSubmit }: BacklogCardProps) {
  const [epics, setEpics] = useState<UiEpic[]>(() => normalizeBacklog(data));
  const [openEpics,   setOpenEpics]   = useState<Record<string, boolean>>({});
  const [openStories, setOpenStories] = useState<Record<string, boolean>>({});
  const [done, setDone] = useState(false);

  const [addingStory, setAddingStory] = useState<string | null>(null);
  const [addingTask,  setAddingTask]  = useState<string | null>(null);
  const [addingEpic,  setAddingEpic]  = useState(false);

  const [newStory, setNewStory] = useState({ title: "", as_a: "user", i_want: "", so_that: "" });
  const [newTask,  setNewTask]  = useState({ title: "", description: "" });
  const [newEpic,  setNewEpic]  = useState({ title: "", description: "" });

  const [errors, setErrors] = useState<BacklogErrors>({ epic: {}, story: {}, task: {} });
  const [deleteErrors, setDeleteErrors] = useState<DeleteErrors>({});

  useEffect(() => {
    setEpics(normalizeBacklog(data));
    setDone(false);
  }, [data]);

  const isEdit = editable && !done;

  const totalStories = epics.reduce((a, e) => a + e.stories.length, 0);
  const totalTasks   = epics.reduce((a, e) => a + e.stories.reduce((b, s) => b + s.tasks.length, 0), 0);
  const hasChanges   = !areBacklogsEqual(uiToBacklog(epics), uiToBacklog(data));

  const showDeleteError = (id: string, msg: string) => {
    setDeleteErrors((prev) => ({ ...prev, [id]: msg }));
    setTimeout(() => {
      setDeleteErrors((prev) => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
    }, 3500);
  };

  const getNextId = (items: { id: string }[], prefix: string) => {
    const numbers = items.map((i) => parseInt(i.id.replace(/\D/g, "") || "0", 10));
    const max = numbers.length ? Math.max(...numbers) : 0;
    return `${prefix}${max + 1}`;
  };

  const updateEpic = (eid: string, patch: Partial<UiEpic>) =>
    setEpics((e) => e.map((ep) => ep.id === eid ? { ...ep, ...patch } : ep));

  const updateStory = (eid: string, sid: string, patch: Partial<UiStory>) =>
    setEpics((e) => e.map((ep) => ep.id === eid
      ? { ...ep, stories: ep.stories.map((s) => s.id === sid ? { ...s, ...patch } : s) }
      : ep));

  const updateTask = (eid: string, sid: string, tid: string, patch: Partial<UiTask>) =>
    setEpics((e) => e.map((ep) => ep.id === eid ? {
      ...ep,
      stories: ep.stories.map((s) => s.id === sid
        ? { ...s, tasks: s.tasks.map((t) => t.id === tid ? { ...t, ...patch } : t) }
        : s),
    } : ep));

  const removeEpic = (eid: string) => {
    if (epics.length === 1) {
      showDeleteError(eid, "Impossible de supprimer le dernier epic. Le backlog ne peut pas être vide.");
      return;
    }
    setEpics((e) => e.filter((ep) => ep.id !== eid));
  };

  const removeStory = (eid: string, sid: string) => {
    const epic = epics.find((ep) => ep.id === eid);
    if (epic && epic.stories.length === 1) {
      showDeleteError(sid, "Impossible de supprimer la dernière user story. Un epic ne peut pas être vide.");
      return;
    }
    setEpics((e) => e.map((ep) => ep.id === eid
      ? { ...ep, stories: ep.stories.filter((s) => s.id !== sid) }
      : ep));
  };

  const removeTask = (eid: string, sid: string, tid: string) => {
    const story = epics.find((ep) => ep.id === eid)?.stories.find((s) => s.id === sid);
    if (story && story.tasks.length === 1) {
      showDeleteError(tid, "Impossible de supprimer la dernière tâche. Une story ne peut pas être vide.");
      return;
    }
    setEpics((e) => e.map((ep) => ep.id === eid ? {
      ...ep,
      stories: ep.stories.map((s) => s.id === sid
        ? { ...s, tasks: s.tasks.filter((t) => t.id !== tid) }
        : s),
    } : ep));
  };

  const addEpic = () => {
    const newErrors: BacklogErrors["epic"] = {};
    if (!newEpic.title.trim())       
      newErrors.title = "Title is required.";
    if (!newEpic.description.trim()) 
      newErrors.description = "Description is required.";
    if (Object.keys(newErrors).length > 0) {
      setErrors((prev) => ({ ...prev, epic: newErrors }));
      return;
    }
    setEpics((e) => [...e, { id: getNextId(epics, "E"), title: newEpic.title.trim(), description: newEpic.description.trim(), stories: [] }]);
    setNewEpic({ title: "", description: "" });
    setAddingEpic(false);
  };

  const addStory = (eid: string) => {
    const newErrors: BacklogErrors["story"] = {};
    if (!newStory.title.trim())   
      newErrors.title   = "Title is required.";
    if (!newStory.as_a.trim())    
      newErrors.as_a    = "As a is required";
    if (!newStory.i_want.trim())  
      newErrors.i_want  = "I want is required";
    if (!newStory.so_that.trim()) 
      newErrors.so_that = "So that is required";
    if (Object.keys(newErrors).length > 0) {
      setErrors((prev) => ({ ...prev, story: newErrors }));
      return;
    }
    const newId = getNextId(epics.flatMap((e) => e.stories), "US");
    setEpics((e) => e.map((ep) => ep.id === eid
      ? { ...ep, stories: [...ep.stories, { id: newId, tasks: [], ...newStory, title: newStory.title.trim() }] }
      : ep));
    setNewStory({ title: "", as_a: "user", i_want: "", so_that: "" });
    setAddingStory(null);
  };

  const addTask = (eid: string, sid: string) => {
    const newErrors: BacklogErrors["task"] = {};
    if (!newTask.title.trim())       
      newErrors.title = "Title is required.";
    if (!newTask.description.trim()) 
      newErrors.description = "Description is required.";
    if (Object.keys(newErrors).length > 0) {
      setErrors((prev) => ({ ...prev, task: newErrors }));
      return;
    }
    const newId = getNextId(epics.flatMap((e) => e.stories.flatMap((s) => s.tasks)), "T");
    setEpics((e) => e.map((ep) => ep.id === eid ? {
      ...ep,
      stories: ep.stories.map((s) => s.id === sid
        ? { ...s, tasks: [...s.tasks, { id: newId, title: newTask.title.trim(), description: newTask.description.trim() }] }
        : s),
    } : ep));
    setNewTask({ title: "", description: "" });
    setAddingTask(null);
  };

  const cancelEpicEdit = () => {
    setAddingEpic(false);
    setNewEpic({ title: "", description: "" });
    setErrors((prev) => ({ ...prev, epic: {} }));
  };

  const cancelStoryEdit = () => {
    setAddingStory(null);
    setNewStory({ title: "", as_a: "user", i_want: "", so_that: "" });
    setErrors((prev) => ({ ...prev, story: {} }));
  };

  const cancelTaskEdit = () => {
    setAddingTask(null);
    setNewTask({ title: "", description: "" });
    setErrors((prev) => ({ ...prev, task: {} }));
  };

  const handleSubmit = () => {
    setDone(true);
    onSubmit(cloneBacklog(normalizeBacklog(epics)));
  };

  const miniInput = "text-[12px] px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white outline-none focus:border-slate-400 placeholder:text-slate-300 font-[inherit] w-full";

  return (
    <div className="flex flex-col gap-2.5 mt-2.5">

      <div className="flex gap-2">
        {[
          { Icon: Layers,   val: epics.length, label: "Epics",   color: "#3b82f6", iconBg: "#3b82f618" },
          { Icon: BookOpen, val: totalStories,  label: "Stories", color: "#16a34a", iconBg: "#16a34a18" },
          { Icon: ListTodo, val: totalTasks,    label: "Tasks",   color: "#d97706", iconBg: "#d9770618" },
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

      {epics.map((epic, idx) => {
        const color  = EPIC_PALETTE[idx % EPIC_PALETTE.length];
        const isOpen = !!openEpics[epic.id];
        return (
          <div key={epic.id} className="flex flex-col">
            <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">

              <div className="flex items-center px-3 sm:px-[15px] py-[13px] gap-2 sm:gap-2.5">
                <button
                  onClick={() => setOpenEpics((s) => ({ ...s, [epic.id]: !s[epic.id] }))}
                  className="flex items-center gap-2 sm:gap-[11px] flex-1 bg-transparent border-none cursor-pointer text-left p-0 min-w-0"
                >
                  <div className={`w-[30px] h-[30px] sm:w-[34px] sm:h-[34px] rounded-[9px] flex items-center justify-center shrink-0 ${color.bg} border-[1.5px] ${color.border}`}>
                    <span className={`text-[8px] sm:text-[9px] font-extrabold tracking-wide ${color.fg}`}>{epic.id}</span>
                  </div>
                  <div className="flex-1 min-w-0" onClick={(e) => isEdit && e.stopPropagation()}>
                    <EditableText
                      value={epic.title}
                      onChange={(v) => updateEpic(epic.id, { title: v })}
                      editable={isEdit}
                      className="text-[13px] sm:text-[14px] font-semibold text-slate-900 block"
                      placeholder="Epic title"
                    />
                    <EditableText
                      value={epic.description}
                      onChange={(v) => updateEpic(epic.id, { description: v })}
                      editable={isEdit}
                      className="text-[10px] sm:text-[11px] text-slate-400 block truncate mt-0.5"
                      placeholder="Short description"
                    />
                  </div>
                  <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
                    <span className="text-[10px] sm:text-[10.5px] text-slate-400 px-[7px] sm:px-[9px] py-[2px] bg-slate-50 rounded-full border border-slate-100 font-medium hidden xs:inline-flex">
                      {epic.stories.length} stories
                    </span>
                    {isOpen
                      ? <ChevronDown  size={14} strokeWidth={2} className="text-slate-400" />
                      : <ChevronRight size={14} strokeWidth={2} className="text-slate-400" />}
                  </div>
                </button>
                {isEdit && (
                  <button
                    onClick={() => removeEpic(epic.id)}
                    className="w-7 h-7 flex items-center justify-center rounded-lg text-red-400 hover:bg-red-50 hover:text-red-500 transition-colors border-none bg-transparent cursor-pointer shrink-0"
                  >
                    <Trash2 size={13} strokeWidth={1.8} />
                  </button>
                )}
              </div>

              {deleteErrors[epic.id] && (
                <div className="text-destructive text-xs px-3 sm:px-[15px] pb-2.5 -mt-1">
                  {deleteErrors[epic.id]}
                </div>
              )}

              {isOpen && (
                <div className="border-t border-slate-100 px-2.5 sm:px-3.5 pt-2.5 pb-3.5 flex flex-col gap-1.5">
                  {epic.stories.map((story: UiStory) => {
                    const isStoryOpen = !!openStories[story.id];
                    return (
                      <div key={story.id} className="flex flex-col">
                        <div className="rounded-[10px] border border-slate-100 bg-slate-50/70 overflow-hidden">

                          <div className="flex items-start px-2.5 sm:px-3 py-2.5 gap-2">
                            <button
                              onClick={() => setOpenStories((s) => ({ ...s, [story.id]: !s[story.id] }))}
                              className="flex items-start gap-2 flex-1 bg-transparent border-none cursor-pointer text-left p-0 min-w-0"
                            >
                              <div className={`w-[24px] h-[24px] sm:w-[26px] sm:h-[26px] rounded-[7px] flex items-center justify-center shrink-0 mt-px ${color.bg} border ${color.border}`}>
                                <span className={`text-[7px] font-extrabold ${color.fg}`}>{story.id}</span>
                              </div>
                              <div className="flex-1 min-w-0" onClick={(e) => isEdit && e.stopPropagation()}>
                                <EditableText
                                  value={story.title}
                                  onChange={(v) => updateStory(epic.id, story.id, { title: v })}
                                  editable={isEdit}
                                  className="text-[12px] sm:text-[13px] font-medium text-slate-900 block"
                                  placeholder="Story title"
                                />
                                <p className="m-0 mt-0.5 text-[10px] sm:text-[11px] text-slate-400 leading-relaxed">
                                  As a{" "}
                                  <EditableText
                                    value={story.as_a}
                                    onChange={(v) => updateStory(epic.id, story.id, { as_a: v })}
                                    editable={isEdit}
                                    className={`not-italic font-semibold ${color.fg}`}
                                    placeholder="role"
                                  />
                                  {" — "}
                                  <EditableText
                                    value={story.i_want}
                                    onChange={(v) => updateStory(epic.id, story.id, { i_want: v })}
                                    editable={isEdit}
                                    className="text-slate-400"
                                    placeholder="I want…"
                                  />
                                </p>
                              </div>
                              <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
                                <span className="text-[10px] sm:text-[10.5px] text-slate-400 px-[7px] sm:px-[9px] py-[2px] bg-slate-50 rounded-full border border-slate-100 font-medium hidden xs:inline-flex">
                                  {story.tasks.length} tasks
                                </span>
                                {isStoryOpen
                                  ? <ChevronDown  size={13} strokeWidth={2} className="text-slate-400" />
                                  : <ChevronRight size={13} strokeWidth={2} className="text-slate-400" />}
                              </div>
                            </button>
                            {isEdit && (
                              <button
                                onClick={() => removeStory(epic.id, story.id)}
                                className="w-6 h-6 flex items-center justify-center rounded-md text-red-400 hover:bg-red-50 hover:text-red-500 transition-colors border-none bg-transparent cursor-pointer shrink-0"
                              >
                                <Trash2 size={12} strokeWidth={1.8} />
                              </button>
                            )}
                          </div>

                          {deleteErrors[story.id] && (
                            <div className="text-destructive text-xs px-3 pb-2 -mt-1">
                              {deleteErrors[story.id]}
                            </div>
                          )}

                          {isStoryOpen && (
                            <div className="border-t border-slate-100 px-2.5 sm:px-3 pt-2.5 pb-3">
                              <p className="m-0 mb-[9px] text-[10.5px] sm:text-[11.5px] text-slate-400 leading-relaxed">
                                <span className="font-semibold text-slate-500">So that</span>{" "}
                                <EditableText
                                  value={story.so_that}
                                  onChange={(v) => updateStory(epic.id, story.id, { so_that: v })}
                                  editable={isEdit}
                                  className="text-slate-400"
                                  placeholder="so that…"
                                />
                              </p>

                              <div className="flex flex-col gap-[5px] mb-1">
                                {story.tasks.map((task: UiTask) => (
                                  <div key={task.id} className="flex flex-col">
                                    <div className="flex items-center gap-2 px-2 sm:px-2.5 py-[7px] bg-white rounded-lg border border-slate-100">
                                      <ListTodo size={12} strokeWidth={1.8} className="text-slate-400 shrink-0" />
                                      <div className="flex flex-col flex-1 min-w-0">
                                        <EditableText
                                          value={task.title}
                                          onChange={(v) => updateTask(epic.id, story.id, task.id, { title: v })}
                                          editable={isEdit}
                                          className="text-[12px] font-semibold text-slate-800"
                                          placeholder="Task title"
                                        />
                                        <EditableText
                                          value={task.description}
                                          onChange={(v) => updateTask(epic.id, story.id, task.id, { description: v })}
                                          editable={isEdit}
                                          className="text-[11px] text-slate-500 mt-[2px]"
                                          placeholder="Task description"
                                        />
                                      </div>
                                      {isEdit && (
                                        <button
                                          onClick={() => removeTask(epic.id, story.id, task.id)}
                                          className="w-5 h-5 flex items-center justify-center rounded-md text-red-400 hover:bg-red-50 hover:text-red-500 transition-colors border-none bg-transparent cursor-pointer shrink-0"
                                        >
                                          <X size={11} strokeWidth={2.5} />
                                        </button>
                                      )}
                                    </div>

                                    {deleteErrors[task.id] && (
                                      <div className="text-destructive text-xs mt-1 px-1">
                                        {deleteErrors[task.id]}
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>

                              {isEdit && (
                                addingTask === story.id ? (
                                  <div className="flex flex-col gap-1.5 mt-2">
                                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-1.5">
                                      <input
                                        value={newTask.title}
                                        onChange={(e) => setNewTask((s) => ({ ...s, title: e.target.value }))}
                                        placeholder="Task title…"
                                        className={miniInput}
                                      />
                                      <input
                                        value={newTask.description}
                                        onChange={(e) => setNewTask((s) => ({ ...s, description: e.target.value }))}
                                        placeholder="Task description…"
                                        className={miniInput}
                                      />
                                      <div className="flex gap-1.5 sm:contents">
                                        <button
                                          onClick={() => addTask(epic.id, story.id)}
                                          className="flex-1 sm:flex-none w-auto sm:w-7 h-7 flex items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border-none cursor-pointer transition-colors"
                                        >
                                          <Check size={13} />
                                        </button>
                                        <button
                                          onClick={cancelTaskEdit}
                                          className="flex-1 sm:flex-none w-auto sm:w-7 h-7 flex items-center justify-center rounded-lg bg-slate-100 text-slate-500 hover:bg-slate-200 border-none cursor-pointer transition-colors"
                                        >
                                          <X size={13} />
                                        </button>
                                      </div>
                                    </div>
                                    {errors.task.title && (
                                      <div className="text-destructive text-xs mt-1 px-1">{errors.task.title}</div>
                                    )}
                                    {errors.task.description && (
                                      <div className="text-destructive text-xs mt-1 px-1">{errors.task.description}</div>
                                    )}
                                  </div>
                                ) : (
                                  <button
                                    onClick={() => setAddingTask(story.id)}
                                    className="mt-1.5 w-full flex items-center justify-center gap-1.5 py-1.5 rounded-lg border border-dashed border-slate-200 text-[11px] text-slate-400 hover:border-slate-300 hover:text-slate-500 bg-transparent cursor-pointer transition-colors"
                                  >
                                    <Plus size={11} strokeWidth={2.5} /> Add task
                                  </button>
                                )
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}

                  {isEdit && (
                    addingStory === epic.id ? (
                      <div className="flex flex-col gap-1.5 p-3 rounded-xl border border-dashed border-slate-200 bg-white mt-1">
                        <input
                          value={newStory.title}
                          onChange={(e) => setNewStory((s) => ({ ...s, title: e.target.value }))}
                          placeholder="Story title…"
                          className={miniInput}
                        />
                        {errors.story.title && (
                          <div className="text-destructive text-xs mt-1 px-1">{errors.story.title}</div>
                        )}
                        <div className="flex flex-col sm:flex-row gap-1.5">
                          {[
                            { field: "as_a",    ph: "As a…"    },
                            { field: "i_want",  ph: "I want…"  },
                            { field: "so_that", ph: "So that…" },
                          ].map(({ field, ph }) => (
                            <input
                              key={field}
                              value={(newStory as any)[field]}
                              onChange={(e) => setNewStory((s) => ({ ...s, [field]: e.target.value }))}
                              placeholder={ph}
                              className={miniInput}
                            />
                          ))}
                        </div>
                        {(errors.story.as_a || errors.story.i_want || errors.story.so_that) && (
                          <div className="text-destructive text-xs mt-1 px-1">
                            {[errors.story.as_a, errors.story.i_want, errors.story.so_that]
                              .filter(Boolean)
                              .join(" • ")}
                          </div>
                        )}
                        <div className="flex gap-1.5 justify-end">
                          <button
                            onClick={() => addStory(epic.id)}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 text-[12px] font-semibold hover:bg-emerald-100 border-none cursor-pointer transition-colors"
                          >
                            <Check size={13} /> Add story
                          </button>
                          <button
                            onClick={cancelStoryEdit}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-500 text-[12px] font-semibold hover:bg-slate-200 border-none cursor-pointer transition-colors"
                          >
                            <X size={13} /> Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={() => setAddingStory(epic.id)}
                        className="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl border border-dashed border-slate-200 text-[12px] text-slate-400 hover:border-slate-300 hover:text-slate-500 bg-transparent cursor-pointer transition-colors mt-1"
                      >
                        <Plus size={12} strokeWidth={2.5} /> Add user story
                      </button>
                    )
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}

      {isEdit && (
        addingEpic ? (
          <div className="flex flex-col gap-1.5 p-3 rounded-xl border border-dashed border-slate-200 bg-white">
            <input
              value={newEpic.title}
              onChange={(e) => setNewEpic((s) => ({ ...s, title: e.target.value }))}
              placeholder="Epic title…"
              className={miniInput}
            />
            {errors.epic.title && (
              <div className="text-destructive text-xs mt-1 px-1">{errors.epic.title}</div>
            )}
            <input
              value={newEpic.description}
              onChange={(e) => setNewEpic((s) => ({ ...s, description: e.target.value }))}
              placeholder="Short description…"
              className={miniInput}
            />
            {errors.epic.description && (
              <div className="text-destructive text-xs mt-1 px-1">{errors.epic.description}</div>
            )}
            <div className="flex gap-1.5 justify-end">
              <button
                onClick={addEpic}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 text-[12px] font-semibold hover:bg-emerald-100 border-none cursor-pointer transition-colors"
              >
                <Check size={13} /> Add epic
              </button>
              <button
                onClick={cancelEpicEdit}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-500 text-[12px] font-semibold hover:bg-slate-200 border-none cursor-pointer transition-colors"
              >
                <X size={13} /> Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setAddingEpic(true)}
            className="w-full flex items-center justify-center gap-1.5 py-2.5 rounded-xl border border-dashed border-slate-200 text-[13px] text-slate-400 hover:border-slate-300 hover:text-slate-500 bg-transparent cursor-pointer transition-colors px-3.5"
          >
            <Plus size={14} strokeWidth={2.5} /> Add epic
          </button>
        )
      )}

      {isEdit && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between px-3 sm:px-4 py-3 rounded-xl bg-slate-50 border border-slate-100 mt-1 gap-3">
          <p className="m-0 text-[12px] text-slate-500 leading-relaxed">
            {hasChanges
              ? "Submit your modifications to validate and generate the sprints."
              : "No modifications detected. Run generation to create sprints from the current backlog."}
          </p>
          <button
            onClick={handleSubmit}
            className="flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-slate-900 text-white text-[12px] font-bold hover:bg-slate-700 border-none cursor-pointer transition-colors shrink-0 sm:ml-4 w-full sm:w-auto"
          >
            <FlagTriangleRight size={15} strokeWidth={2} />
            {hasChanges ? "Validate & Generate Sprints" : "Run Sprint Generation"}
          </button>
        </div>
      )}
    </div>
  );
}