import { useState, useEffect } from 'react';
import type {
  AssociateClickUpSpaceRequest,
  ClickUpSpaceLightDTO,
  GitRepoCreateDTO,
  GitRepoDetailDTO,
  GitRepoUpdateDTO,
  MemberDTO,
  RepoClickUpSpaceDTO,
  RepoClickUpSpaceRefDTO,
  RepoMemberDTO,
  RepoMemberRefDTO,
} from '@/api/api';
import { Button } from '@/components/ui/shared-primitives/button';
import { Label } from '@/components/ui/shared-primitives/label';
import { Card } from '@/components/ui/shared-primitives/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/shared-primitives/select';
import { Badge } from '@/components/ui/shared-primitives/badge';
import { X, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

interface RepoEditModalNewProps {
  repo: GitRepoDetailDTO | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (repo: GitRepoCreateDTO) => Promise<boolean>;
  onUpdate: (repo: GitRepoUpdateDTO) => Promise<boolean>;
  clickUpSpaces: ClickUpSpaceLightDTO[];
  availableMembers: MemberDTO[];
  onAssociate: (association: AssociateClickUpSpaceRequest) => Promise<boolean>;
}

export function RepoEditModalNew({
  repo,
  isOpen,
  onClose,
  onSave,
  onUpdate,
  clickUpSpaces,
  availableMembers,
  onAssociate,
}: RepoEditModalNewProps) {
  const [isSaving, setIsSaving] = useState(false);
  const initialFormData: GitRepoDetailDTO = {
    id: 0,
    name: '',
    url: '',
    members: [],
    clickup_space: null,
  };
  const [formData, setFormData] = useState<GitRepoDetailDTO>(repo || initialFormData);

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
  }`;

  useEffect(() => {
    if (isOpen) {
      setIsSaving(false);
      if (repo) {
        setFormData(repo);
      } else {
        setFormData(initialFormData);
      }
    }
  }, [isOpen, repo]);

  const [membersToRemove, setMembersToRemove] = useState<RepoMemberDTO[]>([]);
  const [newMembers, setNewMembers] = useState<RepoMemberDTO[]>([]);
  const [showAddMembersPanel, setShowAddMembersPanel] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const clickupOptions = clickUpSpaces.filter(
    (space): space is ClickUpSpaceLightDTO & { id: number } => typeof space.id === 'number' && space.repo === null,
  );
  useEffect(() => {
    if (!isOpen) {
      setErrors({});
    }
  }, [isOpen]);

  useEffect(() => {
    if (repo) {
      const repoNameChanged = formData.name !== repo.name;
      const repoUrlChanged = formData.url !== repo.url;
      const spaceChanged = formData.clickup_space?.id !== repo.clickup_space?.id;
      const membersChanged = membersToRemove.length > 0 || newMembers.length > 0;
      setHasChanges(repoNameChanged || repoUrlChanged || spaceChanged || membersChanged);
    }
  }, [formData, membersToRemove, newMembers, repo]);

  const isCancelDisabled = isSaving;
  const isSaveDisabled = isSaving;


  const validateForm = () => {
    setErrors({});

    const newErrors: Record<string, string> = {};

    if (repo && !hasChanges) {
      setErrors({ form: 'No changes to update' });
      return false;
    }

    if (!formData.name && !formData.name?.trim()) {
      newErrors.name = 'Repository name is required';
    }

    if (!formData.url && !formData.url?.trim()) {
      newErrors.url = 'Repository URL is required';
    } else if (!formData.url.includes('github.com')) {
      newErrors.url = 'Must be a valid GitHub URL';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleSpaceChange = (spaceId: string) => {
    if (spaceId === 'none') {
      setFormData((prev) => ({
        ...prev,
        clickup_space: null,
      }));
    } else {
      const selectedSpace = clickUpSpaces.find((space) => space.id?.toString() === spaceId);
      setFormData((prev) => ({
        ...prev,
        clickup_space: selectedSpace
          ? ({
              id: selectedSpace.id ?? null,
              name: selectedSpace.name ?? null,
              space_code: selectedSpace.space_code ?? null,
            } as RepoClickUpSpaceDTO)
          : null,
      }));
    }
  };

  const memberKey = (member: RepoMemberDTO) =>
    member.id ?? member.mail ?? member.username ?? '';

  const toRepoMember = (member: MemberDTO): RepoMemberDTO => ({
    id: member.id,
    username: member.username,
    arabic_name: member.arabic_name,
    mail: member.mail,
  });

  const handleAddMemberToRemove = (member: RepoMemberDTO) => {
    if (!membersToRemove.find((m) => memberKey(m) === memberKey(member))) {
      setMembersToRemove([...membersToRemove, member]);
    }
  };

  const handleRemoveMemberFromRemove = (memberId: string | number) => {
    setMembersToRemove((prev) => prev.filter((m) => memberKey(m) !== memberId));
  };

  const handleAddNewMember = (member: MemberDTO) => {
    const nextMember = toRepoMember(member);
    if (!newMembers.find((m) => memberKey(m) === memberKey(nextMember))) {
      setNewMembers([...newMembers, nextMember]);
    }
  };

  const handleRemoveNewMember = (memberId: string | number) => {
    setNewMembers((prev) => prev.filter((m) => memberKey(m) !== memberId));
  };

  const handleSaveOrUpdate = async () => {
    if (!validateForm()) 
      return;

    const originalMembers = repo?.members || [];
    const filteredMembers = originalMembers.filter((member) =>
      !membersToRemove.find((memberToRemove) => memberKey(memberToRemove) === memberKey(member))
    );
    const allMembers = [
      ...filteredMembers,
      ...newMembers.filter((newM) => !filteredMembers.find((m) => memberKey(m) === memberKey(newM)))
    ];

    const updatedRepo: GitRepoDetailDTO = {
      ...formData,
      members: allMembers,
    };

    setIsSaving(true);
    try {
      let success = false;
      if(repo){
        const members: RepoMemberRefDTO[] | null = updatedRepo.members
          ? updatedRepo.members.map((member) => ({
          id: member.id ?? undefined,
          mail: member.mail ?? undefined,
        }))
        : null;
              
        const clickupSpace: RepoClickUpSpaceRefDTO | null = updatedRepo.clickup_space
          ? {
          id: updatedRepo.clickup_space.id ?? undefined,
          space_code: updatedRepo.clickup_space.space_code ?? undefined,
        }
        : null;
        success = await onUpdate({
          id: updatedRepo.id,
          name: updatedRepo.name ?? null,
          url: updatedRepo.url ?? null,
          members: members,
          clickup_space: clickupSpace,
        } as GitRepoUpdateDTO);
      }else{
        success = await onSave({
          name: updatedRepo.name ?? null,
          url: updatedRepo.url ?? null,
        } as GitRepoCreateDTO);
      }
      if(success && formData.clickup_space && !repo){
        const payload: AssociateClickUpSpaceRequest = {
          space_code: formData.clickup_space.space_code!,
          repo_url: formData.url!,
        };
        success = await onAssociate(payload);
      }
      if (success) {
        onClose();
      }
      
    } finally {
      setIsSaving(false);
    }
  };

  const repoMembers = repo?.members ?? [];
  const availableToAdd = availableMembers.filter((member) => {
    const memberId = member.id ?? member.mail ?? member.username;
    return (
      !repoMembers.find((repoMember) => memberKey(repoMember) === memberId) &&
      !newMembers.find((newMember) => memberKey(newMember) === memberId)
    );
  });

  if (!isOpen) 
    return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl border-border shadow-2xl max-h-[90vh] flex flex-col">
        <div className="sticky top-0 bg-card border-b border-border px-8 py-6 z-10">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-foreground">
                {repo ? 'Edit Repository' : 'Add New Repository'}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                {repo
                  ? 'Update repository details, members, and ClickUp space assignment'
                  : 'Create a new GitHub repository entry with team members'}
              </p>
            </div>
            <button
              onClick={() => {
                if (isCancelDisabled) return;
                setErrors({});
                onClose();
                setShowAddMembersPanel(!showAddMembersPanel)
              }}
              disabled={isCancelDisabled}
              className="p-2 hover:bg-muted rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Close"
            >
              <X className="w-5 h-5 text-muted-foreground" />
            </button>
          </div>
        </div>

        <div className="px-8 py-6 space-y-8 flex-1 overflow-y-auto">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
              <div className="w-1 h-6 bg-primary rounded-full" />
              Repository Information
            </h3>

            <div className="space-y-3">
              <div>
                <Label htmlFor="name" className="text-foreground font-medium">
                  Repository Name
                </Label>
                <input
                  id="name"
                  name="name"
                  value={formData.name || ''}
                  onChange={handleInputChange}
                  placeholder="e.g., next-commerce"
                  className={inputClass(!!errors.name) + ' mt-2'}
                  disabled={isSaving}
                />
                {errors.name && (
                  <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.name}
                  </div>
                )}
              </div>

              <div>
                <Label htmlFor="url" className="text-foreground font-medium">
                  Repository URL
                </Label>
                <input
                  id="url"
                  name="url"
                  value={formData.url || ''}
                  onChange={handleInputChange}
                  placeholder="https://github.com/user/repo"
                  className={inputClass(!!errors.url) + ' mt-2'}
                  disabled={isSaving}
                />
                {errors.url && (
                  <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.url}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
              <div className="w-1 h-6 bg-accent rounded-full" />
              ClickUp Space Assignment
            </h3>

            <div>
              <Label htmlFor="space" className="text-foreground font-medium">
                Select Space (Optional)
              </Label>
              <Select
                value={formData.clickup_space?.id?.toString() || 'none'}
                onValueChange={handleSpaceChange}
                disabled={isSaving}
              >
                <SelectTrigger className="mt-2 bg-input border-border text-foreground">
                  <SelectValue placeholder="No click up space selected" />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {clickUpSpaces.length === 0 ? (
                    <SelectItem value="none" disabled>
                      No ClickUp space available
                    </SelectItem>
                  ) : clickupOptions.length === 0 ? (
                    <SelectItem value="none" disabled>
                      No ClickUp space available for association (all are already linked)
                    </SelectItem>
                  ) : (
                    <>
                      <SelectItem value="none" className="text-muted-foreground hidden" disabled>
                        <span className="text-muted-foreground">No ClickUp space selected</span>
                      </SelectItem>
                      {clickupOptions.map((space) => (
                        <SelectItem
                          key={space.id ?? space.space_code ?? space.name}
                          value={space.id?.toString() ?? ''}
                        >
                          <div className="flex items-center gap-2">
                            {space.name}
                          </div>
                        </SelectItem>
                      ))}
                    </>
                  )}
                </SelectContent>
              </Select>

              {formData.clickup_space && (
                <div className="mt-3 p-3 border border-secondary rounded-lg">
                  <div className="flex items-center gap-2">
                    <p className="text-sm text-foreground font-medium">
                      <CheckCircle2 className="w-4 h-4 inline mr-2 text-green-600" />
                      Assigned to: <span className="font-bold">{formData.clickup_space.name}</span>
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
              <div className="w-1 h-6 bg-blue-500 rounded-full" />
              Team Members Management
            </h3>

            {(repo?.members && repo.members.length > 0) && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-foreground font-semibold text-sm">Current Members</Label>
                  <span className="text-xs text-muted-foreground">
                    {repo.members.length} total
                  </span>
                </div>
                <div className="p-4 rounded-lg border border-amber-500/30 bg-amber-500/5 space-y-3">
                  <p className="text-xs text-amber-700 bg-amber-100/50 p-2 rounded flex items-center gap-2">
                    <span className="font-bold">Tip:</span> Click a member badge to mark it for removal
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {repo.members.map((member) => {
                      const isMarkedForRemoval = membersToRemove.find((m) => memberKey(m) === memberKey(member));
                      return (
                        <Badge
                          key={memberKey(member)}
                          className={`px-3 py-1.5 text-sm cursor-pointer transition-all ${
                            isMarkedForRemoval
                              ? 'bg-red-600 text-white border-red-600'
                              : 'bg-slate-500 text-white border-slate-500 hover:bg-slate-600'
                          } ${isSaving ? 'pointer-events-none opacity-60' : ''}`}
                          onClick={() => {
                            if (isSaving) return;
                            isMarkedForRemoval
                              ? handleRemoveMemberFromRemove(memberKey(member))
                              : handleAddMemberToRemove(member);
                          }}
                        >
                          {member.username}
                        </Badge>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {membersToRemove.length > 0 && (
              <div className="space-y-3 p-4 rounded-lg border border-red-500/50 bg-red-500/10">
                <div className="flex items-center gap-2">
                  <div className="w-1 h-5 bg-red-500 rounded-full" />
                  <Label className="text-foreground font-semibold text-sm">
                    Members to Remove ({membersToRemove.length})
                  </Label>
                </div>
                <div className="flex flex-wrap gap-2">
                  {membersToRemove.map((member) => (
                    <Badge
                      key={memberKey(member)}
                      className="gap-2 px-3 py-1.5 text-sm bg-red-600 text-white"
                    >
                      {member.username}
                      <button
                        type="button"
                        onClick={() => handleRemoveMemberFromRemove(memberKey(member))}
                        disabled={isSaving}
                        className="hover:opacity-70 transition-opacity disabled:opacity-40"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
                <p className="text-xs text-red-700 bg-red-100/50 p-2 rounded">
                  These members will be removed when you click "Update Repository"
                </p>
              </div>
            )}

            <div>
              <Button
                type="button"
                variant={showAddMembersPanel ? 'default' : 'outline'}
                onClick={() => setShowAddMembersPanel(!showAddMembersPanel)}
                className="w-full border-border gap-2 mb-4"
                disabled={isSaving}
              >
                {showAddMembersPanel ? 'Close' : '+ Add Members'}
              </Button>
              {showAddMembersPanel && (
                <div className="space-y-4 p-4 rounded-lg border border-primary/50 bg-primary/5">
                  <div className="flex items-center gap-2">
                    <div className="w-1 h-5 bg-primary rounded-full" />
                    <Label className="text-foreground font-semibold">Select Members to Add</Label>
                  </div>

                  <div>
                    <Label className="text-sm text-muted-foreground">All Available Members</Label>
                    <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {availableToAdd.map((member) => (
                        <button
                          key={member.id ?? member.mail ?? member.username}
                          type="button"
                          onClick={() => handleAddNewMember(member)}
                          disabled={isSaving}
                          className="p-3 rounded-lg border-2 border-border hover:border-primary/50 bg-muted/50 hover:bg-primary/5 text-left transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <p className="font-medium text-foreground text-sm">{member.username}</p>
                          <p className="text-xs text-muted-foreground">{member.mail || 'No email'}</p>
                        </button>
                      ))}
                    </div>
                    {availableToAdd.length === 0 && (
                      <p className="text-sm text-muted-foreground italic mt-3">
                        All members are already added
                      </p>
                    )}
                  </div>

                  {newMembers.length > 0 && (
                    <div className="p-3 bg-green-500/10 rounded-lg border border-green-500/30">
                      <p className="text-sm font-medium text-foreground mb-2">
                        Members to be added ({newMembers.length})
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {newMembers.map((member) => (
                          <Badge
                            key={memberKey(member)}
                            className="gap-2 px-3 py-1.5 text-sm bg-green-600 text-white"
                          >
                            {member.username}
                            <button
                              type="button"
                              onClick={() => handleRemoveNewMember(memberKey(member))}
                              disabled={isSaving}
                              className="hover:opacity-70 transition-opacity disabled:opacity-40"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="sticky bottom-0 bg-card border-t border-border px-8 py-4 flex items-center justify-between z-10">
          {errors.form ? (
            <div className="text-destructive text-sm">{errors.form}</div>
          ) : <div />}
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => onClose()}
              className="border-border"
              disabled={isCancelDisabled}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSaveOrUpdate}
              disabled={isSaveDisabled}
              className="gap-2"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  {repo ? 'Update' : 'Save'} Repository
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}