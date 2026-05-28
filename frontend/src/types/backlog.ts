export interface RefinedMarketIntelligence {
  refined_market_trends: string;
  refined_competitor_features: string[];
  refined_user_pain_points: string[];
  refined_best_practices: string[];
  refined_enrichment_notes: string;
  is_valid: boolean;
  cause?: string;
}

export interface MarketSummary {
  market_trends: string;
  competitor_features: string[];
  user_pain_points: string[];
  best_practices: string[];
  enrichment_notes: string;
}

export interface UiTask {
  id: string;
  title: string;
  description: string;
}

export interface UiStory {
  id: string;
  title: string;
  as_a: string;
  i_want: string;
  so_that: string;
  tasks: UiTask[];
}

export interface UiEpic {
  id: string;
  title: string;
  description: string;
  stories: UiStory[];
}

export interface BacklogPayload {
  epics: Array<{
    epic: { title: string; description: string };
    user_stories: Array<{
      user_story: { title: string; description: string };
      tasks: Array<{ title: string; description: string }>;
    }>;
  }>;
}
export interface UiTaskEstimate {
  id: string;
  title: string;
  description: string;
  estimatedHours: number;
}

export interface UiSprintStory {
  id: string;
  title: string;
  as_a: string;
  i_want: string;
  so_that: string;
  tasks: UiTaskEstimate[];
}

export interface UiSprint {
  id: string;
  name: string;
  goal: string;
  totalEstimatedHours: number;
  stories: UiSprintStory[];
}

export interface ChatMessage {
  id: number;
  ts: Date;
  role: "user" | "agent";
  content: string;
  _streaming?: boolean;
  attachment?: ChatAttachment;
  isRejection?: boolean;
  onRetry?: () => void;
}

export interface ChatAttachment {
  type: "market" | "submitted" | "backlog" | "sprint" | "clickup_prompt";
  data?: MarketSummary | UiEpic[] | UiSprint[] | any | undefined;
  editable?: boolean;
  mode?: "validation" | "backlog_generation" | "backlog_refinement" | "backlog_finishing";
}
