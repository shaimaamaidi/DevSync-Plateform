import { useEffect, useState } from 'react';
import type { ClickUpSpaceDTO, ClickUpSpaceRegisterDTO, CreateSpaceRequest } from '@/api/api';
import { Button } from '@/components/ui/shared-primitives/button';
import { Card } from '@/components/ui/shared-primitives/card';
import { Label } from '@/components/ui/shared-primitives/label';
import { AlertCircle, CheckCircle2, Database, Loader2, Plus, X } from 'lucide-react';
import { useClickUpSpacesList } from '@/hooks/clickup-space-hooks/use-clickup-spaces';
import { useCreateClickUpSpace } from '@/hooks/clickup-structure-hooks/use-create-space';
import { useRegisterClickUpSpace } from '@/hooks/clickup-structure-hooks/use-register-space';
import { showSuccessToast } from '../../global-toaster';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/shared-primitives/dialog';

export interface SpaceSetupFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (space: ClickUpSpaceDTO) => void;
}

type CreationMode = 'create' | 'register';

type PendingRegisterAction =
  | { type: 'not_found' }
  | { type: 'name_mismatch'; actualName: string | null };

export function SpaceSetupForm({ isOpen, onClose, onSuccess }: SpaceSetupFormProps) {
  const { spaces, loading: spacesLoading } = useClickUpSpacesList();
  const { mutateAsync: createSpace, isPending: isCreating } = useCreateClickUpSpace();
  const { mutateAsync: registerSpace, isPending: isRegistering } = useRegisterClickUpSpace();

  const isPending = isCreating || isRegistering;

  const [mode, setMode] = useState<CreationMode>('create');
  const [spaceName, setSpaceName] = useState('');
  const [spaceCode, setSpaceCode] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pendingAction, setPendingAction] = useState<PendingRegisterAction | null>(null);

  const isSaveDisabled = isPending || spacesLoading;

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  useEffect(() => {
    if (isOpen) {
      setMode('create');
      setSpaceName('');
      setSpaceCode('');
      setErrors({});
      setPendingAction(null);
    }
  }, [isOpen]);

  const handleModeChange = (newMode: CreationMode) => {
    setMode(newMode);
    setSpaceName('');
    setSpaceCode('');
    setErrors({});
  };

  const validate = (): boolean => {
    setErrors({});
    const newErrors: Record<string, string> = {};
    
    const trimmedName = spaceName.trim();
    const trimmedCode = spaceCode.trim();

    if (!trimmedName) {
      newErrors.name = 'Click up space name is required';
    } else {
      const alreadyExists = spaces.some(
        (s) => s.name?.toUpperCase() === trimmedName.toUpperCase(),
      );
      if (alreadyExists) {
        newErrors.name = `"${trimmedName}" already exists — please choose a different name`;
      }
    }

    if (mode === 'register' && !trimmedCode) {
      newErrors.code = 'Click up space ID is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) return;

    if (mode === 'create') {
      const request: CreateSpaceRequest = { space_name: spaceName.trim() };
      const result = await createSpace(request);
      if (!result) return;

      showSuccessToast('Click Up space created successfully');
      onSuccess?.(result);
      onClose();
      return;
    }

    await executeRegister(false);
  };

  const executeRegister = async (ignoreName: boolean) => {
    const request: ClickUpSpaceRegisterDTO = {
      name: spaceName.trim(),
      space_code: spaceCode.trim(),
      ignore_name: ignoreName,
    };

    const result = await registerSpace(request);

    if (result.ok) {
      showSuccessToast('Click Up space registered successfully');
      onSuccess?.(result.data);
      onClose();
      return;
    }

    if (result.reason === 'not_found') {
      setPendingAction({ type: 'not_found' });
      return;
    }

    if (result.reason === 'name_mismatch') {
      setPendingAction({ type: 'name_mismatch', actualName: result.actualName });
      return;
    }
  };

  const handleNotFoundConfirm = async () => {
    setPendingAction(null);
    const request: CreateSpaceRequest = { space_name: spaceCode.trim() };
    const result = await createSpace(request);
    if (!result) 
      return;

    showSuccessToast('Click Up space created successfully');
    onSuccess?.(result);
    onClose();
  };

  const handleNameMismatchConfirm = async () => {
    setPendingAction(null);
    await executeRegister(true);
  };

  if (!isOpen) 
    return null;

  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
        <Card className="w-full sm:max-w-[420px] border-border shadow-2xl max-h-[90vh] flex flex-col">

          <div className="flex items-center justify-between px-4 sm:px-6 pt-4 sm:pt-6 shrink-0">
            <h2 className="text-lg sm:text-xl font-bold text-foreground">Create Click Up Space</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              disabled={isPending}
              className="h-8 w-8 shrink-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          <div className="space-y-4 px-4 sm:px-6 py-4 overflow-y-auto flex-1">

            <div className="space-y-2">
              <Label className="text-foreground font-medium">Mode</Label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                <button
                  type="button"
                  disabled={isPending}
                  onClick={() => handleModeChange('create')}
                  className={`flex items-center sm:flex-col gap-3 sm:gap-1.5 rounded-lg border px-3 sm:p-3 py-2.5 text-sm transition-colors cursor-pointer text-left sm:text-center
                    ${mode === 'create'
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border bg-muted/40 text-muted-foreground hover:bg-muted/80'
                    }`}
                >
                  <Plus className="w-5 h-5 shrink-0" />
                  <span className="flex flex-col sm:items-center gap-0.5">
                    <span className="font-medium">Create &amp; Save</span>
                    <span className="text-xs leading-snug opacity-70">
                      Create in ClickUp then persist in DB
                    </span>
                  </span>
                </button>

                <button
                  type="button"
                  disabled={isPending}
                  onClick={() => handleModeChange('register')}
                  className={`flex items-center sm:flex-col gap-3 sm:gap-1.5 rounded-lg border px-3 sm:p-3 py-2.5 text-sm transition-colors cursor-pointer text-left sm:text-center
                    ${mode === 'register'
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border bg-muted/40 text-muted-foreground hover:bg-muted/80'
                    }`}
                >
                  <Database className="w-5 h-5 shrink-0" />
                  <span className="flex flex-col sm:items-center gap-0.5">
                    <span className="font-medium">Register Only</span>
                    <span className="text-xs leading-snug opacity-70">
                      Verify &amp; save existing ClickUp space
                    </span>
                  </span>
                </button>
              </div>
            </div>

            {mode === 'register' && (
              <div className="animate-in fade-in slide-in-from-top-2 duration-200">
                <Label className="text-foreground font-medium">Space ID</Label>
                <input
                  type="text"
                  placeholder="cus_prod_001"
                  value={spaceCode}
                  onChange={(e) => {
                    setSpaceCode(e.target.value);
                    setErrors((prev) => ({ ...prev, code: '' }));
                  }}
                  className={inputClass(!!errors.code) + ' mt-2'}
                  disabled={isPending}
                />
                {errors.code && (
                  <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    {errors.code}
                  </div>
                )}
              </div>
            )}

            <div>
              <Label className="text-foreground font-medium">Space Name</Label>
              <input
                type="text"
                placeholder="My ClickUp Space"
                value={spaceName}
                onChange={(e) => {
                  setSpaceName(e.target.value);
                  setErrors((prev) => ({ ...prev, name: '' }));
                }}
                className={inputClass(!!errors.name) + ' mt-2'}
                disabled={isPending}
              />
              {spaceName.trim() && !errors.name && (
                <p className="text-xs text-muted-foreground mt-1 px-1">
                  Will be {mode === 'create' ? 'created' : 'registered'} as:{' '}
                  <span className="font-semibold text-foreground">{spaceName.trim()}</span>
                </p>
              )}
              {errors.name && (
                <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  {errors.name}
                </div>
              )}
            </div>

            {spaces.length > 0 && (
              <div className="rounded-lg border border-border/60 bg-muted/30 px-3 sm:px-3.5 py-2.5">
                <p className="text-xs text-muted-foreground font-medium mb-1.5">
                  Existing spaces:
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {spaces.map((s) => (
                    <span
                      key={s.id}
                      className="text-xs bg-muted rounded px-2 py-0.5 text-foreground/70 font-mono break-all"
                    >
                      {s.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-2 px-4 sm:px-6 pb-4 sm:pb-6 pt-4 border-t border-border shrink-0">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              className="flex-1 gap-2"
              disabled={isSaveDisabled}
            >
              {isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="truncate">{mode === 'create' ? 'Creating…' : 'Registering…'}</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span className="truncate">{mode === 'create' ? 'Create Space' : 'Register Space'}</span>
                </>
              )}
            </Button>
          </div>
        </Card>
      </div>

      <Dialog
        open={pendingAction?.type === 'not_found'}
        onOpenChange={(open) => { if (!open) setPendingAction(null); }}
      >
        <DialogContent
          className="w-[calc(100%-2rem)] sm:w-full max-w-lg mx-auto"
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg leading-snug">
              Space not found in ClickUp
            </DialogTitle>
            <DialogDescription className="text-sm">
              The space <span className="font-semibold">{spaceCode}</span> does not exist in
              ClickUp yet. Would you like to create it in ClickUp and save it to the database?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setPendingAction(null)} disabled={isPending} className="w-full sm:w-auto">
              No, cancel
            </Button>
            <Button onClick={handleNotFoundConfirm} disabled={isPending} className="gap-2 w-full sm:w-auto">
              {isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              Yes, create it
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={pendingAction?.type === 'name_mismatch'}
        onOpenChange={(open) => { if (!open) setPendingAction(null); }}
      >
        <DialogContent
          className="w-[calc(100%-2rem)] sm:w-full max-w-lg mx-auto"
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg leading-snug">
              Space name mismatch
            </DialogTitle>
            <DialogDescription className="text-sm">
              The space <span className="font-semibold">{spaceCode}</span> exists in ClickUp
              but its name differs from what you entered (
              <span className="font-semibold">{spaceName}</span>
              {pendingAction?.type === 'name_mismatch' && pendingAction.actualName && (
                <> — actual name: <span className="font-semibold">{pendingAction.actualName}</span></>
              )}
              ). Would you like to register it using the real ClickUp name instead?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setPendingAction(null)} disabled={isPending} className="w-full sm:w-auto">
              No, let me correct it
            </Button>
            <Button onClick={handleNameMismatchConfirm} disabled={isPending} className="gap-2 w-full sm:w-auto">
              {isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              Yes, use real name
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}