import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, User, Mail, Pen , Loader2, ArrowLeft } from 'lucide-react';
import { useCurrentUser } from '@/hooks/use-current-user';
import { memberService } from '@/services/member-service';
import { withErrorHandling } from '@/services/api-error';
import { showSuccessToast } from '@/components/global-success-toaster';
import type { MemberUpdateDTO } from '@/api/api';
import { defaultOnError } from '@/utils/default-on-error';

export default function ProfilePage() {
  const { user } = useCurrentUser();
  const navigate = useNavigate();

  const initialUsername = user?.username || '';
  const initialMail = user?.mail || '';

  const [username, setUsername] = useState(initialUsername);
  const [mail, setMail] = useState(initialMail);
  const [loading, setLoading] = useState(false);

  const isDirty = username !== initialUsername || mail !== initialMail;

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isDirty) return;
    setLoading(true);
    
    const member: MemberUpdateDTO = {
      id: user?.id,
      username: username,
      mail: mail,
    };
    
    try{
      const result = await withErrorHandling(
        () => memberService.updateMember(member),
        'Update profile',
        defaultOnError(navigate),
      );

      if (result) 
        showSuccessToast('Profile updated successfully!');
    }finally{
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-muted">

      <nav className="border-b border-border bg-card sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-[10px] bg-foreground flex items-center justify-center">
                <div className="grid grid-cols-2 gap-[3px] w-[18px]">
                  <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-90" />
                  <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-60" />
                  <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-60" />
                  <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-30" />
                </div>
              </div>
              <span className="text-lg font-bold text-foreground tracking-tight">GitHub & Deployments</span>
            </div>
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors ml-auto"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex flex-col items-center mb-10">
          <div className="w-20 h-20 rounded-full bg-foreground/8 border border-border/40 flex items-center justify-center mb-4">
            <span className="text-[28px] font-medium text-foreground uppercase">
              {username.slice(0, 2)}
            </span>
          </div>
          <h1 className="font-serif text-[30px] font-normal text-foreground leading-tight mb-1">
            My Profile
          </h1>
          <p className="text-[13px] text-muted-foreground font-light tracking-wide">
            Your account information
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">

          <div className="w-full rounded-2xl border border-border/40 bg-background p-8 shadow-sm">
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
          </div>

          <div className="w-full rounded-2xl border border-border/40 bg-background p-8 shadow-sm flex flex-col h-full">
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
    </div>
  );
}