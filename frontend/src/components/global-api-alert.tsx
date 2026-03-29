import { useEffect, useState } from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { subscribeToApiError } from '@/services/api-error';

export function GlobalApiAlert() {
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const unsub = subscribeToApiError((msg) => {
      setMessage(msg);
      setTimeout(() => setMessage(null), 6000);
    });
    return unsub;
  }, []);

  if (!message) return null;

  return (
    <div style={{ position: 'fixed', top: 24, right: 24, zIndex: 9999, maxWidth: 400 }}>
      <Alert variant="destructive">
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>{message}</AlertDescription>
      </Alert>
    </div>
  );
}
