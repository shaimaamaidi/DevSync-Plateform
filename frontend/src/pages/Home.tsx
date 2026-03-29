import { useCallback, useEffect, useState } from 'react';
import { AppFooter } from '@/components/app-footer';
import { DashboardStats } from '@/components/dashboard-stats';
import { DeploymentsTracker } from '@/components/deployments-tracker';
import { Navigation } from '@/components/navigation';
import { ReposTable } from '@/components/repos-table';
import type {
  ClickUpSpaceLightDTO,
  DeploymentDTO,
  GitRepoDetailDTO,
  MemberDTO,
} from '@/api/api';
import { clickUpService } from '@/services/clickup-service';
import { deploymentService } from '@/services/deployment-service';
import { memberService } from '@/services/member-service';
import { repoService } from '@/services/repo-service';


import { useEffect as useReactEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MembersTable } from '@/components/members-table';
import { ClickUpSpacesTable } from '@/components/clickup-spaces-table';
import { showSuccessToast } from '@/components/global-success-toaster';


type HomeTab = 'repos' | 'deployments' | 'members' | 'spaces';
interface HomePageProps {
  activeTab?: HomeTab;
}

function HomePage({ activeTab: initialTab }: HomePageProps) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [activeTab, setActiveTab] = useState<HomeTab>(initialTab || 'repos');
  const [repos, setRepos] = useState<GitRepoDetailDTO[]>([]);
  const [deployments, setDeployments] = useState<DeploymentDTO[]>([]);
  const [clickUpSpaces, setClickUpSpaces] = useState<ClickUpSpaceLightDTO[]>([]);
  const [members, setMembers] = useState<MemberDTO[]>([]);

  useReactEffect(() => {
    if (pathname === '/repositories' && activeTab !== 'repos') {
      setActiveTab('repos');
    } else if (pathname === '/deployments' && activeTab !== 'deployments') {
      setActiveTab('deployments');
    } else if (pathname === '/members' && activeTab !== 'members') {
      setActiveTab('members');
    } else if ((pathname === '/spaces' || pathname === '/clickup-spaces') && activeTab !== 'spaces') {
      setActiveTab('spaces');
    }
    // eslint-disable-next-line
  }, [pathname]);

  // Navigue lors du changement d'onglet
  const handleTabChange = (tab: HomeTab) => {
    setActiveTab(tab);
    if (tab === 'repos') {
      navigate('/repositories');
    } else if (tab === 'deployments') {
      navigate('/deployments');
    } else if (tab === 'members') {
      navigate('/members');
    } else if (tab === 'spaces') {
      navigate('/spaces');
    }
  };


  // Fonction centralisée pour refresh toutes les données
  const refreshAllData = useCallback(async () => {
    const [reposData, spacesData, membersData] = await Promise.all([
      repoService.getAllReposWithDetails(),
      clickUpService.getAllSpacesLight(),
      memberService.getAllWithRepos(),
    ]);
    setRepos(reposData);
    setClickUpSpaces(spacesData);
    setMembers(membersData.map(memberService.mapToMemberDTO));
  }, []);

  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);



  const handleUpdateRepo = useCallback(async (updatedRepo: GitRepoDetailDTO) => {
    const nextRepo = await repoService.updateRepo(updatedRepo);
    if (!nextRepo) return;
    await refreshAllData();
    showSuccessToast('Repository updated successfully');
  }, [refreshAllData]);

  const handleDeleteRepo = useCallback(async (id: number) => {
    const deleted = await repoService.deleteRepo(id);
    if (!deleted) return;
    await refreshAllData();
    showSuccessToast('Repository deleted successfully');
  }, [refreshAllData]);

  const handleAddRepo = useCallback(async (newRepo: GitRepoDetailDTO) => {
    const createdRepo = await repoService.createRepo(newRepo);
    if (!createdRepo) return;
    await refreshAllData();
    showSuccessToast('Repository created successfully');
  }, [refreshAllData]);

  const handleLoadDeployments = useCallback(async (repoUrl: string) => {
    const deploymentData = await deploymentService.listByRepoUrl(repoUrl);
    setDeployments(deploymentData);
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation activeTab={activeTab} onTabChange={handleTabChange} />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <DashboardStats repos={repos} deployments={deployments} members={members} />

        <div className="my-8 border-t border-border" />

        {activeTab === 'repos' && (
          <div className="animate-in fade-in duration-300">
            <ReposTable
              repos={repos}
              clickUpSpaces={clickUpSpaces}
              availableMembers={members}
              onUpdate={handleUpdateRepo}
              onDelete={handleDeleteRepo}
              onAdd={handleAddRepo}
            />
          </div>
        )}

        {activeTab === 'deployments' && (
          <div className="animate-in fade-in duration-300">
            <DeploymentsTracker
              deployments={deployments}
              repos={repos}
              onLoadDeployments={handleLoadDeployments}
            />
          </div>
        )}

        {activeTab === 'members' && (
          <div className="animate-in fade-in duration-300">
            <MembersTable
              members={members}
              onUpdate={async (member) => {
                const nextMember = await memberService.updateMember(member);
                if (!nextMember) return;
                await refreshAllData();
                showSuccessToast('Member updated successfully');
              }}
              onDelete={async (id) => {
                const deleted = await memberService.deleteMember(id);
                if (!deleted) return;
                await refreshAllData();
                showSuccessToast('Member deleted successfully');
              }}
              onAdd={async (newMember) => {
                const createdMember = await memberService.createMember(newMember);
                if (!createdMember) return;
                await refreshAllData();
                showSuccessToast('Member created successfully');
              }}
            />
          </div>
        )}

        {activeTab === 'spaces' && (
          <div className="animate-in fade-in duration-300">
            <ClickUpSpacesTable
              spaces={clickUpSpaces}
              onUpdate={async (space) => {
                const nextSpace = await clickUpService.updateSpace(space);
                if (!nextSpace) return;
                await refreshAllData();
                showSuccessToast('ClickUp space updated successfully');
              }}
              onDelete={async (id) => {
                const deleted = await clickUpService.deleteSpace(id);
                if (!deleted) return;
                await refreshAllData();
                showSuccessToast('ClickUp space deleted successfully');
              }}
              onAdd={async (newSpace) => {
                const createdSpace = await clickUpService.createSpace(newSpace);
                if (!createdSpace) return;
                await refreshAllData();
                showSuccessToast('ClickUp space created successfully');
              }}
            />
          </div>
        )}
      </main>

      <AppFooter />
    </div>
  );
}

export default HomePage;
