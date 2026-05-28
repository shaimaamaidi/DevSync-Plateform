import { useState, useEffect, useRef, useCallback } from 'react';
import { Sparkles, Plus, AlertCircle } from 'lucide-react';
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
import { 
  withErrorHandling, 
  defaultOnError,
} from '@/services/api-error';
import { 
  extractStatusCode, 
  resolveErrorAction, 
  normalizeErrorMessage, 
  extractErrorCode, 
  extractAssigneeListFromError
} from '@/utils/error-handler';
import { showErrorToast, showSuccessToast } from '@/components/global-toaster';
import type { 
    GeneratedTaskFromBacklog, 
    Sprint, 
    VerifiedTaskFromBacklog 
} from '@/api/api';
import { useClickUpSpacesList } from '@/hooks/clickup-space-hooks/use-clickup-spaces';
import { useClickUpStructure } from '@/hooks/clickup-structure-hooks/use-clikcup-structure';
import { taskGenerationService } from '@/services/task-generation-service';
import { taskVerificationService } from '@/services/task-verification-service';
import { saveInClickupService } from '@/services/save-in-clickup-service';
import { GeneratedTaskList } from '@/components/generated-tasks-list';
import { VerifiedTaskList } from '@/components/verified-tasks-list';
import { SpaceSetupForm } from '@/components/ui/space-setup-form';
import { StepHeader } from '@/components/ui/step-header';
import { createPortal } from 'react-dom';
import type { TaskGenerationDTO, TaskVerificationDTO } from '@/types/clickup';
import { SaveSummaryBanner } from '@/components/ui/save-summary-banner';
import type { AssigneeDialogStateForGeneration } from '@/types/assignee-dialog';

