import type { RefinedMarketIntelligence, BacklogPayload } from "@/types/backlog";


export function isRefinedMarketIntelligence(v: unknown): v is RefinedMarketIntelligence {
  return Boolean(
    v && typeof v === "object" &&
    "refined_market_trends"       in (v as object) &&
    "refined_competitor_features" in (v as object) &&
    "refined_user_pain_points"    in (v as object) &&
    "refined_best_practices"      in (v as object) &&
    "refined_enrichment_notes"    in (v as object),
  );
}

export function isBacklogPayload(v: unknown): v is BacklogPayload {
  return Boolean(v && typeof v === "object" && Array.isArray((v as BacklogPayload).epics));
}

export function extractBacklogPayload(v: unknown): BacklogPayload | null {
  if (isBacklogPayload(v)) return v;
  if (v && typeof v === "object" && "corrected_backlog" in (v as object)) {
    const corrected = (v as { corrected_backlog?: unknown }).corrected_backlog;
    if (isBacklogPayload(corrected)) return corrected;
  }
  return null;
}

export function isSprintPlanning(v: unknown): v is { sprints: unknown[] } {
  return Boolean(v && typeof v === "object" && Array.isArray((v as any).sprints));
}