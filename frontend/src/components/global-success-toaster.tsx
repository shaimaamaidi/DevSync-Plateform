import { ToastProvider, ToastViewport, Toast, ToastTitle, ToastDescription } from '@/components/ui/toast';
import { useToast, toast } from '@/components/ui/use-toast';

export function GlobalSuccessToaster() {
  const { toasts, dismiss } = useToast();
  return (
    <ToastProvider>
      {toasts.map((t) => (
        <Toast key={t.id} open={t.open} onOpenChange={(o) => !o && dismiss(t.id)}>
          <ToastTitle>{t.title}</ToastTitle>
          <ToastDescription>{t.description}</ToastDescription>
        </Toast>
      ))}
      <ToastViewport />
    </ToastProvider>
  );
}

export function showSuccessToast(message: string, title = 'Succès') {
  toast({ title, description: message });
}
