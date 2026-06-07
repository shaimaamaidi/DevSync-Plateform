import { Navigation } from '@/components/navigation';
import { AppFooter } from '@/components/app-footer';
import { Outlet } from 'react-router-dom';
import { useCurrentUser } from '@/hooks/current-user-hooks/use-current-user';


export function RootLayout() {
  useCurrentUser();
  
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation />
      <main className="flex-1 flex flex-col max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        <Outlet />
      </main>
      <AppFooter />
    </div>
  );
}