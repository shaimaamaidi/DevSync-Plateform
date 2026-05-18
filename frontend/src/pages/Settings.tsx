import { useCallback, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { showSuccessToast } from '@/components/global-toaster';
import { memberService } from '@/services/member-service';
import type { MemberUpdateDTO } from '@/api/api';
import { defaultOnError, withErrorHandling } from '@/services/api-error';
import { useCurrentUser } from '@/hooks/current-user-hooks/use-current-user';

export default function SettingsPage() {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ newPassword?: string; confirmPassword?: string }>({});
  const [generalError, setGeneralError] = useState<string | null>(null);

  const { user, loading: userLoading, error: userError } = useCurrentUser();
  const userId = user?.id ?? null;

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setFieldErrors({});
    setGeneralError(null);

    if (!userId) {
      setGeneralError('User not loaded');
      return;
    }

    const errors: { newPassword?: string; confirmPassword?: string } = {};
    if (!newPassword) {
      errors.newPassword = 'Please enter a new password.';
    } else if (newPassword.length < 6) {
      errors.newPassword = 'Password must be at least 6 characters.';
    }

    if (!confirmPassword) {
      errors.confirmPassword = 'Please confirm your new password.';
    } else if (newPassword !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match.';
    }

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }

    setLoading(true);
    const member: MemberUpdateDTO = {
      id: userId,
      password: newPassword,
    };

    try {
      const result = await withErrorHandling(
        () => memberService.updateMember(member),
        'Update password',
        onError(),
      );

      if (result) {
        showSuccessToast('Password updated successfully!');
        setNewPassword('');
        setConfirmPassword('');
        navigate('/profile');
      }
    } finally {
      setLoading(false);
    }
  };

  if (userLoading) {
    return (
      <div className="flex items-center justify-center py-20">
          <div className="text-muted-foreground">Loading user...</div>
      </div>
    );
  }

  if (userError) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-destructive">{userError}</div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-[420px] rounded-2xl border border-border/40 bg-background p-10 shadow-sm">
        <div className="flex justify-center mb-8">
          <div className="w-9 h-9 rounded-[10px] bg-foreground flex items-center justify-center">
            <div className="grid grid-cols-2 gap-[3px] w-[18px]">
              <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-90" />
              <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-60" />
              <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-60" />
              <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-30" />
            </div>
          </div>
        </div>

        <h1 className="font-serif text-[26px] font-normal text-center text-foreground leading-tight mb-1.5">
          Update your password
        </h1>
        <p className="text-[13px] text-muted-foreground text-center font-light tracking-wide mb-5">
          Change your password to keep your account secure
        </p>

        {generalError && (
          <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/30 text-destructive text-[13px] rounded-lg px-3.5 py-2.5 mb-5">
            <svg className="w-3.5 h-3.5 flex-shrink-0 fill-current" viewBox="0 0 16 16">
              <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 4a.75.75 0 01.75.75v3a.75.75 0 01-1.5 0v-3A.75.75 0 018 5zm0 6.5a.875.875 0 110-1.75.875.875 0 010 1.75z" />
            </svg>
            {generalError}
          </div>
        )}

        <form onSubmit={handleUpdatePassword} className="space-y-5">
          <div className="space-y-1.5">
            <label htmlFor="new-password" className="block text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
              New Password
            </label>
            <div className="relative">
              <input
                id="new-password"
                type={showNewPassword ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value);
                  setFieldErrors((prev) => ({ ...prev, newPassword: undefined }));
                }}
                autoComplete="new-password"
                placeholder="••••••••"
                className={`w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 pr-11 ${fieldErrors.newPassword ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15' : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'}`}
              />
              <button
                type="button"
                onClick={() => setShowNewPassword((prev) => !prev)}
                className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors text-muted-foreground hover:text-foreground"
                aria-label={showNewPassword ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {fieldErrors.newPassword && (
              <div className="text-destructive text-xs mt-1 px-1">{fieldErrors.newPassword}</div>
            )}
          </div>

          <div className="space-y-1.5">
            <label htmlFor="confirm-password" className="block text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
              Confirm New Password
            </label>
            <div className="relative">
              <input
                id="confirm-password"
                type={showConfirmPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  setFieldErrors((prev) => ({ ...prev, confirmPassword: undefined }));
                }}
                autoComplete="new-password"
                placeholder="••••••••"
                className={`w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 pr-11 ${fieldErrors.confirmPassword ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15' : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'}`}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
                className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors text-muted-foreground hover:text-foreground"
                aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {fieldErrors.confirmPassword && (
              <div className="text-destructive text-xs mt-1 px-1">{fieldErrors.confirmPassword}</div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 mt-1 rounded-lg bg-foreground text-background text-sm font-medium tracking-wide transition hover:opacity-85 active:scale-[0.99] disabled:opacity-50 disabled:cursor-default"
          >
            {loading ? 'Updating…' : 'Update Password'}
          </button>
        </form>
      </div>
    </div>
  );
}
