import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import type { MemberCreateDTO, MemberDTO, MemberUpdateDTO } from '@/api/api';
import { Button } from '@/components/ui/button';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import { MemberEditModal } from './member-edit-model-new';

export interface MembersTableProps {
  members: MemberDTO[];
  onUpdate: (member: MemberUpdateDTO) => Promise<boolean>;
  onDelete: (id: number) => void;
  onAdd: (member: MemberCreateDTO) => Promise<boolean>;
  isLoading?: boolean;
}

export function MembersTable({ members, onUpdate, onDelete, onAdd, isLoading }: MembersTableProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMember, setEditingMember] = useState<MemberDTO | null>(null);
  const [deleteConfirmMemberId, setDeleteConfirmMemberId] = useState<number | null>(null);

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

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">Members Management</h2>
        <Button onClick={handleAddClick} className="gap-2">
          <Plus className="w-4 h-4" />
          Add Member
        </Button>
      </div>

      <div className="hidden sm:block overflow-x-auto border border-border rounded-lg">
        {isLoading ? (
          <table className="w-full">
            <tbody>
              {Array.from({ length: 4 }).map((_, i) => (
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
                    <div className="flex justify-end gap-2">
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted">
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Member</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Mail</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Arabic Name</th>
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
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center">
                    <p className="text-muted-foreground">No members yet. Create your first member!</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      <div className="sm:hidden space-y-3">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-lg border border-border p-4 space-y-2 animate-pulse">
              <div className="h-4 w-32 bg-muted rounded" />
              <div className="h-3 w-40 bg-muted rounded" />
              <div className="h-3 w-28 bg-muted rounded" />
            </div>
          ))
        ) : members.length > 0 ? (
          members.map((member) => (
            <div
              key={member.id}
              className="rounded-lg border border-border p-4 bg-card flex items-center justify-between"
            >
              <div>
                <p className="font-medium text-foreground">{member.username}</p>
                <p className="text-xs text-muted-foreground">{member.mail || 'N/A'}</p>
                <p className="text-xs text-muted-foreground" dir="rtl">
                  {member.arabic_name || 'N/A'}
                </p>
              </div>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleEditClick(member)}
                  className="h-8 w-8"
                >
                  <Edit2 className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => typeof member.id === 'number' && setDeleteConfirmMemberId(member.id)}
                  className="h-8 w-8 text-destructive hover:bg-destructive/10"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
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
        onUpdate={onUpdate}
      />

      <Dialog
        open={deleteConfirmMemberId !== null}
        onOpenChange={(open) => { if (!open) setDeleteConfirmMemberId(null); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Are you sure you want to delete this member?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. The member will be permanently deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmMemberId(null)}>No</Button>
            <Button
              variant="destructive"
              onClick={async () => {
                if (deleteConfirmMemberId !== null) {
                  await onDelete(deleteConfirmMemberId);
                  setDeleteConfirmMemberId(null);
                }
              }}
            >
              Yes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}