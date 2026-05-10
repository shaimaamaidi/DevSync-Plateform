import { useState, useMemo, useEffect, useRef } from 'react';
import { Sparkles, Plus } from 'lucide-react';
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
import { useClickUpSpacesList } from '@/hooks/clickup-structure-hooks/use-clickup-spaces';
import { useClickUpStructure } from '@/hooks/clickup-structure-hooks/use-clikcup-structure';
import { taskGenerationService } from '@/services/task-generation-from-summary-service';
import { taskVerificationService } from '@/services/task-verification-service';
import { saveInClickupService } from '@/services/save-in-clickup-service';
import { GeneratedTaskList } from '@/components/generated-tasks-list';
import { VerifiedTaskList } from '@/components/verified-tasks-list';
import { CreateSpaceForm } from '@/components/ui/create-space-form';
import { StepHeader } from '@/components/ui/step-header';

type AssigneeDialogState =
  | { open: false }
  | { open: true; type: 'names'; items: string[] }
  | { open: true; type: 'mails'; items: string[] };

function extractListFromMessage(message: string): string[] {
  const match = message.match(/\[([^\]]+)\]/);
  if (!match) return [message];
  return match[1]
    .split(',')
    .map(s => s.trim().replace(/^['"]|['"]$/g, ''))
    .filter(Boolean);
}

function extractErrorCode(err: unknown): string | null {
  try {
    const data = (err as any)?.response?.data;
    return data?.error?.code ?? data?.code ?? null;
  } catch {
    return null;
  }
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
  const [showCreateSpace, setShowCreateSpace] = useState(false);
  const [isCreateNewSpace, setIsCreateNewSpace] = useState(false);

  const { structure, loading: structureLoading, isStructureEmpty, isFetching} = useClickUpStructure(selectedSpaceId);
  
  const [realIsStructureEmpty, setRealIsStructureEmpty] = useState(true);
  
  const canGenerate = summary.trim().length > 0 && selectedSpaceId !== '';

  const [isStep3Done, setIsStep3Done] = useState(false);

  const [pendingSpaceId, setPendingSpaceId] = useState<string | null>(null);
  const [showSpaceChangeDialog, setShowSpaceChangeDialog] = useState(false);

  const hasStarted = generatedTasks.length > 0 || verifiedTasks.length > 0 || isGenerating || isVerifying;
  
  const shouldAutoGenerate = useRef(false);
  const shouldAutoVerify = useRef(false);


  const allTasksHaveLocation = (tasks: GeneratedTask[] | VerifiedTask[]) =>
    tasks.every(t => t.location?.trim().length > 0);

  const resetProcess = () => {
    setGeneratedTasks([]);
    setVerifiedTasks([]);
    setIsGenerating(false);
    setIsVerifying(false);
    setSavedOk(false);
    setIsStep3Done(false);
  };

  const handleSpaceChange = (value: string) => {
    const newId = value === 'none' ? '' : value;
 
    if (!hasStarted) {
      setSelectedSpaceId(newId);
      return;
    }
 
    setPendingSpaceId(newId);
    setShowSpaceChangeDialog(true);
  };

  const handleConfirmSpaceChangeAndGenerate = async () => {
    if(isCreateNewSpace){
      setShowSpaceChangeDialog(false);
      setShowCreateSpace(true);
      return;
    }

    if (pendingSpaceId === null) 
      return;

    resetProcess();
    setShowSpaceChangeDialog(false);

    setSelectedSpaceId(pendingSpaceId);
    shouldAutoGenerate.current = true;
    setPendingSpaceId(null);
  };
 
  const handleCreateNewSpace = () => {
    if (hasStarted) {
      setShowSpaceChangeDialog(true);
      setIsCreateNewSpace(true);
      return;
    }
    setShowCreateSpace(true);
  };

  useEffect(() => {
    if (shouldAutoGenerate.current && selectedSpaceId && summary.trim().length > 0) {
      shouldAutoGenerate.current = false;
      handleGenerate(selectedSpaceId);
    }
  }, [selectedSpaceId]);


  useEffect(() => {
    if (shouldAutoVerify.current && !structureLoading && generatedTasks.length > 0 && structure.length === 0) {
      shouldAutoVerify.current = false;
      setVerifiedTasks(
        generatedTasks.map(t => ({
          action: 'create' as const,
          task_name: t.task_name,
          task_description: t.task_description,
          task_assigne: t.task_assigne,
          task_status: t.task_status,
          task_priority: t.task_priority,
          location: t.location,
        })),
      );
    }
  }, [structureLoading, generatedTasks, structure]);

  const handleGenerate = async (spaceIdOverride?: string) => {
    const spaceId = spaceIdOverride ?? selectedSpaceId;
    
    if (!canGenerate) 
      return;

    setRealIsStructureEmpty(isStructureEmpty);
    setIsGenerating(true);
    setSavedOk(false);
    setGeneratedTasks([]);
    setVerifiedTasks([]);

    const result = await withErrorHandling(
      () => taskGenerationService.generateFromSummary(summary, spaceId),
      'Generate tasks',
      onError,
    );

    if (result){
      showSuccessToast('Click Up tasks generated successfully');
      setGeneratedTasks(result);
      shouldAutoVerify.current = true;
    }
    setIsGenerating(false);
  };

  const handleVerify = async () => {
    if (!generatedTasks.length) 
      return;
    if (!allTasksHaveLocation(generatedTasks)) 
      return;
    setIsVerifying(true);
    setSavedOk(false);

    const result = await withErrorHandling(
      () => taskVerificationService.verifyTasks(selectedSpaceId, generatedTasks),
      'Verify tasks',
      onError,
    );
    if (result){
      setIsStep3Done(true);
      showSuccessToast('Click Up task verified successfully');
      if (result?.tasks) {
        setVerifiedTasks(result.tasks as unknown as VerifiedTask[]);
      }
    }
    setIsVerifying(false);
  };

  const executeSave = async (ignoreNames: boolean, ignoreMails: boolean) => {
    if (!verifiedTasks.length || !selectedSpaceId) 
      return;
    if (!allTasksHaveLocation(verifiedTasks)) return;
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
        showSuccessToast('Click Up tasks saved successfully');
      }
    } catch (err: unknown) {
      const code = extractErrorCode(err);
      const message = normalizeErrorMessage(err);

      if (code === 'ASSIGNEE_NAME_NOT_FOUND' && !ignoreNames) {
        setAssigneeDialog({ open: true, type: 'names', items: extractListFromMessage(message) });
      } else if (code === 'ASSIGNEE_EMAIL_NOT_IN_CLICKUP') {
        setAssigneeDialog({ open: true, type: 'mails', items: extractListFromMessage(message) });
      } else {
        onError(handleApiError(err), message);
      }
    }

    setIsSaving(false);
  };

  const handleSave = () => executeSave(false, false);
  const handleIgnoreNames = () => { setAssigneeDialog({ open: false }); executeSave(true, false); };
  const handleIgnoreMails = () => { setAssigneeDialog({ open: false }); executeSave(true, true); };

  const handleDropFromGenerated = (task: GeneratedTask) => {
    if (!isStep3Done) 
      return;

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
        location: task.location,
      },
    ]);
  };

  return (
    <div className="w-full space-y-8 py-2">

      <section>
        <StepHeader number={1} title="Meeting summary" />
        <div className="mt-3 space-y-3">

          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">ClickUp space</label>
            <div className="flex items-center gap-2">
              <Select
                value={selectedSpaceId || 'none'}
                onValueChange={handleSpaceChange}
                disabled={spacesLoading || isGenerating}
              >
                <SelectTrigger  className={`w-[500px] bg-input border-border ${!selectedSpaceId || selectedSpaceId === 'none'? 'text-muted-foreground': 'text-foreground'}`}>
                  <SelectValue
                    placeholder={spacesLoading ? 'Loading spaces…' : 'Select a ClickUp space…'}
                  />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {!spacesLoading && spaces.length === 0 ? (
                    <SelectItem value="none" className="text-muted-foreground" disabled>No ClickUp space found</SelectItem>
                  ) : (
                    <>
                      <SelectItem value="none" className="text-muted-foreground hidden" disabled>No Click up space selected</SelectItem>
                      {spaces.map(space => (
                        <SelectItem
                          key={space.space_code ?? ''}
                          value={space.space_code ?? ''}
                        >
                          {space.name}
                        </SelectItem>
                      ))}
                    </>
                  )}
                </SelectContent>
              </Select>
              <Button 
                onClick={handleCreateNewSpace} 
                disabled={isGenerating} className="gap-2"
              >
                <Plus className="w-4 h-4" />
                New click up space
              </Button>
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Meeting Summary</label>
            <textarea
              value={summary}
              onChange={e => setSummary(e.target.value)}
              placeholder={`Paste or type your meeting summary in arabic here…`}
              className="w-full min-h-[120px] resize-y rounded-xl border border-border bg-muted/40 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring transition"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">{summary.length} characters</span>
            <Button
              onClick={() => handleGenerate()}
              disabled={!canGenerate || isGenerating}
              className="gap-2"
              title={
                !selectedSpaceId
                  ? 'Select a ClickUp space first'
                  : !summary.trim()
                  ? 'Enter meeting summary first'
                  : ''
              }
            >
              <Sparkles className="w-4 h-4" />
              {isGenerating ? 'Generating…' : 'Generate tasks'}
            </Button>
          </div>
        </div>
      </section>
      {!realIsStructureEmpty ? (
        <>
          {(generatedTasks.length > 0 || isGenerating) && (
            <section>
              <StepHeader
                number={2}
                isLoading={isGenerating}
                title="Generated tasks"
                subtitle="Delete irrelevant tasks, then verify."
              />
              <div className="mt-3">
                {!isGenerating && generatedTasks.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-6 border border-dashed rounded-xl">
                    No tasks generated from this summary.
                  </p>
                ) : (
                  <GeneratedTaskList
                    tasks={generatedTasks}
                    isLoading={isGenerating}
                    onDelete={idx => setGeneratedTasks(prev => prev.filter((_, i) => i !== idx))}
                    onUpdate={(idx, updated) =>
                      setGeneratedTasks(prev => prev.map((t, i) => (i === idx ? updated : t)))
                    }
                    onVerify={handleVerify}
                    isVerifying={isVerifying}
                    canVerify={allTasksHaveLocation(generatedTasks)}
                    structure={structure}
                    structureLoading={isFetching}
                    spaceId={selectedSpaceId}
                    isStep3Done={isStep3Done}
                  />
                )}
              </div>
            </section>
          )}

          {(verifiedTasks.length > 0 || isVerifying) && (
            <section>
              <StepHeader
                number={3}
                isLoading={isVerifying}
                title="Verified tasks"
                subtitle="Edit, add, or remove tasks. These will be saved to ClickUp."
              />
              <div className="mt-3">
                {!isVerifying && verifiedTasks.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-6 border border-dashed rounded-xl">
                    No tasks to add — all tasks already exist in ClickUp.
                  </p>
                ) : (
                  <VerifiedTaskList
                    tasks={verifiedTasks}
                    isLoading={isVerifying}
                    onChange={setVerifiedTasks}
                    onDrop={handleDropFromGenerated}
                    onSave={handleSave}
                    isSaving={isSaving}
                    savedOk={savedOk}
                    spaceId={selectedSpaceId}
                    structure={structure}
                    structureLoading={isFetching}
                    isStructureEmpty={isStructureEmpty}
                    canSave={allTasksHaveLocation(verifiedTasks)}
                  />
                )}
              </div>
            </section>
          )}
        </>
      ) : (
        <>
          {(verifiedTasks.length > 0 || isGenerating) && (
            <section>
                <StepHeader
                  number={2}
                  isLoading={isGenerating}
                  title="Generated tasks"
                  subtitle="Edit, add, or remove tasks. These will be directly saved to ClickUp (click up space chosen contain no folder and no list)."
                />
                <div className="mt-3">
                  {!isGenerating && verifiedTasks.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-6 border border-dashed rounded-xl">
                      No tasks to add — all tasks already exist in ClickUp.
                    </p>
                  ) : (
                    <VerifiedTaskList
                      tasks={verifiedTasks}
                      isLoading={isGenerating}
                      onChange={setVerifiedTasks}
                      onDrop={handleDropFromGenerated}
                      onSave={handleSave}
                      isSaving={isSaving}
                      savedOk={savedOk}
                      spaceId={selectedSpaceId}
                      structure={structure}
                      structureLoading={isFetching}
                      isStructureEmpty={isStructureEmpty}
                      canSave={allTasksHaveLocation(verifiedTasks)}
                    />
                  )}
                </div>
              </section>
          )}
        </>
      )}
      <Dialog
        open={showSpaceChangeDialog}
        onOpenChange={open => { if (!open) { setShowSpaceChangeDialog(false); setPendingSpaceId(null); } }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change ClickUp space?</DialogTitle>
            <DialogDescription>
              You have already started the task generation process. Switching to a different
              space will <strong>reset all current progress</strong> — generated and verified
              tasks will be cleared — and generation will restart automatically with the new
              space. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => { setShowSpaceChangeDialog(false); setPendingSpaceId(null); }}
            >
              Cancel
            </Button>
            <Button onClick={handleConfirmSpaceChangeAndGenerate}>
              Yes, switch &amp; regenerate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
 
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
                <li key={name} className="text-sm px-3 py-1.5 rounded-md bg-muted text-foreground font-medium">
                  {name}
                </li>
              ))}
            </ul>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setAssigneeDialog({ open: false })}>No</Button>
            <Button onClick={handleIgnoreNames}>Yes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
                <li key={mail} className="text-sm px-3 py-1.5 rounded-md bg-muted text-foreground font-medium">
                  {mail}
                </li>
              ))}
            </ul>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setAssigneeDialog({ open: false })}>No</Button>
            <Button onClick={handleIgnoreMails}>Yes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <CreateSpaceForm
        isOpen={showCreateSpace}
        onClose={() => {
          setShowCreateSpace(false)
        }}
        onSuccess={space => {
          if(hasStarted){
            resetProcess();
            shouldAutoGenerate.current = true;
          }
          setRealIsStructureEmpty(true);
          setIsCreateNewSpace(false);
      
          if (space.space_code) setSelectedSpaceId(space.space_code);
          setPendingSpaceId(null);
        }}
      />

    </div>
  );
}
