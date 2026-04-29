import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, User, Mail, Pen, Loader2 } from 'lucide-react';
import { useCurrentUser } from '@/hooks/use-current-user';
import { memberService } from '@/services/member-service';
import { withErrorHandling } from '@/services/api-error';
import { showSuccessToast } from '@/components/global-toaster';
import type { MemberUpdateDTO } from '@/api/api';
import { defaultOnError } from '@/lib/error-utils';

function FieldSkeleton() {
  return (
    <div className="space-y-1.5">
      <div className="h-3 w-20 rounded bg-muted animate-pulse" />
      <div className="h-11 w-full rounded-lg bg-muted animate-pulse" />
    </div>
  );
}

export default function ProfilePage() {
  const { user, loading: userLoading } = useCurrentUser();
  const navigate = useNavigate();
  const onError = defaultOnError(navigate);

  const [username, setUsername] = useState('');
  const [mail, setMail] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setUsername(user.username || '');
      setMail(user.mail || '');
    }
  }, [user]);

  const isDirty = username !== (user?.username || '') || mail !== (user?.mail || '');

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isDirty) return;
    setLoading(true);

    const member: MemberUpdateDTO = {
      id: user?.id,
      username,
      mail,
    };

    try {
      const result = await withErrorHandling(
        () => memberService.updateMember(member),
        'Update profile',
        onError,
      );
      if (result) showSuccessToast('Profile updated successfully!');
    } finally {
      setLoading(false);
    }
  };

  const initials = username.slice(0, 2).toUpperCase();

  return (
    <div className="py-6 md:py-12">
      <div className="flex flex-col items-center mb-6 md:mb-10">
        <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-foreground/8 border border-border/40 flex items-center justify-center mb-4">
          {userLoading ? (
            <div className="w-full h-full rounded-full bg-muted animate-pulse" />
          ) : (
            <span className="text-2xl md:text-[28px] font-medium text-foreground">
              {initials}
            </span>
          )}
        </div>
        <h1 className="font-serif text-2xl md:text-[30px] font-normal text-foreground leading-tight mb-1">
          My Profile
        </h1>
        <p className="text-[13px] text-muted-foreground font-light tracking-wide">
          Your account information
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 w-full">
        <div className="w-full rounded-2xl border border-border/40 bg-background p-5 md:p-8 shadow-sm">
          <h2 className="text-[11px] font-medium text-muted-foreground uppercase tracking-widest mb-5">
            Personal information
          </h2>

          {userLoading ? (
            <div className="space-y-5">
              <FieldSkeleton />
              <FieldSkeleton />
              <div className="h-11 w-full rounded-lg bg-muted animate-pulse mt-1" />
            </div>
          ) : (
            <form onSubmit={handleUpdate} className="space-y-5">
              <div className="space-y-1.5">
                <label
                  htmlFor="username"
                  className="block text-[11px] font-semibold uppercase tracking-widest text-foreground flex items-center gap-1.5"
                >
                  <User className="w-3 h-3" />
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  placeholder="Your username"
                  className="w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 border-border/60 focus:border-foreground/40 focus:ring-foreground/8"
                />
              </div>

              <div className="space-y-1.5">
                <label
                  htmlFor="mail"
                  className="block text-[11px] font-semibold uppercase tracking-widest text-foreground flex items-center gap-1.5"
                >
                  <Mail className="w-3 h-3" />
                  Email address
                </label>
                <input
                  id="mail"
                  type="email"
                  value={mail}
                  onChange={(e) => setMail(e.target.value)}
                  autoComplete="email"
                  placeholder="you@example.com"
                  className="w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 border-border/60 focus:border-foreground/40 focus:ring-foreground/8"
                />
              </div>

              <button
                type="submit"
                disabled={!isDirty || loading}
                className="w-full h-11 mt-1 rounded-lg bg-foreground text-background text-sm font-medium tracking-wide transition hover:opacity-85 active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving…
                  </>
                ) : (
                  <>
                    <Pen className="w-4 h-4" />
                    Update profile
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        <div className="w-full rounded-2xl border border-border/40 bg-background p-5 md:p-8 shadow-sm flex flex-col">
          <h2 className="text-[11px] font-medium text-muted-foreground uppercase tracking-widest mb-5">
            Security
          </h2>
          <div className="flex-1">
            <label className="block text-[11px] font-semibold uppercase tracking-widest text-foreground flex items-center gap-1.5 mb-2">
              <KeyRound className="w-3 h-3" />
              Password
            </label>
            <p className="text-[13px] text-muted-foreground font-light mb-4">
              Update your password to keep your account secure
            </p>
          </div>
          <button
            type="button"
            onClick={() => navigate('/settings')}
            className="w-full p-4 rounded-lg border border-border/60 bg-muted/50 hover:bg-muted transition-colors flex items-center justify-center gap-2 text-sm font-medium text-foreground mt-6"
          >
            <KeyRound className="w-4 h-4" />
            Change password
          </button>
        </div>
      </div>
    </div>
  );
}