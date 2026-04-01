import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { showSuccessToast } from '@/components/global-success-toaster';

export default function SignupPage() {
  const [mail, setMail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // TODO: call signup API
      // await authService.signup({ mail, username, password });
      showSuccessToast('Account created! You can now log in.');
      navigate('/login');
    } catch (err: any) {
      setError('Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted">
      <Card className="w-full max-w-md p-8 space-y-6">
        <h2 className="text-2xl font-bold text-center">Create your account</h2>
        <form className="space-y-4" onSubmit={handleSignup}>
          <div>
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              autoComplete="username"
            />
          </div>
          <div>
            <Label htmlFor="mail">Email</Label>
            <Input
              id="mail"
              type="email"
              value={mail}
              onChange={(e) => setMail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>
          {error && <div className="text-destructive text-sm text-center">{error}</div>}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Signing up...' : 'Sign Up'}
          </Button>
        </form>
        <div className="text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Button variant="link" type="button" onClick={() => navigate('/login')}>
            Sign in
          </Button>
        </div>
      </Card>
    </div>
  );
}
