import { Layers, Zap, Heart, ArrowRight, Circle, Sparkles } from 'lucide-react';

export function AppFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-12 bg-white border-t border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 pt-10 pb-6">

        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-xl font-black tracking-tight" style={{ color: '#0E9E82' }}>
                Rido Ops
              </span>
            </div>

            <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed max-w-xs">
              Manage GitHub repos, teams, and deployments — unified with ClickUp for
              end-to-end project visibility and AI-powered task intelligence.
            </p>

            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/5">
              <Circle className="w-2 h-2 fill-emerald-500 text-emerald-500 animate-pulse" />
              <span className="text-[11px] font-medium text-emerald-600 dark:text-emerald-400 tracking-wide">
                All systems operational
              </span>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="flex items-center gap-2 text-[10px] font-bold tracking-[0.25em] uppercase" style={{ color: '#0E9E82' }}>
              <Layers className="w-3 h-3" />
              Core
            </h3>
            <ul className="space-y-3">
              {[
                'Repository Management',
                'Team Member Tracking',
                'Deployment Monitoring',
                'Branch & PR Oversight',
                'ClickUp Spaces',
                'Task CRUD & Sync',
              ].map((label) => (
                <li key={label} className="group flex items-start gap-2">
                  <ArrowRight className="w-3 h-3 mt-0.5 text-blue-300 group-hover:text-blue-500 dark:text-blue-900 dark:group-hover:text-blue-400 transition-colors shrink-0" />
                  <span className="text-xs font-medium text-zinc-600 dark:text-zinc-300 group-hover:text-zinc-900 dark:group-hover:text-white transition-colors block leading-tight">
                    {label}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-4">
            <h3 className="flex items-center gap-2 text-[10px] font-bold tracking-[0.25em] uppercase" style={{ color: '#0E9E82' }}>
              <Sparkles className="w-3 h-3" />
              AI Capabilities
            </h3>
            <ul className="space-y-3">
              {[
                'Tasks from Meeting Summary',
                'Backlog from Description',
                'LLM Task Progress Tracking',
              ].map((label) => (
                <li key={label} className="group flex items-start gap-2">
                  <ArrowRight className="w-3 h-3 mt-0.5 text-blue-300 group-hover:text-blue-500 dark:text-blue-900 dark:group-hover:text-blue-400 transition-colors shrink-0" />
                  <span className="text-xs font-medium text-zinc-600 dark:text-zinc-300 group-hover:text-zinc-900 dark:group-hover:text-white transition-colors block leading-tight">
                    {label}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-4">
            <h3 className="flex items-center gap-2 text-[10px] font-bold tracking-[0.25em] uppercase" style={{ color: '#0E9E82' }}>
              <Zap className="w-3 h-3" />
              ClickUp
            </h3>
            <ul className="space-y-3">
              {[
                'Create & Update Tasks',
                'Manage Spaces & Lists',
                'Assign Members',
                'Priorities & Deadlines',
                'Completion Status',
                'Two-way Sync',
              ].map((label) => (
                <li key={label} className="group flex items-start gap-2">
                  <ArrowRight className="w-3 h-3 mt-0.5 text-emerald-300 group-hover:text-emerald-500 dark:text-emerald-900 dark:group-hover:text-emerald-400 transition-colors shrink-0" />
                  <span className="text-xs font-medium text-zinc-600 dark:text-zinc-300 group-hover:text-zinc-900 dark:group-hover:text-white transition-colors block leading-tight">
                    {label}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-5 border-t border-zinc-100 dark:border-zinc-800 flex justify-center">
          <p className="text-[11px] text-zinc-400 dark:text-zinc-600 flex items-center gap-1.5 tracking-wide">
            Made with{' '}
            <Heart className="w-3 h-3 text-rose-400 fill-rose-400" />{' '}
            for developers
            <span className="mx-1">·</span>
            © {year} Rido Ops
          </p>
        </div>
      </div>
    </footer>
  );
}