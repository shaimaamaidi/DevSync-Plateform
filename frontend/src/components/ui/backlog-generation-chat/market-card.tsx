import { useEffect, useState } from "react";
import {
  TrendingUp,
  Swords,
  AlertTriangle,
  Sparkles,
  StickyNote,
  FlagTriangleRight
} from "lucide-react";

import type { MarketSummary } from "@/types/backlog";
import { EditableList } from "@/components/ui/task-detail-controls/editable-list";
import {
  areMarketSummariesEqual,
  cloneMarketSummary,
  normalizeMarketSummary,
} from "@/lib/backlog.mapper";

type Accent = "info" | "danger" | "success" | "amber" | null;
type SectionKey = keyof MarketSummary;

interface Section {
  key: SectionKey;
  label: string;
  type: "text" | "list";
  Icon: any;
  accent: Accent;
  iconBg: string;
  iconColor: string;
}

const ACCENT_STYLES: Record<
  Exclude<Accent, null>,
  { bg: string; color: string; border: string }
> = {
  danger: { bg: "#fef2f2", color: "#ef4444", border: "rgba(239,68,68,0.3)" },
  success: { bg: "#f0fdf4", color: "#16a34a", border: "rgba(34,197,94,0.3)" },
  amber: { bg: "#fffbeb", color: "#d97706", border: "rgba(245,158,11,0.3)" },
  info: { bg: "#eff6ff", color: "#3b82f6", border: "rgba(59,130,246,0.3)" },
};

const SECTIONS: readonly Section[] = [
  {
    key: "market_trends",
    label: "Market Trends",
    type: "text",
    Icon: TrendingUp,
    accent: null,
    iconBg: "#f0f9ff",
    iconColor: "#0369a1",
  },
  {
    key: "competitor_features",
    label: "Competitor Features",
    type: "list",
    Icon: Swords,
    accent: "info",
    iconBg: "#eff6ff",
    iconColor: "#3b82f6",
  },
  {
    key: "user_pain_points",
    label: "User Pain Points",
    type: "list",
    Icon: AlertTriangle,
    accent: "danger",
    iconBg: "#fef2f2",
    iconColor: "#ef4444",
  },
  {
    key: "best_practices",
    label: "Best Practices",
    type: "list",
    Icon: Sparkles,
    accent: "success",
    iconBg: "#f0fdf4",
    iconColor: "#16a34a",
  },
  {
    key: "enrichment_notes",
    label: "Enrichment Notes",
    type: "text",
    Icon: StickyNote,
    accent: "amber",
    iconBg: "#fffbeb",
    iconColor: "#d97706",
  },
];

const TEXT_REQUIRED_KEYS = new Set<SectionKey>(["market_trends", "enrichment_notes"]);

interface MarketCardProps {
  data: MarketSummary;
  readonly editable: boolean;
  onSubmit: (summary: MarketSummary) => void;
}

