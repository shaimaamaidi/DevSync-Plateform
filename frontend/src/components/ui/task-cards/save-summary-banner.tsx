import { CheckCircle, ListChecks, Plus, RefreshCw, ExternalLink, Sparkles, XCircle, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/shared-primitives/button';
import type { FailedTask } from '@/api/api';

interface SaveSummaryBannerProps {
  total: number;
  created: number;
  updated: number;
  failed: number;
  failedTasks?: FailedTask[];
  name?: string;
  navigateToNewAction: () => void;
  navigateToConsultationSpace: () => void;
}

export function SaveSummaryBanner({ 
    total, 
    created, 
    updated,
    failed,
    failedTasks = [],
    name,
    navigateToNewAction,
    navigateToConsultationSpace, 
}: SaveSummaryBannerProps) {
  const [showFailed, setShowFailed] = useState(false);
  const hasFailures = failed > 0 && failedTasks.length > 0;

  return (
    <section>
      <div className="space-y-4">

        <div className="flex items-center gap-3">
          <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
            hasFailures
              ? 'bg-amber-100 text-amber-600 dark:bg-amber-900 dark:text-amber-400'
              : 'bg-primary text-primary-foreground'
          }`}>
            {hasFailures ? <AlertTriangle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
          </div>
          <div>
            <h2 className="text-base font-semibold text-foreground">
              {hasFailures ? 'Tasks saved with some failures' : 'Tasks saved to ClickUp'}
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Here's a breakdown of what was applied to your space.
            </p>
          </div>
        </div>

        <div className={`grid gap-2 sm:gap-3 ${hasFailures ? 'grid-cols-2 sm:grid-cols-4' : 'grid-cols-3'}`}>
          <div className="bg-muted rounded-md p-3 space-y-1">
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <ListChecks className="w-3 h-3" aria-hidden="true" />
              Total
            </p>
            <p className="text-xl font-semibold text-foreground">{total}</p>
          </div>
          <div className="bg-muted rounded-md p-3 space-y-1">
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Plus className="w-3 h-3" aria-hidden="true" />
              Created
            </p>
            <p className="text-xl font-semibold text-green-600 dark:text-green-400">{created}</p>
          </div>
          <div className="bg-muted rounded-md p-3 space-y-1">
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <RefreshCw className="w-3 h-3" aria-hidden="true" />
              Updated
            </p>
            <p className="text-xl font-semibold text-blue-600 dark:text-blue-400">{updated}</p>
          </div>
          {(hasFailures) && (
            <div className="bg-muted rounded-md p-3 space-y-1">
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <XCircle className="w-3 h-3" aria-hidden="true" />
                Failed
              </p>
              <p className="text-xl font-semibold text-red-600 dark:text-red-400">{failed}</p>
            </div>
          )}
        </div>

        {hasFailures && (
          <div className="border border-red-200 dark:border-red-900 rounded-md overflow-hidden">
            <button
              onClick={() => setShowFailed(v => !v)}
              className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-950/40 hover:bg-red-100 dark:hover:bg-red-950/60 transition-colors"
            >
              <span className="flex items-center gap-2">
                <XCircle className="w-3.5 h-3.5" />
                {failed} task{failed > 1 ? 's' : ''} failed — see details
              </span>
              {showFailed ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
            {showFailed && (
              <ul className="divide-y divide-red-100 dark:divide-red-900/40">
                {failedTasks.map((ft, i) => (
                  <li key={i} className="px-3 py-2.5 space-y-0.5 bg-background">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium text-foreground truncate">{ft.task_name}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 ${
                        ft.action === 'create'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400'
                          : ft.action === 'update'
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400'
                          : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
                      }`}>
                        {ft.action}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">{ft.reason}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div className="border-t border-gray-200 pt-3 flex flex-wrap justify-end gap-2">
          <Button variant="outline" className="gap-2" onClick={navigateToNewAction}>
            <Sparkles className="w-4 h-4" />
            {`New ${name}`}
          </Button>
          <Button className="gap-2" onClick={navigateToConsultationSpace}>
            <ExternalLink className="w-4 h-4" />
            View space tasks
          </Button>
        </div>

      </div>
    </section>
  );
}