import { useState } from 'react';
import { authService } from '@/services/auth-service';
import { useNavigate } from 'react-router-dom';
import { showSuccessToast } from '@/components/global-success-toaster';
import { toast } from '@/components/ui/use-toast';
import { Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const [mail, setMail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [invalidCredentials, setInvalidCredentials] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setInvalidCredentials(false);
    try {
      await authService.login({ mail, password });
      showSuccessToast('Login successful!');
      toast({ title: 'Login', description: 'You are now logged in.', variant: 'success' });
      navigate('/repositories');
    } catch (err: any) {
      const isNetworkError = err?.code === 'ERR_NETWORK' || !err?.response;
      if (isNetworkError) {
        setError(null); 
        setInvalidCredentials(false);
        toast({
          title: 'Connection problem',
          description: 'Unable to connect to the server. Please try again in a few minutes.',
          variant: 'destructive',
        });
      } else {
        setInvalidCredentials(true);
        toast({ title: 'Login failed', description: 'Invalid credentials', variant: 'destructive' });
      }
    } finally {
      setLoading(false);
    }
  };

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted">
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
          Welcome back
        </h1>
        <p className="text-[13px] text-muted-foreground text-center font-light tracking-wide mb-5">
          Sign in to continue to your workspace
        </p>

        {invalidCredentials && (
          <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/30 text-destructive text-[13px] rounded-lg px-3.5 py-2.5 mb-5">
            <svg className="w-3.5 h-3.5 flex-shrink-0 fill-current" viewBox="0 0 16 16">
              <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 4a.75.75 0 01.75.75v3a.75.75 0 01-1.5 0v-3A.75.75 0 018 5zm0 6.5a.875.875 0 110-1.75.875.875 0 010 1.75z" />
            </svg>
            Invalid credentials. Please try again.
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/30 text-destructive text-[13px] rounded-lg px-3.5 py-2.5 mb-5">
            <svg className="w-3.5 h-3.5 flex-shrink-0 fill-current" viewBox="0 0 16 16">
              <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 4a.75.75 0 01.75.75v3a.75.75 0 01-1.5 0v-3A.75.75 0 018 5zm0 6.5a.875.875 0 110-1.75.875.875 0 010 1.75z" />
            </svg>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div className="space-y-1.5">
            <label
              htmlFor="mail"
              className={`block text-[11px] font-semibold uppercase tracking-widest text-muted-foreground`}
            >
              Email address
            </label>
            <input
              id="mail"
              type="email"
              value={mail}
              onChange={(e) => { setMail(e.target.value); setInvalidCredentials(false); }}
              required
              autoFocus
              autoComplete="email"
              placeholder="you@example.com"
              className={inputClass(invalidCredentials)}
            />
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="password"
              className={`block text-[11px] font-semibold uppercase tracking-widest text-muted-foreground`}
            >
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => { setPassword(e.target.value); setInvalidCredentials(false); }}
                required
                autoComplete="current-password"
                placeholder="••••••••"
                className={`${inputClass(invalidCredentials)} pr-11`}
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                className={`absolute right-3 top-1/2 -translate-y-1/2 transition-colors text-muted-foreground hover:text-foreground`}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <div className="text-right h-[12px]"></div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 mt-1 rounded-lg bg-foreground text-background text-sm font-medium tracking-wide transition hover:opacity-85 active:scale-[0.99] disabled:opacity-50 disabled:cursor-default"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}