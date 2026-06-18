import { useCallback, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/shared-primitives/dialog';
import { 
  ClickUpMemberRole, 
  type MemberCreateDTO, 
  type MemberDTO, 
  type MemberUpdateDTO 
} from '@/api/api';
import { Button } from '@/components/ui/shared-primitives/button';
import { Plus, Edit2, Trash2, AlertCircle, Database, Loader2, Link2Off } from 'lucide-react';
import { MemberEditModal } from './ui/member-edit-model-new';
import { useCurrentUser } from '@/hooks/current-user-hooks/use-current-user';
import { showSuccessToast } from './global-toaster';
import { clickUpStructureManagementService } from '@/services/clickup-workspace-management-service';
import { extractErrorCode, extractStatusCode, normalizeErrorMessage, resolveErrorAction } from '@/utils/error-handler';
import { defaultOnError } from '@/services/api-error';
import { useNavigate } from 'react-router-dom';

export interface MembersTableProps {
  members: MemberDTO[];
  onUpdate: (member: MemberUpdateDTO) => Promise<boolean>;
  onDelete: (id: number) => void;
  onAdd: (member: MemberCreateDTO) => Promise<boolean>;
  onInviteToClickUp: (email: string, role: ClickUpMemberRole) => Promise<boolean>;
  isLoading?: boolean;
  error?: string | null;
  refetchMembers?: () => void;
}

export interface RemoveFromClickUpResult {
  success: boolean;
  softErrorCode?: string;
  softErrorMessage?: string;
}

const CLICKUP_SOFT_ERROR_CODES = ['MEMBER_NOT_FOUND', 'CLICKUP_PLAN_RESTRICTION'];

export function MembersTable({ 
  members, 
  onUpdate, 
  onDelete, 
  onAdd, 
  onInviteToClickUp, 
  isLoading,
  error,
  refetchMembers
}: MembersTableProps) {
  const { user: currentUser } = useCurrentUser();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMember, setEditingMember] = useState<MemberDTO | null>(null);
  const [deleteConfirmMemberId, setDeleteConfirmMemberId] = useState<number | null>(null);

  const [inviteToClickUpMemberDialog, setInviteToClickUpMemberDialog] = useState(false);
  const [memeberMail, setMemberMail] = useState<string | null>(null);
  const [roleDialogOpen, setRoleDialogOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<ClickUpMemberRole>(ClickUpMemberRole.NUMBER_4);
  const [deleteFromDBConfirmId, setDeleteFromDBConfirmId] = useState<number | null>(null);

  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);
  
  const [clickUpRemovalInfo, setClickUpRemovalInfo] = useState<string | null>(null);
  const [isRemovingFromClickUp, setIsRemovingFromClickUp] = useState(false);

  const handleAddClick = () => {
    setEditingMember(null);
    setIsModalOpen(true);
  };

  const handleEditClick = (member: MemberDTO) => {
    setEditingMember(member);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingMember(null);
  };

  const handleAddSuccess = async (member: MemberCreateDTO): Promise<void> => {
    setMemberMail(member?.mail ?? null);
    setInviteToClickUpMemberDialog(true);
  };
  
  const handleRemoveMemberFromClickUp = useCallback(
    
    async (memberId: number): Promise<RemoveFromClickUpResult> => {
      try {
        await clickUpStructureManagementService.removeMemberFromWorkspace(memberId);
        showSuccessToast('Member removed from ClickUp successfully');
        return { success: true };
      } catch (err) {
        const code = extractErrorCode(err);

        if (code && CLICKUP_SOFT_ERROR_CODES.includes(code)) {
          return {
            success: false,
            softErrorCode: code,
            softErrorMessage: normalizeErrorMessage(err),
          };
        }

        const action = resolveErrorAction(err);
        const message = normalizeErrorMessage(err);
        const status = extractStatusCode(err);
        await onError()(action, message, { code, status: status ?? undefined });
        return { success: false };
      }
    },
    [onError],
  );

  const handleRemoveFromClickUp = async () => {
    if (deleteConfirmMemberId === null) return;
    const memberId = deleteConfirmMemberId;

    setIsRemovingFromClickUp(true);
    const result = await handleRemoveMemberFromClickUp(memberId);
    setIsRemovingFromClickUp(false);
    setDeleteConfirmMemberId(null);

    if (result.success) {
      setClickUpRemovalInfo(null);
      setDeleteFromDBConfirmId(memberId);
      return;
    }

    if (result.softErrorCode) {
      setClickUpRemovalInfo(
        result.softErrorMessage ?? "This member could not be removed from ClickUp.",
      );
      setDeleteFromDBConfirmId(memberId);
    }
  };

  const handleDeleteFromDBDirectly = () => {
    if (deleteConfirmMemberId === null) return;
    setDeleteFromDBConfirmId(deleteConfirmMemberId);
    setClickUpRemovalInfo(null);
    setDeleteConfirmMemberId(null);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap justify-between gap-2">
        <h2 className="text-xl sm:text-2xl font-bold text-foreground">Members Management</h2>
        <Button onClick={handleAddClick} className="gap-2 shrink-0">
          <Plus className="w-4 h-4" />
          Add Member
        </Button>
      </div>

      <div className="hidden sm:block overflow-x-auto overflow-y-auto max-h-[480px] border border-border rounded-lg">
        {isLoading ? (
          <table className="w-full min-w-[560px]">
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b border-border">
                  <td className="px-6 py-4">
                    <div className="h-4 w-32 rounded bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-48 rounded bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-36 rounded bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-16 rounded bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-2">
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : error ? (
          <table className="w-full min-w-[560px]">
            <tbody>
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <div className="flex items-center gap-2 text-destructive text-sm">
                      <AlertCircle className="w-4 h-4" />
                      Failed to load members.
                    </div>
                    <button onClick={() => refetchMembers?.()}
                      className="text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground transition">
                      Try again
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        ) : (
          <table className="w-full min-w-[560px]">
            <thead className="sticky top-0 z-10">
              <tr className="border-b border-border bg-muted">
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Member</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Mail</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Arabic Name</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Role</th>
                <th className="px-10 py-4 text-right text-sm font-semibold text-foreground">Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.length > 0 ? (
                members.map((member) => (
                  <tr
                    key={member.id}
                    className="border-b border-border hover:bg-muted/50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <span className="font-medium text-foreground w-full text-center block">
                        {member.username}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-sm text-muted-foreground">{member.mail || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-4 text-center" dir="rtl">
                      <span className="text-sm text-muted-foreground">
                        {member.arabic_name || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-sm text-muted-foreground capitalize">{member.role || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEditClick(member)}
                          className="h-8 w-8"
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        {currentUser?.id !== member.id && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => {
                              if (typeof member.id === 'number') {
                                setDeleteConfirmMemberId(member.id);
                              }
                            }}
                            className="h-8 w-8 text-destructive hover:bg-destructive/10"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <p className="text-muted-foreground">No members yet. Create your first member!</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      <div className="sm:hidden space-y-3 max-h-[60vh] overflow-y-auto overflow-x-auto pr-1 max-w-full">
        {isLoading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="rounded-lg border border-border p-4 space-y-2 animate-pulse">
              <div className="h-4 w-32 bg-muted rounded" />
              <div className="h-3 w-40 bg-muted rounded" />
              <div className="h-3 w-28 bg-muted rounded" />
              <div className="h-3 w-36 bg-muted rounded" />
            </div>
          ))
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <div className="flex items-center gap-2 text-destructive text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              Failed to load members.
            </div>
            <button
              onClick={() => refetchMembers?.()}
              className="text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground transition"
            >
              Try again
            </button>
          </div>
        ) : members.length > 0 ? (
          members.map((member) => (
            <div
              key={member.id}
              className="rounded-lg border border-border p-4 bg-card flex items-center justify-between gap-2"
            >
              <div className="min-w-0 flex-1">
                <p className="font-medium text-foreground truncate">{member.username}</p>
                <p className="text-xs text-muted-foreground">{member.mail || 'N/A'}</p>
                <p className="text-xs text-muted-foreground" dir="rtl">
                  {member.arabic_name || 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground capitalize">{member.role || 'N/A'}</p>
              </div>
              <div className="flex gap-1 shink-0">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleEditClick(member)}
                  className="h-8 w-8"
                >
                  <Edit2 className="w-4 h-4" />
                </Button>
                {currentUser?.id !== member.id && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => typeof member.id === 'number' && setDeleteConfirmMemberId(member.id)}
                    className="h-8 w-8 text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-muted-foreground py-8">
            No members yet. Create your first member!
          </p>
        )}
      </div>

      <MemberEditModal
        isOpen={isModalOpen}
        editingMember={editingMember}
        onClose={handleModalClose}
        onAdd={onAdd}
        handleAddSuccess={handleAddSuccess}
        onUpdate={onUpdate}
      />

      <Dialog
        open={deleteConfirmMemberId !== null}
        onOpenChange={(open) => { if (!open && !isRemovingFromClickUp) setDeleteConfirmMemberId(null); }}
      >
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>Remove this member</DialogTitle>
            <DialogDescription>Choose how you want to remove them.</DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-2 gap-2 py-2">
            <button
              type="button"
              disabled={isRemovingFromClickUp}
              onClick={handleDeleteFromDBDirectly}
              className="flex flex-col items-center gap-1.5 rounded-lg border p-3 text-sm transition-colors cursor-pointer border-border bg-muted/40 text-muted-foreground hover:bg-muted/80 hover:border-foreground/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Database className="w-5 h-5" />
              <span className="font-medium text-foreground">Database</span>
              <span className="text-xs text-center leading-snug opacity-70">
                Deletes only from the database.
              </span>
            </button>

            <button
              type="button"
              disabled={isRemovingFromClickUp}
              onClick={handleRemoveFromClickUp}
              className="flex flex-col items-center gap-1.5 rounded-lg border p-3 text-sm transition-colors cursor-pointer border-border bg-muted/40 text-muted-foreground hover:bg-muted/80 hover:border-foreground/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRemovingFromClickUp ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Link2Off className="w-5 h-5" />
              )}
              <span className="font-medium text-foreground">ClickUp</span>
              <span className="text-xs text-center leading-snug opacity-70">
                Remove the member from ClickUp then from the database.
              </span>
            </button>
          </div>

          <DialogFooter>
            <Button
              variant="ghost"
              onClick={() => setDeleteConfirmMemberId(null)}
              disabled={isRemovingFromClickUp}
              className="w-full"
            >
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={inviteToClickUpMemberDialog} onOpenChange={setInviteToClickUpMemberDialog}>
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>Invite to ClickUp?</DialogTitle>
            <DialogDescription>Member added successfully. Do you want to also invite them to ClickUp?</DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setInviteToClickUpMemberDialog(false)}>No</Button>
            <Button onClick={() => { setInviteToClickUpMemberDialog(false); setRoleDialogOpen(true); }}>Yes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={roleDialogOpen} onOpenChange={setRoleDialogOpen}>
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>Select ClickUp Role</DialogTitle>
          </DialogHeader>
          <div className="space-y-2 py-2">
            {[
              { label: 'Member', value: ClickUpMemberRole.NUMBER_4 },
              { label: 'Admin', value: ClickUpMemberRole.NUMBER_3 },
              { label: 'Owner', value: ClickUpMemberRole.NUMBER_2 },
              { label: 'Guest', value: ClickUpMemberRole.NUMBER_5 },
            ].map(r => (
              <Button
                key={r.value}
                variant={selectedRole === r.value ? 'default' : 'outline'}
                className="w-full"
                onClick={() => setSelectedRole(r.value)}
              >
                {r.label}
              </Button>
            ))}
          </div>
          <DialogFooter className="flex flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setRoleDialogOpen(false)}>Cancel</Button>
            <Button onClick={async () => {
              if (memeberMail) {
                await onInviteToClickUp(memeberMail, selectedRole);
              }
              setRoleDialogOpen(false);
              setMemberMail(null);
            }}>Invite</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={deleteFromDBConfirmId !== null}
        onOpenChange={(open) => { if (!open) { setDeleteFromDBConfirmId(null); setClickUpRemovalInfo(null); } }}
      >
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>Remove from database too?</DialogTitle>
            <DialogDescription>
              {clickUpRemovalInfo ?? "Member removed from ClickUp. Do you also want to delete them from the database?"}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={() => { setDeleteFromDBConfirmId(null); setClickUpRemovalInfo(null); }}>
              No
            </Button>
            <Button
              variant="destructive"
              onClick={async () => {
                if (deleteFromDBConfirmId !== null) {
                  await onDelete(deleteFromDBConfirmId);
                  setDeleteFromDBConfirmId(null);
                  setClickUpRemovalInfo(null);
                }
              }}
            >
              Yes, delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}