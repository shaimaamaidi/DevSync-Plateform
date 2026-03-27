import { useState, useEffect } from 'react';
import type {
  ClickUpSpaceLightDTO,
  GitRepoDetailDTO,
  MemberDTO,
  RepoClickUpSpaceDTO,
  RepoMemberDTO,
} from '@/api/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { X, AlertCircle, CheckCircle2 } from 'lucide-react';

interface RepoEditModalNewProps {
  repo: GitRepoDetailDTO | null;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (repo: GitRepoDetailDTO) => void;
  clickUpSpaces: ClickUpSpaceLightDTO[];
  availableMembers: MemberDTO[];
}

export function RepoEditModalNew({
  repo,
  isOpen,
  onOpenChange,
  onSave,
  clickUpSpaces,
  availableMembers,
}: RepoEditModalNewProps) {
  const [formData, setFormData] = useState<GitRepoDetailDTO>(
    repo || {
      id: undefined,
      name: '',
      url: '',
      members: [],
      clickup_space: null,
    }
  );
  const [membersToRemove, setMembersToRemove] = useState<RepoMemberDTO[]>([]);
  const [newMembers, setNewMembers] = useState<RepoMemberDTO[]>([]);
  const [showAddMembersPanel, setShowAddMembersPanel] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (repo) {
      const repoNameChanged = formData.name !== repo.name;
      const repoUrlChanged = formData.url !== repo.url;
      const spaceChanged = formData.clickup_space?.id !== repo.clickup_space?.id;
      const membersChanged = membersToRemove.length > 0 || newMembers.length > 0;

      setHasChanges(repoNameChanged || repoUrlChanged || spaceChanged || membersChanged);
    }
  }, [formData, membersToRemove, newMembers, repo]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Repository name is required';
    }

    if (!formData.url?.trim()) {
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
    id: member.id ?? null,
    username: member.username ?? null,
    mail: member.mail ?? null,
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

  const handleSave = () => {
    if (!validateForm()) return;

    // Calculate final members list: remove membersToRemove and add newMembers
    const originalMembers = repo?.members || [];
    const finalMembers = [
      ...originalMembers.filter((member) =>
        !membersToRemove.find((memberToRemove) => memberKey(memberToRemove) === memberKey(member))
      ),
      ...newMembers,
    ];

    const updatedRepo: GitRepoDetailDTO = {
      ...formData,
      members: finalMembers,
    };

    onSave(updatedRepo);
    onOpenChange(false);
    setMembersToRemove([]);
    setNewMembers([]);
    setShowAddMembersPanel(false);
  };

  const repoMembers = repo?.members ?? [];
  const availableToAdd = availableMembers.filter((member) => {
    const memberId = member.id ?? member.mail ?? member.username;
    return (
      !repoMembers.find((repoMember) => memberKey(repoMember) === memberId) &&
      !newMembers.find((newMember) => memberKey(newMember) === memberId)
    );
  });

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-border shadow-2xl max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-card border-b border-border px-8 py-6">
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
                onClick={() => onOpenChange(false)}
                className="p-2 hover:bg-muted rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-8 py-6 space-y-8">
            {/* Repository Information */}
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
                  <Input
                    id="name"
                    name="name"
                    value={formData.name || ''}
                    onChange={handleInputChange}
                    placeholder="e.g., next-commerce"
                    className={`mt-2 bg-input border-border text-foreground ${
                      errors.name ? 'border-destructive' : ''
                    }`}
                  />
                  {errors.name && (
                    <p className="text-sm text-destructive mt-1 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.name}
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="url" className="text-foreground font-medium">
                    Repository URL
                  </Label>
                  <Input
                    id="url"
                    name="url"
                    value={formData.url || ''}
                    onChange={handleInputChange}
                    placeholder="https://github.com/user/repo"
                    className={`mt-2 bg-input border-border text-foreground ${
                      errors.url ? 'border-destructive' : ''
                    }`}
                  />
                  {errors.url && (
                    <p className="text-sm text-destructive mt-1 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.url}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* ClickUp Space Assignment */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <div className="w-1 h-6 bg-accent rounded-full" />
                ClickUp Space Assignment
              </h3>

              <div>
                <Label htmlFor="space" className="text-foreground font-medium">
                  Select Space (Optional)
                </Label>
                <Select value={formData.clickup_space?.id?.toString() || 'none'} onValueChange={handleSpaceChange}>
                  <SelectTrigger className="mt-2 bg-input border-border text-foreground">
                    <SelectValue placeholder="Assign to a ClickUp space..." />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    <SelectItem value="none">
                      <span className="text-muted-foreground">None</span>
                    </SelectItem>
                    {clickUpSpaces.map((space) => (
                      <SelectItem
                        key={space.id ?? space.space_code ?? space.name}
                        value={space.id?.toString() ?? ''}
                      >
                        <div className="flex items-center gap-2">
                          {space.name}
                        </div>
                      </SelectItem>
                    ))}
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

            {/* Team Members */}
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <div className="w-1 h-6 bg-blue-500 rounded-full" />
                Team Members Management
              </h3>

              {/* Original Members - Fixed List */}
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
                            }`}
                            onClick={() =>
                              isMarkedForRemoval
                                ? handleRemoveMemberFromRemove(memberKey(member))
                                : handleAddMemberToRemove(member)
                            }
                          >
                            {member.username}
                          </Badge>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* Members To Remove Section */}
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
                          className="hover:opacity-70 transition-opacity"
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

              {/* Add Members Button */}
              <div>
                <Button
                  type="button"
                  variant={showAddMembersPanel ? 'default' : 'outline'}
                  onClick={() => setShowAddMembersPanel(!showAddMembersPanel)}
                  className="w-full border-border gap-2"
                >
                  {showAddMembersPanel ? 'Close' : '+ Add Members'}
                </Button>
              </div>

              {/* Add Members Panel */}
              {showAddMembersPanel && (
                <div className="space-y-4 p-4 rounded-lg border border-primary/50 bg-primary/5">
                  <div className="flex items-center gap-2">
                    <div className="w-1 h-5 bg-primary rounded-full" />
                    <Label className="text-foreground font-semibold">Select Members to Add</Label>
                  </div>

                  {/* Available Members Dropdown */}
                  <div>
                    <Label className="text-sm text-muted-foreground">All Available Members</Label>
                    <div className="mt-3 grid grid-cols-2 gap-2">
                      {availableToAdd.map((member) => (
                        <button
                          key={member.id ?? member.mail ?? member.username}
                          type="button"
                          onClick={() => handleAddNewMember(member)}
                          className="p-3 rounded-lg border-2 border-border hover:border-primary/50 bg-muted/50 hover:bg-primary/5 text-left transition-all"
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

                  {/* Selected New Members */}
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
                              className="hover:opacity-70 transition-opacity"
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

          {/* Footer */}
          <div className="sticky bottom-0 bg-card border-t border-border px-8 py-4 flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {hasChanges && (
                <span className="flex items-center gap-2 text-primary">
                  <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  Unsaved changes
                </span>
              )}
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="border-border"
              >
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={!hasChanges && !!repo}
                className="gap-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                {repo ? 'Update' : 'Create'} Repository
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}
