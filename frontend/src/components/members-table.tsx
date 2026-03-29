import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import type { MemberDTO } from '@/api/api';
import { Button } from '@/components/ui/button';
import { Plus, Edit2, Trash2, X } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';


export interface MembersTableProps {
  members: MemberDTO[];
  onUpdate: (member: MemberDTO) => void;
  onDelete: (id: number) => void;
  onAdd: (member: MemberDTO) => void;
}

export function MembersTable({ members, onUpdate, onDelete, onAdd }: MembersTableProps) {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingMember, setEditingMember] = useState<MemberDTO | null>(null);
  const [formData, setFormData] = useState<Partial<MemberDTO>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [deleteConfirmMemberId, setDeleteConfirmMemberId] = useState<number | null>(null);

  // Reset errors when modal is opened or closed
  useEffect(() => {
    if (!isAddModalOpen) {
      setErrors({});
    }
  }, [isAddModalOpen]);

  const handleAddClick = () => {
    setEditingMember(null);
    setIsAddModalOpen(true);
  };

  // Reset formData when opening add modal
  useEffect(() => {
    if (isAddModalOpen && editingMember === null) {
      setFormData({ username: '', mail: '' });
    }
  }, [isAddModalOpen, editingMember]);

  const handleEditClick = (member: MemberDTO) => {
    setEditingMember(member);
    setFormData(member);
    setIsAddModalOpen(true);
  };

  const handleSave = () => {

    setErrors({});
    const newErrors: Record<string, string> = {};
    if (!formData.username) newErrors.username = 'Username is required';
    if (!formData.mail) {
      newErrors.mail = 'Email is required';
    } else {
      // Vérification du format d'email simple
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.mail)) {
        newErrors.mail = 'Invalid email format';
      }
    }
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    if (editingMember) {
      onUpdate({ ...editingMember, ...formData } as MemberDTO);
    } else {
      onAdd({
        username: formData.username,
        mail: formData.mail,
      } as MemberDTO);
    }

    setIsAddModalOpen(false);
    setFormData({});
    setErrors({});
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

      <div className="overflow-x-auto border border-border rounded-lg">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted">
              <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">
                Member
              </th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">
                Mail
              </th>
              <th className="px-10 py-4 text-right text-sm font-semibold text-foreground">
                Actions
              </th>
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
                    <span className="font-medium text-foreground w-full text-center block">{member.username}</span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="text-sm text-muted-foreground">{member.mail || 'N/A'}</span>
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
                <td colSpan={3} className="px-6 py-12 text-center">
                  <p className="text-muted-foreground">No members yet. Create your first member!</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add/Edit Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-md border-border shadow-2xl">
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-foreground">
                  {editingMember ? 'Edit Member' : 'Add New Member'}
                </h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsAddModalOpen(false)}
                  className="h-8 w-8"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-4">
                <div>
                  <Label className="text-foreground font-medium">Username</Label>
                  <Input
                    type="text"
                    placeholder="john.dev"
                    value={formData.username || ''}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="mt-2 bg-input border-border text-foreground"
                  />
                  {errors.username && (
                    <div className="text-red-500 text-xs mt-1">{errors.username}</div>
                  )}
                </div>
                <div>
                  <Label className="text-foreground font-medium">Mail</Label>
                  <Input
                    type="email"
                    placeholder="john.dev@company.com"
                    value={formData.mail || ''}
                    onChange={(e) => setFormData({ ...formData, mail: e.target.value })}
                    className="mt-2 bg-input border-border text-foreground"
                  />
                  {errors.mail && (
                    <div className="text-red-500 text-xs mt-1">{errors.mail}</div>
                  )}
                </div>
              </div>

              <div className="flex gap-2 pt-4 border-t border-border">
                <Button
                  variant="outline"
                  onClick={() => setIsAddModalOpen(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button onClick={handleSave} className="flex-1">
                  {editingMember ? 'Update' : 'Add'} Member
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmMemberId !== null} onOpenChange={(open) => { if (!open) setDeleteConfirmMemberId(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Are you sure you want to delete this member?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. The member will be permanently deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmMemberId(null)}>
              No
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (deleteConfirmMemberId !== null) {
                  onDelete(deleteConfirmMemberId);
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
