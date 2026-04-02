import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { GitBranch, Zap, Users, Boxes, LogOut, Settings } from 'lucide-react';
import { authService } from '@/services/auth-service';



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
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
          >
            <div className="w-9 h-9 rounded-[10px] bg-foreground flex items-center justify-center">
              <div className="grid grid-cols-2 gap-[3px] w-[18px]">
                <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-90" />
                <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-60" />
                <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-60" />
                <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-30" />
              </div>
            </div>
            <div className="text-left">
              <h1 className="text-lg font-bold text-foreground tracking-tight">GitHub & Deployments</h1>
            </div>
          </button>

          <div className="flex items-center gap-2 ml-auto">
              <div className="flex items-center gap-1 p-1 bg-muted rounded-lg ml-10">
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
            <Button
              variant="ghost"
              className="gap-2 ml-2"
              onClick={() => navigate('/profile')}
              title="Profile"
            >
              <Settings className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              className="gap-2 ml-2"
              onClick={() => {
                authService.logout();
                navigate('/login');
              }}
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
