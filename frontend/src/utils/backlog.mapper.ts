import type { 
  BacklogPayload, 
  MarketSummary, 
  RefinedMarketIntelligence, 
  UiEpic, 
  UiSprint 
} from "@/types/backlog";


export function refinedToSummary(r: RefinedMarketIntelligence): MarketSummary {
  return {
    market_trends:       r.refined_market_trends,
    competitor_features: r.refined_competitor_features,
    user_pain_points:    r.refined_user_pain_points,
    best_practices:      r.refined_best_practices,
    enrichment_notes:    r.refined_enrichment_notes,
  };
};

export function normalizeMarketSummary(value: MarketSummary): MarketSummary {
  return {
    market_trends: value?.market_trends ?? "",
    competitor_features: Array.isArray(value?.competitor_features) ? value.competitor_features : [],
    user_pain_points: Array.isArray(value?.user_pain_points) ? value.user_pain_points : [],
    best_practices: Array.isArray(value?.best_practices) ? value.best_practices : [],
    enrichment_notes: value?.enrichment_notes ?? "",
  };
};

export function normalizeBacklog(epics: UiEpic[]): UiEpic[] {
  return (epics ?? []).map((epic) => ({
    id:          epic.id          ?? `E${Math.random()}`,
    title:       epic.title       ?? "",
    description: epic.description ?? "",
    stories: (epic.stories ?? []).map((story) => ({
      id:      story.id      ?? `US${Math.random()}`,
      title:   story.title   ?? "",
      as_a:    story.as_a    ?? "user",
      i_want:  story.i_want  ?? "",
      so_that: story.so_that ?? "",
      tasks: (story.tasks ?? []).map((task) => ({
        id:       task.id       ?? `T${Math.random()}`,
        title:    task.title    ?? "",
        description: task.description ?? "?",
      })),
    })),
  }));
}

export function cloneMarketSummary(value: MarketSummary): MarketSummary {
  return {
    market_trends: value.market_trends,
    competitor_features: [...value.competitor_features],
    user_pain_points: [...value.user_pain_points],
    best_practices: [...value.best_practices],
    enrichment_notes: value.enrichment_notes,
  };
};

export function cloneBacklog(epics: UiEpic[]): UiEpic[] {
  return normalizeBacklog(epics).map((epic) => ({
    ...epic,
    stories: epic.stories.map((story) => ({
      ...story,
      tasks: [...story.tasks],
    })),
  }));
};

function toComparableMarketSummary(value: MarketSummary): MarketSummary {
  return {
    market_trends: (value.market_trends ?? "").trim(),
    competitor_features: (value.competitor_features ?? []).map((item) => (item ?? "").trim()),
    user_pain_points: (value.user_pain_points ?? []).map((item) => (item ?? "").trim()),
    best_practices: (value.best_practices ?? []).map((item) => (item ?? "").trim()),
    enrichment_notes: (value.enrichment_notes ?? "").trim(),
  };
};

export function areMarketSummariesEqual(a: MarketSummary, b: MarketSummary): boolean {
  return JSON.stringify(toComparableMarketSummary(normalizeMarketSummary(a))) ===
    JSON.stringify(toComparableMarketSummary(normalizeMarketSummary(b)));
};

function parseUserStoryDescription(description: string): { as_a: string; i_want: string; so_that: string } {
  const text = (description ?? "").trim();
  if (!text) 
    return { as_a: "user", i_want: "", so_that: "" };
  let as_a = "user";
  let remaining = text;
  
  const lower = text.toLowerCase();
  if (lower.startsWith("as a ")) {
    const afterAsA = text.slice(5); // remove "As a "
    const commaIndex = afterAsA.indexOf(",");

    if (commaIndex !== -1) {
      as_a = afterAsA.slice(0, commaIndex).trim() || "user";
      remaining = afterAsA.slice(commaIndex + 1).trim();
    } else {
      const parts = afterAsA.split(" ");
      as_a = parts[0] || "user";
      remaining = afterAsA.slice(as_a.length).trim();
    }
  }

  if (remaining.toLowerCase().startsWith("i want")) {
    remaining = remaining.slice(6).trim();
  }

  let i_want = remaining;
  let so_that = "";

  const soThatIndex = remaining.toLowerCase().indexOf("so that");

  if (soThatIndex !== -1) {
    i_want = remaining.slice(0, soThatIndex).replace(/,$/, "").trim();
    so_that = remaining.slice(soThatIndex + 7).trim(); // "so that".length = 7
  }

  return {
    as_a,
    i_want,
    so_that,
  };
};

export function backlogToUi(b: BacklogPayload): UiEpic[] {
  return (b.epics ?? []).map((eb, ei) => ({
    id: `E${ei + 1}`,
    title: eb.epic?.title ?? `Epic ${ei + 1}`,
    description: eb.epic?.description ?? "",
    stories: (eb.user_stories ?? []).map((usb, si) => ({
      id:`US${ei + 1}.${si + 1}`,
      title: usb.user_story?.title ?? `Story ${si + 1}`,
      ...parseUserStoryDescription(usb.user_story?.description ?? ""),
      tasks: (usb.tasks ?? []).map((t, ti) => ({
        id: `T${ei + 1}.${si + 1}.${ti + 1}`,
        title: t?.title ?? `Task ${ti + 1}`,
        description: t?.description ?? "?",
      })),
    })),
  }));
};

export function uiToBacklog(epics: UiEpic[]): BacklogPayload {
  return {
    epics: (epics ?? []).map((ep) => ({
      epic: {
        title: ep.title?.trim() || "",
        description: ep.description?.trim() || "",
      },

      user_stories: (ep.stories ?? []).map((s) => {
        const as_a = (s.as_a ?? "user").trim().replace(/\s*,\s*$/, "").trim() || "user";
        const i_want = (s.i_want ?? "").trim().replace(/\s*,\s*$/, "").trim();
        let so_that = (s.so_that ?? "").trim();
        const lower = so_that.toLowerCase();
        if (lower.startsWith("so that ")) {
          so_that = so_that.slice(7).trim();
        }

        let description = `As a ${as_a}, I want ${i_want}`;

        if (so_that) {
          description += `, so that ${so_that}`;
        }

        return {
          user_story: {
            title: s.title ?? "",
            description,
          },
          tasks: (s.tasks ?? []).map((t) => ({
            title: t.title ?? "",
            description: t.description ?? "",
          })),
        };
      }),
    })),
  };
};

export function areBacklogsEqual(a: BacklogPayload, b: BacklogPayload): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

export function sprintPlanningToUi(raw: any): UiSprint[] {
  return (raw?.sprints ?? []).map((sprint: any, si: number) => ({
    id: `S${si + 1}`,
    name: sprint.name ?? `Sprint ${si + 1}`,
    goal: sprint.goal ?? "",
    totalEstimatedHours: sprint.total_estimated_hours ?? 0,
    stories: (sprint.user_stories ?? []).map((us: any, ui: number) => ({
      id: `S${si + 1}.US${ui + 1}`,
      title: us.user_story?.title ?? "",
      ...parseUserStoryDescription(us.user_story?.description ?? ""),
      tasks: (us.tasks ?? []).map((t: any, ti: number) => ({
        id: `S${si + 1}.US${ui + 1}.T${ti + 1}`,
        title: t.task?.title ?? "",
        description: t.task?.description ?? "",
        estimatedHours: t.estimated_hours ?? 0,
      })),
    })),
  }));
}