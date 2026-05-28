import { CheckCircle, ListChecks, Plus, RefreshCw, ExternalLink, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SaveSummaryBannerProps {
  total: number;
  created: number;
  updated: number;
  name?: string;
  navigateToNewAction: () => void;
  navigateToConsultationSpace: () => void;
}

export function SaveSummaryBanner({ 
    total, 
    created, 
    updated, 
    name,
    navigateToNewAction,
    navigateToConsultationSpace, 
}: SaveSummaryBannerProps) {
  return (
    <section>
      <div className="space-y-4">

        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-full bg-primary text-primary-foreground flex items-center justify-center flex-shrink-0">
            <CheckCircle className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-foreground">Tasks saved to ClickUp</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Here's a breakdown of what was applied to your space.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 sm:gap-3">
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
        </div>

        <div className="border-t border-gray-200 pt-3 flex flex-wrap justify-end gap-2">
          <Button
            variant="outline"
            className="gap-2"
            onClick={navigateToNewAction}
          >
            <Sparkles className="w-4 h-4" />
            {`New ${name}`}
          </Button>
          <Button
            className="gap-2"
            onClick={navigateToConsultationSpace}
          >
            <ExternalLink className="w-4 h-4" />
            View space tasks
          </Button>
        </div>

      </div>
    </section>
  );
}