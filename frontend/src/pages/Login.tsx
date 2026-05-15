import { useState } from 'react';
import { authService } from '@/services/auth-service';
import { useNavigate } from 'react-router-dom';
import { showSuccessToast } from '@/components/global-toaster';
import { Eye, EyeOff } from 'lucide-react';
import { withErrorHandling } from '@/services/api-error';
import type { MemberAuthDTO } from '@/api/api';
import { defaultOnError } from '@/utils/error-handler';

export default function LoginPage() {
  const [mail, setMail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [invalidCredentials, setInvalidCredentials] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ mail?: string; password?: string }>({});
  const navigate = useNavigate();

  const onError = defaultOnError(navigate);

  const validateFields = () => {
    const errors: { mail?: string; password?: string } = {};
    if (!mail) {
      errors.mail = 'Please enter your email address.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail)) {
      errors.mail = 'Please enter a valid email address.';
    }
    if (!password) {
      errors.password = 'Please enter your password.';
    }
    return errors;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setInvalidCredentials(false);
    const errors = validateFields();
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) 
      return;
    
    setLoading(true);
    
     const result = await withErrorHandling(
      () => authService.login({ mail, password } as MemberAuthDTO),
      'Login',
      onError,
    );

    setLoading(false);

    if (!result) {
      setInvalidCredentials(true);
      return;
    }

    showSuccessToast('Login successful!');
    navigate('/repositories');
  };

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted px-4 py-8">
      <div className="w-full max-w-[420px] rounded-2xl border border-border/40 bg-background p-6 sm:p-10 shadow-sm">
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
        <form onSubmit={handleLogin} className="space-y-5" noValidate>
          <div className="space-y-1.5">
            <label
              htmlFor="mail"
              className="block text-[11px] font-semibold uppercase tracking-widest text-foreground"
            >
              Email address
            </label>
            <input
              id="mail"
              type="email"
              value={mail}
              onChange={(e) => {
                setMail(e.target.value);
                setInvalidCredentials(false);
                setFieldErrors((prev) => ({ ...prev, mail: undefined }));
              }}
              autoFocus
              autoComplete="email"
              placeholder="you@example.com"
              className={inputClass(!!fieldErrors.mail || invalidCredentials)}
            />
            {fieldErrors.mail && (
              <div className="text-destructive text-xs mt-1 px-1">{fieldErrors.mail}</div>
            )}
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="password"
              className="block text-[11px] font-semibold uppercase tracking-widest text-foreground"
            >
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setInvalidCredentials(false);
                  setFieldErrors((prev) => ({ ...prev, password: undefined }));
                }}
                autoComplete="current-password"
                placeholder="••••••••"
                className={`${inputClass(!!fieldErrors.password || invalidCredentials)} pr-11`}
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
            {fieldErrors.password && (
              <div className="text-destructive text-xs mt-1 px-1">{fieldErrors.password}</div>
            )}
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