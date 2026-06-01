const TOOL_LABELS: Record<string, string> = {
  build_product_context: "Analyzing your product description…",
  generate_market_queries: "Preparing market research queries…",
  web_search: "Searching the web…",
  summarize_market_intelligence: "Summarizing market intelligence…",
  validate_market_intelligence: "Validating market intelligence…",
  generate_backlog: "Generating your backlog…",
  fix_user_backlog: "Reviewing your backlog changes…",
  delivery_planning: "Planning your delivery sprints…",
};

export function getToolLabel(name: string): string {
  return TOOL_LABELS[name] ?? `Running ${name}…`;
}