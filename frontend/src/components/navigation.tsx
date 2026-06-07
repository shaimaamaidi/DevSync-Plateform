import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/shared-primitives/button';
import { 
  GitBranch, 
  Zap, 
  Users, 
  Boxes, 
  LogOut, 
  Settings, 
  FlaskConical, 
  Menu, 
  X, 
  ClipboardList, 
  BarChart2
} from 'lucide-react';
import { authService } from '@/services/auth-service';
import { useIsMobile } from '@/hooks/use-mobile';
import logo from '@/assets/rido-logo.jpeg';
import { useCurrentUser } from '@/hooks/current-user-hooks/use-current-user';

type HomeTab = 'repos' | 'deployments' | 'members' | 'spaces' | 'backlog-generation' | 'meeting-tasks' | 'project-insights';

interface NavigationProps {
  activeTab?: HomeTab;
  onTabChange?: (tab: HomeTab) => void;
}

const NAV_ITEMS = [
  { path: '/repositories', tab: 'repos' as HomeTab, icon: GitBranch, label: 'Repositories' },
  { path: '/deployments', tab: 'deployments' as HomeTab, icon: Zap, label: 'Deployments' },
  { path: '/members', tab: 'members' as HomeTab, icon: Users, label: 'Members' },
  { path: '/spaces', tab: 'spaces' as HomeTab, icon: Boxes, label: 'Spaces' },
  { path: '/backlog-generation-chat', tab: 'backlog-generation' as HomeTab, icon: FlaskConical, label: 'Backlog Generation' },
  { path: '/meeting-tasks', tab: 'meeting-tasks' as HomeTab, icon: ClipboardList, label: 'Meeting Tasks' },
  { path: '/project-insights', tab: 'project-insights' as HomeTab, icon: BarChart2, label: 'Project Insights' },
];

export function Navigation({ onTabChange }: NavigationProps) {
  const { user: currentUser, loading } = useCurrentUser();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const isMobile = useIsMobile();
  const [mobileOpen, setMobileOpen] = useState(false);

  const visibleNavItems = NAV_ITEMS.filter(({ tab }) =>
    tab === 'members' ? currentUser?.role === 'admin' : true
  );

  const handleNav = (path: string, tab?: HomeTab) => {
    navigate(path);
    if (tab) onTabChange?.(tab);
    setMobileOpen(false);
  };

  return (
    <nav className="border-b border-border bg-card sticky top-0 z-50 shadow-sm relative">
      <div className="max-w-7xl mx-auto px-2">
        <div className="flex items-center h-16">

          <button
            onClick={() => handleNav('/')}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity shrink-0"
          >
          <img
            src={logo}
            alt="Logo"
            className="w-10 h-10 rounded-xl object-cover border border-border"
          />            
          {!isMobile && (
              <h1 className="text-lg font-bold text-foreground tracking-tight" style={{ color: '#0E9E82' }}>
                Rido Ops
              </h1>
            )}
          </button>

          {!isMobile && (
            <div className="flex-1 flex items-center justify-center">
              {loading ? (
                <div className="flex items-center gap-1 p-1 bg-muted rounded-lg">
                  {Array.from({ length: NAV_ITEMS.length }).map((_, i) => (
                    <div key={i} className="h-9 w-24 rounded-md bg-muted-foreground/20 animate-pulse" />
                  ))}
                </div>
              ) : (
                <div className="flex items-center gap-1 p-1 bg-muted rounded-lg">
                  {visibleNavItems.map(({ path, tab, icon: Icon, label }) => (
                    <Button
                      key={path}
                      variant={pathname === path ? 'default' : 'ghost'}
                      onClick={() => handleNav(path, tab)}
                      className="gap-2"
                    >
                      <Icon className="w-4 h-4" />
                      <span>{label}</span>
                    </Button>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="shrink-0 flex items-center gap-1 ml-auto">
            <Button
              variant="ghost"
              onClick={() => handleNav('/profile')}
              title="Profile"
            >
              <Settings className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              onClick={() => { authService.logout(); navigate('/login'); }}
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </Button>

            {isMobile && (
              <Button
                variant="ghost"
                onClick={() => setMobileOpen(prev => !prev)}
                aria-label="Toggle menu"
              >
                {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            )}
          </div>
        </div>
      </div>

      {isMobile && (
        <div
          style={{
            position: 'absolute',
            top: '64px',
            left: 0,
            right: 0,
            zIndex: 49,
            transformOrigin: 'top',
            transform: mobileOpen ? 'scaleY(1)' : 'scaleY(0)',
            opacity: mobileOpen ? 1 : 0,
            pointerEvents: mobileOpen ? 'auto' : 'none',
            transition: 'transform 0.2s ease, opacity 0.18s ease',
          }}
          className="border-b border-border bg-card px-4 py-3 flex flex-col gap-1 shadow-md"
        >
          {loading ? (
            Array.from({ length: NAV_ITEMS.length }).map((_, i) => (
              <div key={i} className="h-9 w-full rounded-md bg-muted-foreground/20 animate-pulse" />
            ))
          ) : (
            visibleNavItems.map(({ path, tab, icon: Icon, label }) => (
              <Button
                key={path}
                variant={pathname === path ? 'default' : 'ghost'}
                onClick={() => handleNav(path, tab)}
                className="w-full justify-start gap-3"
              >
                <Icon className="w-4 h-4" />
                {label}
              </Button>
            ))
          )}
        </div>
      )}
    </nav>
  );
}