import { useCallback, useEffect, useMemo, useState } from 'react';
import { DashboardStats } from '@/components/dashboard-stats';
import { DeploymentsTracker } from '@/components/deployments-tracker';
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
import { useNavigate } from 'react-router-dom';
import { MembersTable } from '@/components/members-table';
import { ClickUpSpacesTable } from '@/components/clickup-spaces-table';
import { showSuccessToast } from '@/components/global-toaster';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';


type WorkspaceSection = 'repos' | 'deployments' | 'members' | 'spaces' | 'backlog-generation';
interface WorkspaceDashboardPageProps {
  activeTab?: WorkspaceSection;
}

function Dashboard({ activeTab = 'repos' }: WorkspaceDashboardPageProps) {
  const [isLoading, setIsLoading] = useState(true);

  const navigate = useNavigate();
  const [repos, setRepos] = useState<GitRepoDetailDTO[]>([]);
  const [deployments, setDeployments] = useState<DeploymentDTO[]>([]);
  const [clickUpSpaces, setClickUpSpaces] = useState<ClickUpSpaceLightDTO[]>([]);
  const [members, setMembers] = useState<MemberDTO[]>([]);

  const onError = useMemo(() => defaultOnError(navigate), [navigate]);


  const refreshAllData = useCallback(async () => {
    setIsLoading(true);

    const [reposData, spacesData, membersData] = await Promise.all([
      withErrorHandling(() => repoService.getAllReposWithDetails(), 'Load repositories', onError),
      withErrorHandling(() => clickUpService.getAllSpacesLight(), 'Load ClickUp spaces', onError),
      withErrorHandling(() => memberService.getAllWithRepos(), 'Load members', onError),
    ]);
    if (reposData) 
      setRepos(reposData);
    if (spacesData) 
      setClickUpSpaces(spacesData);
    if (membersData) 
      setMembers(membersData.map(memberService.mapToMemberDTO));

    setIsLoading(false);
  }, []);

  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);

  const handleUpdateRepo = useCallback(async (updatedRepo: GitRepoUpdateDTO) => {
    const result = await withErrorHandling(
      () => repoService.updateRepo(updatedRepo),
      'Update repository',
      onError,
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
      onError,
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
      onError,
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
      onError,
    );
    if (!result) return;
    await refreshAllData();
    showSuccessToast('Repository deleted successfully');
  }, [refreshAllData]);

  const handleDeleteMember = useCallback(async (id: number) => {
    const result = await withErrorHandling(
      () => memberService.deleteMember(id),
      'Delete member',
      onError,
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
      onError,
    );
    if (!result) return;
    await refreshAllData();
    showSuccessToast('ClickUp space deleted successfully');
  }, [refreshAllData]);

  const handleAddRepo = useCallback(async (newRepo: GitRepoCreateDTO) => {
    const result = await withErrorHandling(
      () => repoService.createRepo(newRepo),
      'Create repository',
      onError,
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
      onError,
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
      onError,
    );
    if (!result) 
      return Promise.resolve(false);
    await refreshAllData();
    showSuccessToast('ClickUp space created successfully');
    return Promise.resolve(true);
  }, [refreshAllData]);

  const handleLoadDeployments = useCallback(async (repoUrl: string) => {
    setIsLoading(true);

    const deploymentData = await withErrorHandling(
      () => deploymentService.listByRepoUrl(repoUrl),
      'Load deployments',
      onError,
    );
    if (deploymentData) 
      setDeployments(deploymentData);

    setIsLoading(false);
  }, []);

  return (
    <>
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
            isLoading={isLoading}
            />
        </div>
      )}

      {activeTab === 'deployments' && (
        <div className="animate-in fade-in duration-300">
          <DeploymentsTracker
            deployments={deployments}
            repos={repos}
            onLoadDeployments={handleLoadDeployments}
            isLoading={isLoading}
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
            isLoading={isLoading} 
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
            isLoading={isLoading} 
            />
        </div>
      )}
    </>
  );
}

export default Dashboard;
