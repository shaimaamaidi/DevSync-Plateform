import { useState, useEffect } from 'react';
import { KeyRound, User, Mail, Pen, Loader2, AlertCircle } from 'lucide-react';
import { showSuccessToast } from '@/components/global-toaster';
import type { MemberUpdateDTO } from '@/api/api';
import { FieldSkeleton } from '@/components/ui/field-skeleton';
import { useNavigate } from 'react-router-dom';
import { useUpdateCurrentUser } from '@/hooks/current-user-hooks/use-update-current-member';
import { useCurrentUser } from '@/hooks/current-user-hooks/use-current-user';


export default function ProfilePage() {
  const { user, loading: userLoading, error: userError, refetch } = useCurrentUser();
  const { mutateAsync: updateMember, isPending } = useUpdateCurrentUser();

  const [username, setUsername] = useState('');
  const [mail, setMail] = useState('');
  const [arabicName, setArabicName] = useState('');
  const initials = username.slice(0, 2).toUpperCase();
  
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      setUsername(user.username || '');
      setMail(user.mail || '');
      setArabicName(user.arabic_name || '');
    }
  }, [user]);

  const isDirty =
    username !== (user?.username || '') ||
    mail !== (user?.mail || '') ||
    arabicName !== (user?.arabic_name || '');

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isDirty || !user) 
      return;

    const member: MemberUpdateDTO = {
      id: user.id,
      username,
      mail,
      arabic_name: arabicName,
    };

    const result = await updateMember(member); 

    if (result) 
      showSuccessToast('Profile updated successfully!');
  };

  if (userLoading) {
    return (
      <div className="py-6 md:py-12">
        <div className="flex flex-col items-center mb-6 md:mb-10">
          <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-muted animate-pulse mb-4" />
          <div className="h-7 w-32 rounded-lg bg-muted animate-pulse mb-2" />
          <div className="h-4 w-44 rounded-lg bg-muted animate-pulse" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 w-full">
          <div className="w-full rounded-2xl border border-border/40 bg-background p-5 md:p-8 shadow-sm">
            <div className="h-3 w-36 rounded bg-muted animate-pulse mb-5" />
            <div className="space-y-5">
              <FieldSkeleton />
              <FieldSkeleton />
              <FieldSkeleton />
              <div className="h-11 w-full rounded-lg bg-muted animate-pulse mt-1" />
            </div>
          </div>
          <div className="w-full rounded-2xl border border-border/40 bg-background p-5 md:p-8 shadow-sm">
            <div className="h-3 w-20 rounded bg-muted animate-pulse mb-5" />
            <div className="space-y-3">
              <div className="h-3 w-24 rounded bg-muted animate-pulse" />
              <div className="h-4 w-64 rounded bg-muted animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (userError) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <div className="flex items-center gap-2 text-destructive text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          Failed to load profile data.
        </div>
        <button
          onClick={() => refetch()}
          className="text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground transition"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="py-6 md:py-12">
      <div className="flex flex-col items-center mb-6 md:mb-10">
        <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-foreground/8 border border-border/40 flex items-center justify-center mb-4">
          <span className="text-2xl md:text-[28px] font-medium text-foreground">
            {initials}
          </span>
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

              <div className="space-y-1.5">
                <label
                  htmlFor="arabic-name"
                  className="block text-[11px] font-semibold uppercase tracking-widest text-foreground flex items-center gap-1.5"
                >
                  <User className="w-3 h-3" />
                  Arabic Name
                </label>
                <input
                  id="arabic-name"
                  type="text"
                  value={arabicName}
                  onChange={(e) => setArabicName(e.target.value)}
                  placeholder="الاسم بالعربية"
                  dir="rtl"
                  className="w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 border-border/60 focus:border-foreground/40 focus:ring-foreground/8"
                />
              </div>

              <button
                type="submit"
                disabled={!isDirty || isPending}
                className="w-full h-11 mt-1 rounded-lg bg-foreground text-background text-sm font-medium tracking-wide transition hover:opacity-85 active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isPending ? (
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