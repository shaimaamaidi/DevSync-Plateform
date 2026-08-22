import { useEffect, useState } from 'react';
import { MemberRole, type MemberCreateDTO, type MemberDTO, type MemberUpdateDTO } from '@/api/api';
import { Button } from '@/components/ui/shared-primitives/button';
import { Card } from '@/components/ui/shared-primitives/card';
import { Label } from '@/components/ui/shared-primitives/label';
import { AlertCircle, CheckCircle2, Loader2, X } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './shared-primitives/select';

export interface MemberEditModalProps {
  isOpen: boolean;
  editingMember: MemberDTO | null;
  onClose: () => void;
  onAdd: (member: MemberCreateDTO) => Promise<boolean>;
  handleAddSuccess: (member: MemberCreateDTO) => void;
  onUpdate: (member: MemberUpdateDTO) => Promise<boolean>;
}

export function MemberEditModal({
  isOpen,
  editingMember,
  onClose,
  onAdd,
  handleAddSuccess,
  onUpdate,
}: MemberEditModalProps) {
  const [formData, setFormData] = useState<Partial<MemberUpdateDTO & { password?: string }>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  const hasChanges = editingMember
    ? formData.username !== editingMember.username ||
      formData.mail !== editingMember.mail ||
      formData.arabic_name !== (editingMember.arabic_name || '') ||
      formData.role !== editingMember.role ||
      (!!formData.password && formData.password.length > 0)
    : true;

  const isCancelDisabled = isSaving;
  const isSaveDisabled = isSaving;

  useEffect(() => {
    if (isOpen) {
      setErrors({});
      setIsSaving(false);
      setFormData(
        editingMember
          ? {
              id: editingMember.id,
              username: editingMember.username,
              mail: editingMember.mail,
              arabic_name: editingMember.arabic_name || '',
              role: editingMember.role,
              password: '',
            }
          : { username: '', mail: '', arabic_name: '', role: MemberRole.Member, password: '' }
      );
    }
  }, [isOpen, editingMember]);

  const handleSave = async () => {
    setErrors({});

    const newErrors: Record<string, string> = {};

    if (editingMember && !hasChanges) {
      setErrors({ form: 'No changes to update' });
      return;
    }
    if (!formData.username?.trim()) 
      newErrors.username = 'Username is required';
    if (!formData.mail?.trim()) {
      newErrors.mail = 'Email is required';
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.mail)) {
        newErrors.mail = 'Invalid email format';
      }
    }

    if (!editingMember && !formData.arabic_name?.trim()) {
      newErrors.arabic_name = 'Arabic name is required';
    }

    if (!editingMember && !formData.role) {
      newErrors.role = 'Role is required';
    }

    if (!editingMember && (!formData.password || formData.password.trim().length < 6)) {
      newErrors.password = 'Password (min 6 caractères) requis';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSaving(true);

    try {
      let success = false;
      let newMember: MemberCreateDTO | null = null;
      if (editingMember) {
        success = await onUpdate({
          id: editingMember.id,
          username: formData.username === editingMember.username ? null : formData.username,
          mail: formData.mail === editingMember.mail ? null : formData.mail,
          arabic_name: formData.arabic_name === editingMember.arabic_name ? null : formData.arabic_name,
          role: formData.role === editingMember.role ? null : formData.role,
          password: (formData.password === '') ? null : formData.password,
        } as MemberUpdateDTO);
      } else {
        newMember = {
          username: formData.username,
          mail: formData.mail,
          arabic_name: formData.arabic_name,
          password: formData.password,
          role: formData.role,
        } as MemberCreateDTO;
        success = await onAdd(newMember);
      }
      if (success) {
        onClose();
        if (!editingMember && newMember) { 
          handleAddSuccess(newMember);
        }
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) 
    return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="w-full max-w-md border-border shadow-2xl flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between px-6 pt-6 pb-4 shrink-0">
          <h2 className="text-xl font-bold text-foreground">
            {editingMember ? 'Edit Member' : 'Add New Member'}
          </h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            disabled={isCancelDisabled}
            className="h-8 w-8"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="overflow-y-auto flex-1 px-6 space-y-4">
          <div>
            <Label className="text-foreground font-medium">Username</Label>
            <input
              type="text"
              placeholder="john.dev"
              value={formData.username || ''}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              onBlur={(e) => {
                if (!e.target.value.trim() && editingMember) {
                  setFormData({ ...formData, username: editingMember.username });
                }
              }}
              className={inputClass(!!errors.username) + ' mt-2'}
              disabled={isSaving}
            />
            {errors.username && (
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.username}
              </div>
            )}
          </div>

          <div>
            <Label className="text-foreground font-medium">Mail</Label>
            <input
              type="email"
              placeholder="john.dev@company.com"
              value={formData.mail || ''}
              onChange={(e) => setFormData({ ...formData, mail: e.target.value })}
              onBlur={(e) => {
                if (!e.target.value.trim() && editingMember) {
                  setFormData({ ...formData, mail: editingMember.mail });
                }
              }}
              className={inputClass(!!errors.mail) + ' mt-2'}
              disabled={isSaving}
            />
            {errors.mail && (
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.mail}
              </div>
            )}
          </div>

          <div>
            <Label className="text-foreground font-medium">Arabic Name</Label>
            <input
              type="text"
              placeholder="الاسم بالعربية"
              dir="rtl"
              value={formData.arabic_name || ''}
              onChange={(e) => setFormData({ ...formData, arabic_name: e.target.value })}
              onBlur={(e) => {
                if (!e.target.value.trim() && editingMember) {
                  setFormData({ ...formData, arabic_name: editingMember.arabic_name });
                }
              }}
              className={inputClass(!!errors.arabic_name) + ' mt-2'}
              disabled={isSaving}
            />
            {errors.arabic_name && (
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.arabic_name}
              </div>
            )}
          </div>
            
          <div>
            <Label className="text-foreground font-medium">Role</Label>
            <Select
              value={formData.role || MemberRole.Member}
              onValueChange={(value) => setFormData({ ...formData, role: value as MemberRole })}
              disabled={isSaving}
            >
              <SelectTrigger className="mt-2 w-full bg-input border-border text-foreground">
                <SelectValue placeholder="Select a role" />
              </SelectTrigger>
              <SelectContent className="bg-card border-border">
                <SelectItem value={MemberRole.Member}>Member</SelectItem>
                <SelectItem value={MemberRole.Admin}>Admin</SelectItem>
              </SelectContent>
            </Select>
            {errors.role && (
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.role}
              </div>
            )}
          </div>

          <div>
            <Label className="text-foreground font-medium">Password</Label>
            <input
              type="password"
              placeholder="Password"
              value={formData.password || ''}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className={inputClass(!!errors.password) + ' mt-2'}
              disabled={isSaving}
            />
            {editingMember && (
              <div className="text-muted-foreground text-xs mt-1">                
                Leave blank to keep the password unchanged.
              </div>
            )}

            {errors.password && (
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.password}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between px-6 py-4 border-t border-border shrink-0">
          {errors.form ? (
            <div className="text-destructive text-sm">{errors.form}</div>
          ) : <div/>}
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isCancelDisabled}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              className="flex-1 gap-2"
              disabled={isSaveDisabled}
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  {editingMember ? 'Update' : 'Save'} Member
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}