export function MarketCard({ data, editable, onSubmit }: MarketCardProps) {
  const [draft, setDraft] = useState<MarketSummary>(() => normalizeMarketSummary(data));
  const [done, setDone] = useState(false);
  const [textErrors, setTextErrors] = useState<Partial<Record<SectionKey, string>>>({});

  const normalizedData = normalizeMarketSummary(data);
  const hasChanges = !areMarketSummariesEqual(draft, normalizedData);

  useEffect(() => {
    setDraft(normalizeMarketSummary(data));
    setDone(false);
    setTextErrors({});
  }, [data]);

  const handleUpdate = <K extends SectionKey>(key: K, value: MarketSummary[K]) => {
    setDraft((prev) => ({ ...prev, [key]: value }));
  };

  const handleTextBlur = (key: SectionKey) => {
    if (!TEXT_REQUIRED_KEYS.has(key)) return;
    const current = (draft[key] as string) ?? "";
    if (!current.trim()) {
      const previous = (normalizedData[key] as string) ?? "";
      setDraft((prev) => ({ ...prev, [key]: previous }));
      setTextErrors((prev) => ({ ...prev, [key]: "This field cannot be empty." }));
    } else {
      setTextErrors((prev) => ({ ...prev, [key]: undefined }));
    }
  };

  const handleTextChange = (key: SectionKey, value: string) => {
    handleUpdate(key, value as MarketSummary[SectionKey]);
    if (textErrors[key]) {
      setTextErrors((prev) => ({ ...prev, [key]: undefined }));
    }
  };

  const getList = (key: SectionKey): string[] =>
    Array.isArray(draft[key]) ? (draft[key] as string[]) : [];

  const handleSubmit = () => {
    const errors: Partial<Record<SectionKey, string>> = {};
    TEXT_REQUIRED_KEYS.forEach((key) => {
      const val = (draft[key] as string) ?? "";
      if (!val.trim()) errors[key] = "This field cannot be empty.";
    });
    if (Object.keys(errors).length > 0) {
      setTextErrors(errors);
      return;
    }
    setDone(true);
    onSubmit(cloneMarketSummary(normalizeMarketSummary(draft)));
  };

  return (
    <div className="flex flex-col gap-2 mt-2.5">
      {SECTIONS.map(({ key, label, type, Icon, accent, iconBg, iconColor }) => {
        const isEdit = editable && !done;
        const style  = accent ? ACCENT_STYLES[accent] : null;

        return (
          <div
            key={key}
            className="bg-white border border-slate-100 rounded-xl px-3 sm:px-[15px] py-3 sm:py-[13px] shadow-sm"
          >
            <div className="flex items-center gap-[9px] mb-2.5">
              <div
                className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                style={{ background: iconBg }}
              >
                <Icon size={13} strokeWidth={1.8} style={{ color: iconColor }} />
              </div>
              <span className="text-[11px] font-bold uppercase tracking-[0.08em] text-slate-400">
                {label}
              </span>
            </div>

            {type === "text" ? (
              <>
                {isEdit ? (
                  <textarea
                    value={(draft[key] as string) ?? ""}
                    onChange={(e) => handleTextChange(key, e.target.value)}
                    onBlur={() => handleTextBlur(key)}
                    rows={2}
                    className="w-full resize-y border border-[1.5px] border-slate-200 rounded-lg py-[9px] px-[11px] text-[13px] leading-relaxed bg-slate-50 text-slate-900 font-[inherit] box-border outline-none transition-colors focus:border-slate-400"
                  />
                ) : (
                  <p className="m-0 text-[13px] leading-[1.7] text-gray-700">
                    {(draft[key] as string) ?? ""}
                  </p>
                )}
                {isEdit && textErrors[key] && (
                  <div className="text-destructive text-xs mt-1 px-1">
                    {textErrors[key]}
                  </div>
                )}
              </>
            ) : (
              <>
                {isEdit ? (
                  <EditableList
                    items={getList(key)}
                    onChange={(items) => handleUpdate(key, items as MarketSummary[SectionKey])}
                    accent={accent ?? undefined}
                  />
                ) : (
                  <div className="flex flex-col gap-[5px]">
                    {getList(key).map((item, i) => (
                      <div
                        key={i}
                        className="text-[12.5px] py-[7px] px-3 rounded-lg leading-relaxed"
                        style={{
                          background: style?.bg ?? "#eff6ff",
                          color: style?.color ?? "#3b82f6",
                          border: `1px solid ${style?.border ?? "rgba(59,130,246,0.3)"}`,
                        }}
                      >
                        {item}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        );
      })}

      {editable && !done && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between px-3 sm:px-4 py-3 rounded-xl bg-slate-50 border border-slate-100 mt-1 gap-3">
          <p className="m-0 text-[12px] text-slate-500 leading-relaxed">
            {hasChanges
              ? "Submit your changes to validate and generate the backlog."
              : "No changes detected. Launch the generation to create the backlog with the current data."}
          </p>
          <button
            onClick={handleSubmit}
            className="flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-slate-900 text-white text-[12px] font-bold hover:bg-slate-700 border-none cursor-pointer transition-colors shrink-0 sm:ml-4 w-full sm:w-auto"
          >
            <FlagTriangleRight size={15} strokeWidth={2} />
            {hasChanges ? "Validate & Generate Backlog" : "Launch Generation"}
          </button>
        </div>
      )}
    </div>
  );
}