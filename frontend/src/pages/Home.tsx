import { useCallback, useEffect, useState } from 'react';
import { AppFooter } from '@/components/app-footer';
import { DashboardStats } from '@/components/dashboard-stats';
import { DeploymentsTracker } from '@/components/deployments-tracker';
import { Navigation } from '@/components/navigation';
import { ReposTable } from '@/components/repos-table';
import type {
  ClickUpSpaceCreateDTO,
  ClickUpSpaceLightDTO,
  ClickUpSpaceUpdateDTO,
  DeploymentDTO,
  GitRepoCreateDTO,
  GitRepoDetailDTO,
  GitRepoUpdateDTO,
  MemberCreateDTO,
  MemberDTO,
  MemberUpdateDTO,
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
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { BacklogGenerationChat } from '@/components/backlog-generation-chat';


type HomeTab = 'repos' | 'deployments' | 'members' | 'spaces' | 'backlog-generation';
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
    } else if (pathname === '/backlog-generation-chat' && activeTab !== 'backlog-generation') {
      setActiveTab('backlog-generation');
    }
  }, [pathname]);

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
    } else if (tab === 'backlog-generation') {
      navigate('/backlog-generation-chat');
    }
  };


  const refreshAllData = useCallback(async () => {
    const [reposData, spacesData, membersData] = await Promise.all([
      withErrorHandling(() => repoService.getAllReposWithDetails(), 'Load repositories', defaultOnError(navigate)),
      withErrorHandling(() => clickUpService.getAllSpacesLight(), 'Load ClickUp spaces', defaultOnError(navigate)),
      withErrorHandling(() => memberService.getAllWithRepos(), 'Load members', defaultOnError(navigate)),
    ]);
    if (reposData) 
      setRepos(reposData);
    if (spacesData) 
      setClickUpSpaces(spacesData);
    if (membersData) 
      setMembers(membersData.map(memberService.mapToMemberDTO));
  }, []);

  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);

  const handleUpdateRepo = useCallback(async (updatedRepo: GitRepoUpdateDTO) => {
    const result = await withErrorHandling(
      () => repoService.updateRepo(updatedRepo),
      'Update repository',
      defaultOnError(navigate),
    );
    if (!result) 
      return Promise.resolve(false);
    await refreshAllData();
    showSuccessToast('Repository updated successfully');
    return Promise.resolve(true);
  }, [refreshAllData]);

  const handleUpdateMember = useCallback(async (member: MemberUpdateDTO) => {
    const result = await withErrorHandling(
      () => memberService.updateMember(member),
      'Update member',
      defaultOnError(navigate),
  );
  if (!result) 
    return Promise.resolve(false);
  await refreshAllData();
  showSuccessToast('Member updated successfully');
  return Promise.resolve(true);
  }, [refreshAllData]);
  
  const handleUpdateClickUpSpace = useCallback(async (space: ClickUpSpaceUpdateDTO) => {
    const result = await withErrorHandling(
      () => clickUpService.updateSpace(space),
      'Update clickup space',
      defaultOnError(navigate),
    );
    if (!result) 
      return Promise.resolve(false);
    await refreshAllData();
    showSuccessToast('ClickUp space updated successfully');
    return Promise.resolve(true);
  }, [refreshAllData]);

  
  const handleDeleteRepo = useCallback(async (id: number) => {
    const result = await withErrorHandling(
      () => repoService.deleteRepo(id),
      'Delete repository',
      defaultOnError(navigate),
    );
    if (!result) return;
    await refreshAllData();
    showSuccessToast('Repository deleted successfully');
  }, [refreshAllData]);

  const handleDeleteMember = useCallback(async (id: number) => {
    const result = await withErrorHandling(
      () => memberService.deleteMember(id),
      'Delete member',
      defaultOnError(navigate),
    );
    
    if (!result)
      return;
    await refreshAllData();
    showSuccessToast('Member deleted successfully');    
  }, [refreshAllData]);

  const handleDeleteClickUpSpace = useCallback(async (id: number) => {
    const result = await withErrorHandling(
      () => clickUpService.deleteSpace(id),
      'Delete clickup space',
      defaultOnError(navigate),
    );
    if (!result) return;
    await refreshAllData();
    showSuccessToast('ClickUp space deleted successfully');
  }, [refreshAllData]);

  const handleAddRepo = useCallback(async (newRepo: GitRepoCreateDTO) => {
    const result = await withErrorHandling(
      () => repoService.createRepo(newRepo),
      'Create repository',
      defaultOnError(navigate),
    );
    if (!result) 
      return Promise.resolve(false);
    await refreshAllData();
    showSuccessToast('Repository created successfully');
    return Promise.resolve(true);
  }, [refreshAllData]);

  const handleAddMember = useCallback(async (newMember: MemberCreateDTO) => {
    const result = await withErrorHandling(
      () => memberService.createMember(newMember),
      'Create member',
      defaultOnError(navigate),
    );
    if (!result)
      return Promise.resolve(false);
    await refreshAllData();
    showSuccessToast('Member created successfully');
    return Promise.resolve(true);
  }, [refreshAllData]);

  const handleAddClickUpSpace = useCallback(async (newSpace: ClickUpSpaceCreateDTO) => {
    const result = await withErrorHandling(
      () => clickUpService.createSpace(newSpace),
      'Create clickup space',
      defaultOnError(navigate),
    );
    if (!result) 
      return Promise.resolve(false);
    await refreshAllData();
    showSuccessToast('ClickUp space created successfully');
    return Promise.resolve(true);
  }, [refreshAllData]);

  const handleLoadDeployments = useCallback(async (repoUrl: string) => {
    const deploymentData = await withErrorHandling(
      () => deploymentService.listByRepoUrl(repoUrl),
      'Load deployments',
      defaultOnError(navigate),
    );
    if (deploymentData) 
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
              onUpdate={handleUpdateMember}
              onDelete={handleDeleteMember}
              onAdd={handleAddMember}
            />
          </div>
        )}

        {activeTab === 'spaces' && (
          <div className="animate-in fade-in duration-300">
            <ClickUpSpacesTable
              spaces={clickUpSpaces}
              onUpdate={handleUpdateClickUpSpace}
              onDelete={handleDeleteClickUpSpace}
              onAdd={handleAddClickUpSpace}
            />
          </div>
        )}

        {activeTab === 'backlog-generation' && (
          <div className="animate-in fade-in duration-300">
            <BacklogGenerationChat />
          </div>
        )}
      </main>

      <AppFooter />
    </div>
  );
}

export default HomePage;
