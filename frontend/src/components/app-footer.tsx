import { GitBranch, Heart, Info } from 'lucide-react';

export function AppFooter() {
  return (
    <footer className="border-t border-border bg-card mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
              <GitBranch className="w-5 h-5" />
              DevOps Manager
            </h3>
            <p className="text-sm text-muted-foreground">
              A comprehensive platform for managing GitHub repositories, team members, and deployments with ClickUp integration.
            </p>
          </div>

          {/* Features */}
          <div>
            <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
              <Info className="w-5 h-5" />
              Features
            </h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>- Repository Management</li>
              <li>- Team Member Tracking</li>
              <li>- Deployment Monitoring</li>
              <li>- ClickUp Space Integration</li>
            </ul>
          </div>

          {/* Status */}
          <div>
            <h3 className="font-semibold text-foreground mb-3">Status</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span className="text-muted-foreground">All systems operational</span>
              </div>
              <p className="text-xs text-muted-foreground mt-3">
                Made with <Heart className="w-3 h-3 inline text-red-500" /> for developers
              </p>
            </div>
          </div>
        </div>

        <div className="border-t border-border mt-8 pt-8">
          <p className="text-center text-xs text-muted-foreground">
            (c) {new Date().getFullYear()} DevOps Manager. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
