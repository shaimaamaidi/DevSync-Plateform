import { useEffect, useState } from 'react';
import type { MemberCreateDTO, MemberDTO, MemberUpdateDTO } from '@/api/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { CheckCircle2, Loader2, X } from 'lucide-react';

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
      (!!formData.password && formData.password.length > 0)
    : true;

  const isFormEmpty = !formData.username?.trim() || !formData.mail?.trim();

  const isCancelDisabled = isSaving;
  const isSaveDisabled = editingMember
    ? !hasChanges || isSaving
    : isFormEmpty || isSaving;

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
              password: '',
            }
          : { username: '', mail: '', arabic_name: '', password: '' }
      );
    }
  }, [isOpen, editingMember]);

  const handleSave = async () => {
    setErrors({});

    const newErrors: Record<string, string> = {};
    if (!formData.username) newErrors.username = 'Username is required';
    if (!formData.mail) {
      newErrors.mail = 'Email is required';
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.mail)) {
        newErrors.mail = 'Invalid email format';
      }
    }
    if (!editingMember && (!formData.password || formData.password.length < 6)) {
      newErrors.password = 'Password (min 6 caractères) requis';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSaving(true);

    try {
      let success = false;
      let member: MemberDTO | null = null;
      if (editingMember) {
        success = await onUpdate({
          id: editingMember.id,
          username: formData.username,
          mail: formData.mail,
          arabic_name: formData.arabic_name,
          password: formData.password,
        } as MemberUpdateDTO);
      } else {
        member ={
          username: formData.username,
          mail: formData.mail,
          arabic_name: formData.arabic_name,
          password: formData.password,
        } as MemberCreateDTO;
        success = await onAdd(member);
      }
      if (success) {
        onClose();
        if (!editingMember && member) {
          handleAddSuccess(member);
        }
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    isOpen && (
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
                onClick={onClose}
                disabled={isCancelDisabled}
                className="h-8 w-8"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <Label className="text-foreground font-medium">Username</Label>
                <input
                  type="text"
                  placeholder="john.dev"
                  value={formData.username || ''}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className={inputClass(!!errors.username) + ' mt-2'}
                  disabled={isSaving}
                />
                {errors.username && (
                  <div className="text-destructive text-xs mt-1 px-1">{errors.username}</div>
                )}
              </div>

              <div>
                <Label className="text-foreground font-medium">Mail</Label>
                <input
                  type="email"
                  placeholder="john.dev@company.com"
                  value={formData.mail || ''}
                  onChange={(e) => setFormData({ ...formData, mail: e.target.value })}
                  className={inputClass(!!errors.mail) + ' mt-2'}
                  disabled={isSaving}
                />
                {errors.mail && (
                  <div className="text-destructive text-xs mt-1 px-1">{errors.mail}</div>
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
                  className={inputClass(!!errors.arabic_name) + ' mt-2'}
                  disabled={isSaving}
                />
                {errors.arabic_name && (
                  <div className="text-destructive text-xs mt-1 px-1">{errors.arabic_name}</div>
                )}
              </div>

              <div>
                <Label className="text-foreground font-medium">Password</Label>
                <input
                  type="password"
                  placeholder="Mot de passe (laisser vide pour ne pas changer)"
                  value={formData.password || ''}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className={inputClass(!!errors.password) + ' mt-2'}
                  disabled={isSaving}
                />
                {editingMember && (
                  <div className="text-muted-foreground text-xs mt-1">
                    Laisser vide pour ne pas changer le mot de passe
                  </div>
                )}
                {errors.password && (
                  <div className="text-destructive text-xs mt-1 px-1">{errors.password}</div>
                )}
              </div>
            </div>

            <div className="flex gap-2 pt-4 border-t border-border">
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
                    {editingMember ? 'Update' : 'Create'} Member
                  </>
                )}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    )
  );
}