export function BacklogTaskManager() {
  const sprintBacklogRef = useRef<Sprint | null>(null);

  const [selectedSpaceId, setSelectedSpaceId] = useState<string>('');

  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const { spaces, loading: spacesLoading } = useClickUpSpacesList();
  const { structure, loading: structureLoading, isStructureEmpty, isFetching} = useClickUpStructure(selectedSpaceId);
  const [realIsStructureEmpty, setRealIsStructureEmpty] = useState(true);

  const [generatedTasks, setGeneratedTasks] = useState<TaskGenerationDTO[]>([]);
  const pendingGenerateRef = useRef(false);
  const [verifiedTasks, setVerifiedTasks] = useState<TaskVerificationDTO[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [savedOk, setSavedOk] = useState(false);
  const [isVerificationFinished, setIsVerificationFinished] = useState(false);

  const [disabledAll, setDisabledAll] = useState(false);

  const [showSpaceChangeDialog, setShowSpaceChangeDialog] = useState(false);
  const [showRegenerateDialog, setShowRegenerateDialog] = useState(false);
  const [assigneeDialog, setAssigneeDialog] = useState<AssigneeDialogStateForGeneration>({ open: false });
  
  const [showSpaceSetup, setShowSpaceSetup] = useState(false);
  const [isNewSpace, setIsNewSpace] = useState(false);
  const [pendingSpaceId, setPendingSpaceId] = useState<string | null>(null);

  const shouldAutoGenerate = useRef(false);

  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const hasStarted = generatedTasks.length > 0 || verifiedTasks.length > 0 || isGenerating || isVerifying;

  const allTasksHaveLocation = (tasks: TaskGenerationDTO[] | TaskVerificationDTO[]) =>
    tasks.every(t => t.location?.trim().length > 0);

  const [saveSummary, setSaveSummary] = useState<{
    created: number; updated: number; total: number;
  } | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem('sprint_backlog');
    if (!raw) {
        navigate('/backlog-generation-chat');
        return;
    }
    const parsed: Sprint = JSON.parse(raw);
    if (!parsed.user_stories?.length) {
        navigate('/backlog-generation-chat');
        return;
    }
    sprintBacklogRef.current = parsed;
    localStorage.removeItem('sprint_backlog');
  }, []);

  const resetProcess = () => {
    setGeneratedTasks([]);
    setVerifiedTasks([]);
    setIsGenerating(false);
    setIsVerifying(false);
    setIsSaving(false);
    setSaveSummary(null);
    setSavedOk(false);
    setIsVerificationFinished(false);
    setDisabledAll(false);
  };

  const handleSpaceChange = (value: string) => {
    const newId = value === 'none' ? '' : value;
    if (newId) {
      setErrors(prev => {
        const { space, ...rest } = prev;
        return rest;
      });
    }
    if (!hasStarted) {
      setSelectedSpaceId(newId);
      return;
    }
 
    setPendingSpaceId(newId);
    setShowSpaceChangeDialog(true);
  };

  const handleConfirmSpaceChangeAndGenerate = async () => {
    if(isNewSpace){
      setShowSpaceChangeDialog(false);
      setShowSpaceSetup(true);
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
      setIsNewSpace(true);
      return;
    }
    setShowSpaceSetup(true);
  };

  useEffect(() => {
    if (shouldAutoGenerate.current) {
      shouldAutoGenerate.current = false;
      handleGenerate(selectedSpaceId);
    }
  }, [selectedSpaceId]);

  useEffect(() => {
    if (pendingGenerateRef.current && !structureLoading && !isFetching) {
      pendingGenerateRef.current = false;
      setRealIsStructureEmpty(isStructureEmpty);
      executeGenerate(selectedSpaceId);
    }
  }, [structureLoading, isFetching]);
  
  const validateForm = () => {
    setErrors({});
    const newErrors: Record<string, string> = {};

    if (!sprintBacklogRef.current || !sprintBacklogRef.current.user_stories?.length) {
      newErrors.backlog = 'Sprint Backlog provided is empty or invalid. Please retry the generation of backlog again.';
    }

    if (selectedSpaceId === '') {
      newErrors.space = 'Click up space is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleGenerate = async (spaceIdOverride?: string) => {
    const spaceId = spaceIdOverride ?? selectedSpaceId;

    if (!validateForm()) 
      return;

    resetProcess();
    setIsGenerating(true);

    if (structureLoading || isFetching) {
      pendingGenerateRef.current = true;
      return;
    }

    await executeGenerate(spaceId);
  };

  const executeGenerate = async (spaceId: string) => {
    const result = await withErrorHandling(
      () => taskGenerationService.generateFromBacklog(sprintBacklogRef.current as Sprint, spaceId),
      'Generate tasks from backlog',
      onError(),
    );

    if (result){
      showSuccessToast('Click up tasks generated successfully');
      setGeneratedTasks(
          result.map(t => ({
            task_name: t.task_name,
            task_description: t.task_description,
            task_assigne: t.task_assigne,
            task_status: t.task_status,
            task_priority: t.task_priority,
            location: t.location,
            estimation: t.estimation,
          })),
        );
      if (isStructureEmpty) {
        setVerifiedTasks(
          result.map(t => ({
            action: 'create' as const,
            task_name: t.task_name,
            task_description: t.task_description,
            task_assigne: t.task_assigne,
            task_status: t.task_status,
            task_priority: t.task_priority,
            location: t.location,
            estimation: t.estimation,
          })),
        );
      }
    }
    setIsGenerating(false);
  }

  const handleVerify = async () => {
    if (!generatedTasks.length) 
      return;
    if (!allTasksHaveLocation(generatedTasks)) 
      return;
    setIsVerifying(true);
    setSavedOk(false);

    const result = await withErrorHandling(
      () => taskVerificationService.verifyTasksFromBacklog(selectedSpaceId, generatedTasks as GeneratedTaskFromBacklog[]),
      'Verify tasks generated from backlog',
      onError(),
    );
    if (result){
      setIsVerificationFinished(true);
      showSuccessToast('Click up task verified successfully');
      if (result.tasks) {
        setVerifiedTasks(
            result.tasks.map(t => ({
            action: t.action,
            task_name: t.task_name,
            task_description: t.task_description,
            task_assigne: t.task_assigne,
            task_status: t.task_status,
            task_priority: t.task_priority,
            location: t.location,
            task_id: t.task_id,
            estimation: t.estimation,
          })) ,
        );
      }
    }
    setIsVerifying(false);
  };

  const executeSave = async (ignoreNames: boolean, ignoreMails: boolean) => {
    if (!verifiedTasks.length || !selectedSpaceId) return;
    if (!allTasksHaveLocation(verifiedTasks)) return;
    setIsSaving(true);

    try {
      const result = await saveInClickupService.saveTasksFromBacklog(
        selectedSpaceId,
        verifiedTasks as VerifiedTaskFromBacklog[],
        { ignoreNames, ignoreMails },
      );

      if (result) {
        setSaveSummary({
          created: verifiedTasks.filter(t => t.action === 'create').length,
          updated: verifiedTasks.filter(t => t.action === 'update').length,
          total: verifiedTasks.length,
        });
        setSavedOk(true);
        setDisabledAll(true);
        setAssigneeDialog({ open: false });
        localStorage.removeItem('sprint_backlog');
        showSuccessToast('Click up tasks saved successfully');
      }
    } catch (err: unknown) {
      const code = extractErrorCode(err);
      const status = extractStatusCode(err);
      const message = normalizeErrorMessage(err);

      if (code === 'ASSIGNEE_NAME_NOT_FOUND' && !ignoreNames) {
        setAssigneeDialog({ open: true, type: 'names', items: extractAssigneeListFromError(message) });
      } else if (code === 'ASSIGNEE_EMAIL_NOT_IN_CLICKUP') {
        setAssigneeDialog({ open: true, type: 'mails', items: extractAssigneeListFromError(message) });
      } else {
        const action = resolveErrorAction(err);
        await onError()(action, message, { code, status: status ?? undefined });
      }
    }finally{
      setIsSaving(false);
    }
  };

  const handleSave = () => executeSave(false, false);
  const handleIgnoreNames = () => { setAssigneeDialog({ open: false }); executeSave(true, false); };
  const handleIgnoreMails = () => { setAssigneeDialog({ open: false }); executeSave(true, true); };

  const handleDropFromGenerated = (task: TaskGenerationDTO) => {
    const t = task as GeneratedTaskFromBacklog;
    
    if (realIsStructureEmpty)
      return;
    if (!isVerificationFinished) 
      return;

    const sameTitle = verifiedTasks.find(
      v => v.task_name.trim().toLowerCase() === task.task_name.trim().toLowerCase(),
    );

    if (sameTitle) {
      showErrorToast('Task already exists and was not added', `Duplicate task`);
      return;  
    }
    
    setVerifiedTasks(prev => [
      ...prev,
      {
        action: 'create',
        task_name: t.task_name,
        task_description: t.task_description,
        task_assigne: t.task_assigne,
        task_status: t.task_status,
        task_priority: t.task_priority,
        location: t.location,
        estimation: t.estimation,
      },
    ]);
  };

  const navigateToNewBacklog = () => {
    navigate('/backlog-generation-chat');
  };

  const navigateToConsultationSpace = () => {
    navigate(`/spaces/${selectedSpaceId}/tasks`);
  };
  
  return (
    <div className="w-full space-y-8 py-2">
      <div className="w-full space-y-8">
        <div className={`overflow-hidden transition-all duration-500 ease-out ${
          hasStarted ? 'translate-y-2 max-h-[1000px]' : 'translate-y-0 max-h-[1000px]'
        }`}>
        <section>
          <StepHeader number={1} title="Click up space" />
          <div className="mt-3 space-y-3 border border-gray-300 rounded-lg p-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">ClickUp space</label>
              <div className="flex flex-col gap-1">
                <div className="flex flex-wrap items-center gap-2">
                  <div className="flex flex-col gap-1">
                    <Select
                      value={selectedSpaceId || 'none'}
                      onValueChange={handleSpaceChange}
                      disabled={spacesLoading || isGenerating || isVerifying || isSaving}
                    >
                      <SelectTrigger
                        className={`w-full sm:w-[500px] bg-input border-border ${
                          errors.space ? 'border-destructive' : ''
                        } ${
                          !selectedSpaceId || selectedSpaceId === 'none'
                            ? 'text-muted-foreground'
                            : 'text-foreground'
                        }`}
                      >
                        <SelectValue
                          placeholder={spacesLoading ? 'Loading spaces…' : 'Select a click up space…'}
                        />
                      </SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        {!spacesLoading && spaces.length === 0 ? (
                          <SelectItem value="none" className="text-muted-foreground" disabled>
                            No click up space found
                          </SelectItem>
                        ) : (
                          <>
                            <SelectItem value="none" className="text-muted-foreground hidden" disabled>
                              No click up space selected
                            </SelectItem>
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

                    {errors.space && (
                      <div className="text-destructive text-xs px-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        {errors.space}
                      </div>
                    )}
                  </div>

                  <Button
                    onClick={handleCreateNewSpace}
                    disabled={isGenerating || isVerifying || isSaving || disabledAll}
                    className="gap-2 self-start shrink-0"
                  >
                    <Plus className="w-4 h-4" />
                    New click up space
                  </Button>
                </div>
              </div>
            </div>
            <div className="space-y-1">              
                <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex-1">
                        {errors.backlog && (
                        <div className="text-destructive text-xs px-1 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" />
                            {errors.backlog}
                        </div>
                        )}
                    </div>
                    <Button
                        onClick={() => {
                        if (hasStarted) {
                            setShowRegenerateDialog(true);
                            return;
                        }
                        handleGenerate();
                        }}
                        disabled={isGenerating || isVerifying || isSaving || disabledAll}
                        className="gap-2 ml-auto"
                        title={
                        !selectedSpaceId
                            ? 'Select a ClickUp space first'
                            : !sprintBacklogRef.current || !sprintBacklogRef.current.user_stories?.length
                            ? 'Sprint backlog is empty or invalid, please retry the generation of backlog'
                            : ''
                        }
                    >
                        <Sparkles className="w-4 h-4" />
                        {isGenerating ? 'Generating…' : 'Generate tasks'}
                    </Button>
                </div>
            </div>
          </div>
        </section>
        </div>
        {!realIsStructureEmpty ? (
          <>
            <div className={`overflow-hidden transition-all duration-500 ease-out ${
              (generatedTasks.length > 0 || isGenerating) ? 'opacity-100 max-h-[2000px] translate-y-0' : 'opacity-0 max-h-0 -translate-y-2'
            }`}>
              <section>
                <StepHeader
                  number={2}
                  isLoading={isGenerating}
                  title="Generated tasks"
                  subtitle="Delete irrelevant tasks, then verify."
                />
                <div className="mt-3 border border-gray-300 rounded-lg p-3">
                  {!isGenerating && generatedTasks.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-6 border border-dashed rounded-xl">
                      No tasks generated from the sprint backlog provided.
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
                      isVerificationFinished={isVerificationFinished}
                      disabled={disabledAll}
                      showEstimation={true}
                    />
                  )}
                </div>
              </section>
            </div>
            <div className={`overflow-hidden transition-all duration-500 ease-out ${
              (verifiedTasks.length > 0 || isVerifying) ? 'opacity-100 max-h-[2000px] translate-y-0' : 'opacity-0 max-h-0 -translate-y-2'
            }`}>
              <section>
                <StepHeader
                  number={3}
                  isLoading={isVerifying}
                  title="Verified tasks"
                  subtitle="Edit, add, or remove tasks. These will be saved to ClickUp."
                />
                <div className="mt-3 border border-gray-300 rounded-lg p-3">
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
                      disabled={disabledAll}
                      showEstimation={true}
                    />
                  )}
                </div>
              </section>
            </div>
          </>
        ) : (
          <>
            <div className={`overflow-hidden transition-all duration-500 ease-out ${
              (verifiedTasks.length > 0 || isGenerating) ? 'opacity-100 max-h-[2000px] translate-y-0' : 'opacity-0 max-h-0 -translate-y-2'
            }`}>
              <section>
                  <StepHeader
                    number={2}
                    isLoading={isGenerating}
                    title="Generated tasks"
                    subtitle="Edit, add, or remove tasks. These will be directly saved to ClickUp (click up space chosen contain no folder and no list)."
                  />
                  <div className="mt-3 border border-gray-300 rounded-lg p-3">
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
                        disabled={disabledAll}
                        showEstimation={true}
                      />
                    )}
                  </div>
                </section>
            </div>
          </>
        )}
        {savedOk && saveSummary && (
          <div className="overflow-hidden transition-all duration-500 ease-out opacity-100 max-h-[1000px] translate-y-0">
            <section>
              <StepHeader
                number={!realIsStructureEmpty ? 4 : 3}
                title="Saved successfully"
                subtitle="Tasks have been applied to your ClickUp space."
              />
              <div className="mt-3 border border-gray-300 rounded-lg p-3">
                <SaveSummaryBanner
                  total={saveSummary.total}
                  created={saveSummary.created}
                  updated={saveSummary.updated}
                  name="backlog"
                  navigateToNewAction={navigateToNewBacklog}
                  navigateToConsultationSpace={navigateToConsultationSpace}
                />
              </div>
            </section>
          </div>
        )}
      </div>
      <Dialog
        open={showRegenerateDialog}
        onOpenChange={open => { if (!open) setShowRegenerateDialog(false); }}
      >
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>Regenerate tasks?</DialogTitle>
            <DialogDescription>
              You have already started the task generation process. Regenerating will{' '}
              <strong>reset all current progress</strong> — generated and verified tasks will
              be cleared — and the process will restart from scratch. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex flex-col-reverse sm:flex-row gap-2">
            <Button
              variant="outline"
              onClick={() => setShowRegenerateDialog(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                setShowRegenerateDialog(false);
                handleGenerate();
              }}
            >
              Yes, regenerate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={showSpaceChangeDialog}
        onOpenChange={open => { if (!open) { setShowSpaceChangeDialog(false); setPendingSpaceId(null); } }}
      >
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>Change ClickUp space?</DialogTitle>
            <DialogDescription>
              You have already started the task generation process. Switching to a different
              space will <strong>reset all current progress</strong> — generated and verified
              tasks will be cleared — and generation will restart automatically with the new
              space. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex flex-col-reverse sm:flex-row gap-2">
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
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
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
          <DialogFooter className="flex flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setAssigneeDialog({ open: false })}>No</Button>
            <Button onClick={handleIgnoreNames}>Yes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={assigneeDialog.open && assigneeDialog.type === 'mails'}
        onOpenChange={open => { if (!open) setAssigneeDialog({ open: false }); }}
      >
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
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
          <DialogFooter className="flex flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setAssigneeDialog({ open: false })}>No</Button>
            <Button onClick={handleIgnoreMails}>Yes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {showSpaceSetup && createPortal(
        <SpaceSetupForm
          isOpen={showSpaceSetup}
          onClose={() => {
            setShowSpaceSetup(false)
          }}
          onSuccess={space => {
            if(hasStarted){
              resetProcess();
              shouldAutoGenerate.current = true;
            }
            setIsNewSpace(false);
        
            if (space.space_code) setSelectedSpaceId(space.space_code);
            setPendingSpaceId(null);
          }}
        />,
        document.body
      )}

    </div>
  );
}
