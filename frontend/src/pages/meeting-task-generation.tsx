import { useState, useMemo } from 'react';
import { Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { withErrorHandling, handleApiError, normalizeErrorMessage } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { showSuccessToast } from '@/components/global-toaster';
import type { GeneratedTask, VerifiedTask } from '@/api/api';
import { useClickUpSpacesList } from '@/hooks/use-clickup-spaces';
import { taskGenerationService } from '@/services/task-generation-from-summary-service';
import { taskVerificationService } from '@/services/task-verification-service';
import { saveInClickupService } from '@/services/save-in-clickup-service';
import { GeneratedTaskList } from '@/components/generated-tasks-list';
import { VerifiedTaskList } from '@/components/verified-tasks-list';



// ── Assignee dialog state ────────────────────────────────────────────────────
type AssigneeDialogState =
  | { open: false }
  | { open: true; type: 'names'; items: string[] }
  | { open: true; type: 'mails'; items: string[] };

// Extract list from backend error message like: "... not found: ['name1', 'name2']"
function extractListFromMessage(message: string): string[] {
  const match = message.match(/\[([^\]]+)\]/);
  if (!match) return [message];
  return match[1]
    .split(',')
    .map(s => s.trim().replace(/^['"]|['"]$/g, ''))
    .filter(Boolean);
}

export function MeetingTaskManager() {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const { spaces, loading: spacesLoading } = useClickUpSpacesList();

  const [selectedSpaceId, setSelectedSpaceId] = useState<string>('');
  const [summary, setSummary] = useState('');
  const [generatedTasks, setGeneratedTasks] = useState<GeneratedTask[]>([]);
  const [verifiedTasks, setVerifiedTasks] = useState<VerifiedTask[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [savedOk, setSavedOk] = useState(false);

  const [assigneeDialog, setAssigneeDialog] = useState<AssigneeDialogState>({ open: false });

  const canGenerate = summary.trim().length > 0 && selectedSpaceId !== '';

  // ── Step 1: Generate ──────────────────────────────────────────────────────
  const handleGenerate = async () => {
    if (!canGenerate) return;
    setIsGenerating(true);
    setSavedOk(false);
    setGeneratedTasks([]);
    setVerifiedTasks([]);

    const result = await withErrorHandling(
      () => taskGenerationService.generateFromSummary(summary, selectedSpaceId),
      'Generate tasks',
      onError,
    );

    if (result) setGeneratedTasks(result);
    setIsGenerating(false);
  };

  // ── Step 2: Verify ────────────────────────────────────────────────────────
  const handleVerify = async () => {
    if (!generatedTasks.length) return;
    setIsVerifying(true);
    setSavedOk(false);

    const result = await withErrorHandling(
      () => taskVerificationService.verifyTasks(selectedSpaceId, generatedTasks),
      'Verify tasks',
      onError,
    );

    if (result?.tasks) {
      setVerifiedTasks(result.tasks as unknown as VerifiedTask[]);
    }
    setIsVerifying(false);
  };

  // ── Step 3: Save with assignee retry chain ────────────────────────────────
  // First call:  ignore_names=false, ignore_mails=false
  // If 424 (AssigneeNameNotFoundException):  open names dialog → retry with ignore_names=true, ignore_mails=false
  // If 422 (AssigneeEmailNotInClickUpException): open mails dialog → retry with ignore_names=true, ignore_mails=true
  // All other errors: delegate to global onError via handleApiError + normalizeErrorMessage
  //   (same classification logic used internally by withErrorHandling)
  const executeSave = async (ignoreNames: boolean, ignoreMails: boolean) => {
    if (!verifiedTasks.length || !selectedSpaceId) return;
    setIsSaving(true);

    try {
      const result = await saveInClickupService.saveTasks(
        selectedSpaceId,
        verifiedTasks as unknown as VerifiedTask[],
        { ignoreNames, ignoreMails },
      );

      if (result) {
        setSavedOk(true);
        setAssigneeDialog({ open: false });
        showSuccessToast('Tasks saved to ClickUp successfully');
      }
    } catch (err: unknown) {
      const status = (err as any)?.response?.status as number | undefined;
      const message = normalizeErrorMessage(err);

      if (status === 424 && !ignoreNames) {
        // AssigneeNameNotFoundException → ask user to ignore unresolved names
        setAssigneeDialog({ open: true, type: 'names', items: extractListFromMessage(message) });
      } else if (status === 422) {
        // AssigneeEmailNotInClickUpException → ask user to ignore unresolved emails
        setAssigneeDialog({ open: true, type: 'mails', items: extractListFromMessage(message) });
      } else {
        // All other errors: same classification as withErrorHandling internals
        onError(handleApiError(err), message);
      }
    }

    setIsSaving(false);
  };

  const handleSave = () => executeSave(false, false);

  // User confirmed to ignore unresolved names → retry with ignore_names=true
  const handleIgnoreNames = () => {
    setAssigneeDialog({ open: false });
    executeSave(true, false);
  };

  // User confirmed to ignore unresolved emails → retry with ignore_names=true, ignore_mails=true
  const handleIgnoreMails = () => {
    setAssigneeDialog({ open: false });
    executeSave(true, true);
  };

  // ── Drag from Step 2 → Step 3 ─────────────────────────────────────────────
  const handleDropFromGenerated = (task: GeneratedTask) => {
    const alreadyExists = verifiedTasks.some(
      v => v.task_name === task.task_name && v.task_assigne === task.task_assigne,
    );
    if (alreadyExists) return;
    setVerifiedTasks(prev => [
      ...prev,
      {
        action: 'create',
        task_name: task.task_name,
        task_description: task.task_description,
        task_assigne: task.task_assigne,
        task_status: task.task_status,
        task_priority: task.task_priority,
        folder: task.folder,
      },
    ]);
  };

  return (
    <div className="w-full space-y-8 py-2">

      {/* ── Step 1 ── */}
      <section>
        <StepHeader number={1} title="Meeting summary" />
        <div className="mt-3 space-y-3">

          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">ClickUp space</label>
            <Select
              value={selectedSpaceId || 'none'}
              onValueChange={v => setSelectedSpaceId(v === 'none' ? '' : v)}
              disabled={spacesLoading || isGenerating}
            >
              <SelectTrigger className="mt-1 bg-input border-border text-foreground">
                <SelectValue
                  placeholder={spacesLoading ? 'Loading spaces…' : 'Select a ClickUp space…'}
                />
              </SelectTrigger>
              <SelectContent className="bg-card border-border">
                <SelectItem value="none">
                  <span className="text-muted-foreground">Select a space…</span>
                </SelectItem>
                {spaces.map(space => (
                  <SelectItem
                    key={space.id ?? space.space_code ?? space.name ?? ''}
                    value={space.id?.toString() ?? ''}
                  >
                    {space.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Meeting notes</label>
            <textarea
              value={summary}
              onChange={e => setSummary(e.target.value)}
              placeholder={`Paste or type your meeting notes here…\n\ne.g. "We discussed the Q3 launch. Alice will handle the landing page by Friday. Bob needs to review the API docs and open a PR."`}
              className="w-full min-h-[120px] resize-y rounded-xl border border-border bg-muted/40 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring transition"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">{summary.length} characters</span>
            <Button
              onClick={handleGenerate}
              disabled={!canGenerate || isGenerating}
              className="gap-2"
              title={
                !selectedSpaceId
                  ? 'Select a ClickUp space first'
                  : !summary.trim()
                  ? 'Enter meeting notes first'
                  : ''
              }
            >
              <Sparkles className="w-4 h-4" />
              {isGenerating ? 'Generating…' : 'Generate tasks'}
            </Button>
          </div>
        </div>
      </section>

      {/* ── Step 2 ── */}
      {(generatedTasks.length > 0 || isGenerating) && (
        <section>
          <StepHeader
            number={2}
            title="Generated tasks"
            subtitle="Delete irrelevant tasks, then verify. Drag any task into Step 3 to add it manually."
          />
          <div className="mt-3">
            <GeneratedTaskList
              tasks={generatedTasks}
              isLoading={isGenerating}
              onDelete={idx => setGeneratedTasks(prev => prev.filter((_, i) => i !== idx))}
              onVerify={handleVerify}
              isVerifying={isVerifying}
            />
          </div>
        </section>
      )}

      {/* ── Step 3 ── */}
      {(verifiedTasks.length > 0 || isVerifying) && (
        <section>
          <StepHeader
            number={3}
            title="Verified tasks"
            subtitle="Edit, add, or remove tasks. These will be saved to ClickUp."
          />
          <div className="mt-3">
            <VerifiedTaskList
              tasks={verifiedTasks}
              isLoading={isVerifying}
              onChange={setVerifiedTasks}
              onDrop={handleDropFromGenerated}
              onSave={handleSave}
              isSaving={isSaving}
              savedOk={savedOk}
            />
          </div>
        </section>
      )}

      {/* ── Dialog: Unresolved assignee NAMES (424) ── */}
      <Dialog
        open={assigneeDialog.open && assigneeDialog.type === 'names'}
        onOpenChange={open => { if (!open) setAssigneeDialog({ open: false }); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Some assignee names were not found. Do you want to ignore them?</DialogTitle>
            <DialogDescription>
              The following names could not be matched in the member database and will be
              left unassigned. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          {assigneeDialog.open && assigneeDialog.type === 'names' && (
            <ul className="mt-1 space-y-1">
              {assigneeDialog.items.map(name => (
                <li
                  key={name}
                  className="text-sm px-3 py-1.5 rounded-md bg-muted text-foreground font-medium"
                >
                  {name}
                </li>
              ))}
            </ul>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setAssigneeDialog({ open: false })}>
              No
            </Button>
            <Button onClick={handleIgnoreNames}>
              Yes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Dialog: Unresolved assignee EMAILS (422) ── */}
      <Dialog
        open={assigneeDialog.open && assigneeDialog.type === 'mails'}
        onOpenChange={open => { if (!open) setAssigneeDialog({ open: false }); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Some assignee emails were not found in ClickUp. Do you want to ignore them?</DialogTitle>
            <DialogDescription>
              The following emails could not be matched to any ClickUp workspace member and
              will be left unassigned. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          {assigneeDialog.open && assigneeDialog.type === 'mails' && (
            <ul className="mt-1 space-y-1">
              {assigneeDialog.items.map(mail => (
                <li
                  key={mail}
                  className="text-sm px-3 py-1.5 rounded-md bg-muted text-foreground font-medium"
                >
                  {mail}
                </li>
              ))}
            </ul>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setAssigneeDialog({ open: false })}>
              No
            </Button>
            <Button onClick={handleIgnoreMails}>
              Yes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

    </div>
  );
}

function StepHeader({
  number,
  title,
  subtitle,
}: {
  number: number;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-7 h-7 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold flex-shrink-0 mt-0.5">
        {number}
      </div>
      <div>
        <h2 className="text-base font-semibold text-foreground">{title}</h2>
        {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
      </div>
    </div>
  );
}


