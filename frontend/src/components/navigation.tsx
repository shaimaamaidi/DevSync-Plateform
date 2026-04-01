import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { GitBranch, Zap, Users, Boxes, LogOut, Settings } from 'lucide-react';



type HomeTab = 'repos' | 'deployments' | 'members' | 'spaces';
interface NavigationProps {
  activeTab?: HomeTab;
  onTabChange?: (tab: HomeTab) => void;
}

export function Navigation({ onTabChange }: NavigationProps) {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const isRepositoriesPage = pathname === '/repositories';
  const isDeploymentsPage = pathname === '/deployments';
  const isMembersPage = pathname === '/members';
  const isSpacesPage = pathname === '/spaces';

  return (
    <nav className="border-b border-border bg-card sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
          >
            <div className="p-2.5 rounded-lg bg-gradient-to-br from-primary/20 to-primary/10 border border-primary/30">
              <GitBranch className="w-6 h-6 text-primary" />
            </div>
            <div className="text-left">
              <h1 className="text-lg font-bold text-foreground tracking-tight">GitHub & Deployments</h1>
            </div>
          </button>

          {/* Navigation Tabs + Config + Logout */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 p-1 bg-muted rounded-lg">
              <Button
                variant={isRepositoriesPage ? 'default' : 'ghost'}
                onClick={() => {
                  navigate('/repositories');
                  onTabChange?.('repos');
                }}
                className="gap-2"
              >
                <GitBranch className="w-4 h-4" />
                <span className="hidden sm:inline">Repositories</span>
              </Button>
              <Button
                variant={isDeploymentsPage ? 'default' : 'ghost'}
                onClick={() => {
                  navigate('/deployments');
                  onTabChange?.('deployments');
                }}
                className="gap-2"
              >
                <Zap className="w-4 h-4" />
                <span className="hidden sm:inline">Deployments</span>
              </Button>
              <Button
                variant={isMembersPage ? 'default' : 'ghost'}
                onClick={() => navigate('/members')}
                className="gap-2"
              >
                <Users className="w-4 h-4" />
                <span className="hidden sm:inline">Members</span>
              </Button>
              <Button
                variant={isSpacesPage ? 'default' : 'ghost'}
                onClick={() => navigate('/spaces')}
                className="gap-2"
              >
                <Boxes className="w-4 h-4" />
                <span className="hidden sm:inline">Spaces</span>
              </Button>
            </div>
            {/* Config button */}
            <Button
              variant="ghost"
              className="gap-2 ml-2"
              onClick={() => navigate('/settings')}
              title="Update password"
            >
              <Settings className="w-5 h-5" />
              <span className="hidden sm:inline">Config</span>
            </Button>
            {/* Logout button */}
            <Button
              variant="ghost"
              className="gap-2 ml-2"
              onClick={() => {
                // TODO: call logout logic
                navigate('/login');
              }}
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
