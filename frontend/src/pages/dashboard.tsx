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
  GitRepoUpdateDTO,
  MemberCreateDTO,
  MemberUpdateDTO,
} from '@/api/api';
import { clickUpService } from '@/services/clickup-service';
import { deploymentService } from '@/services/deployment-service';
import { useNavigate } from 'react-router-dom';
import { MembersTable } from '@/components/members-table';
import { ClickUpSpacesTable } from '@/components/clickup-spaces-table';
import { showSuccessToast } from '@/components/global-toaster';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { useUpdateClickUpSpace } from '@/hooks/clickup-space-hooks/use-update-clickup-space';
import { useDeleteClickUpSpace } from '@/hooks/clickup-space-hooks/use-delete-clickup-space';
import { useAddClickUpSpace } from '@/hooks/clickup-space-hooks/use-add-clickup-space';
import { useMembers } from '@/hooks/member-hooks/use-members';
import { useUpdateMember } from '@/hooks/member-hooks/use-update-member';
import { useDeleteMember } from '@/hooks/member-hooks/use-delete-member';
import { useAddMember } from '@/hooks/member-hooks/use-add-member';
import { useRepos } from '@/hooks/repository-hooks/use-repos';
import { useUpdateRepo } from '@/hooks/repository-hooks/use-update-repo';
import { useDeleteRepo } from '@/hooks/repository-hooks/use-delete-repo';
import { useAddRepo } from '@/hooks/repository-hooks/use-add-repo';


type WorkspaceSection = 'repos' | 'deployments' | 'members' | 'spaces' | 'backlog-generation';
interface WorkspaceDashboardPageProps {
  activeTab?: WorkspaceSection;
}

function Dashboard({ activeTab = 'repos' }: WorkspaceDashboardPageProps) {
  const [isLoadingDeployments, setIsLoadingDeployments] = useState(false);

  const navigate = useNavigate();

  const [deployments, setDeployments] = useState<DeploymentDTO[]>([]);
  const [clickUpSpaces, setClickUpSpaces] = useState<ClickUpSpaceLightDTO[]>([]);
  const [clickupLoading, setClickupLoading] = useState(true);

  const { repos, loading: reposLoading } = useRepos();
  const { mutateAsync: updateRepo } = useUpdateRepo();
  const { mutateAsync: deleteRepo } = useDeleteRepo();
  const { mutateAsync: addRepo } = useAddRepo();

  const { members, loading: membersLoading } = useMembers();
  const { mutateAsync: updateMember } = useUpdateMember();
  const { mutateAsync: deleteMember } = useDeleteMember();
  const { mutateAsync: addMember } = useAddMember();
    
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const { mutateAsync: updateClickUpSpace } = useUpdateClickUpSpace();
  const { mutateAsync: deleteClickUpSpace } = useDeleteClickUpSpace();
  const { mutateAsync: addClickUpSpace } = useAddClickUpSpace();

  const refreshClickUpData = useCallback(async () => {
    setClickupLoading(true);

    const [spacesData] = await Promise.all([
      withErrorHandling(() => clickUpService.getAllSpacesLight(), 'Load ClickUp spaces', onError),
    ]);

    if (spacesData) 
      setClickUpSpaces(spacesData);

    setClickupLoading(false);
  }, []);

  useEffect(() => {
    refreshClickUpData();
  }, [refreshClickUpData]);

  const handleUpdateRepo = useCallback(async (updatedRepo: GitRepoUpdateDTO) => {
    const result = await updateRepo(updatedRepo);

    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('Repository updated successfully');
    return Promise.resolve(true);
  }, [updateRepo]);

  const handleUpdateMember = useCallback(async (member: MemberUpdateDTO) => {
    const result = await updateMember(member)
    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('Member updated successfully');
    return Promise.resolve(true);
  }, [updateMember]);
  
  const handleUpdateClickUpSpace = useCallback(async (space: ClickUpSpaceUpdateDTO) => {
    const result = await updateClickUpSpace(space);
    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('ClickUp space updated successfully');
    return Promise.resolve(true);
  }, [updateClickUpSpace]);

  
  const handleDeleteRepo = useCallback(async (id: number) => {
    const result = await deleteRepo(id);

    if (!result) return;

    showSuccessToast('Repository deleted successfully');
  }, [deleteRepo]);

  const handleDeleteMember = useCallback(async (id: number) => {
    const result = await deleteMember(id);

    if (!result)
      return;

    showSuccessToast('Member deleted successfully');    
  }, [deleteMember]);

  const handleDeleteClickUpSpace = useCallback(async (id: number) => {
    const result = await deleteClickUpSpace(id);
    
    if (!result) 
      return;

    showSuccessToast('ClickUp space deleted successfully');
  }, [deleteClickUpSpace]);

  const handleAddRepo = useCallback(async (newRepo: GitRepoCreateDTO) => {
    const result = await addRepo(newRepo);

    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('Repository created successfully');
    return Promise.resolve(true);
  }, [addRepo]);

  const handleAddMember = useCallback(async (newMember: MemberCreateDTO) => {
    const result = await addMember(newMember);

    if (!result)
      return Promise.resolve(false);

    showSuccessToast('Member created successfully');
    return Promise.resolve(true);
  }, [addMember]);

  const handleAddClickUpSpace = useCallback(async (newSpace: ClickUpSpaceCreateDTO) => {
    const result = await addClickUpSpace(newSpace);

    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('ClickUp space created successfully');
    return Promise.resolve(true);
  }, [addClickUpSpace]);

  const handleLoadDeployments = useCallback(async (repoUrl: string) => {
    setIsLoadingDeployments(true);

    const deploymentData = await withErrorHandling(
      () => deploymentService.listByRepoUrl(repoUrl),
      'Load deployments',
      onError,
    );
    if (deploymentData) 
      setDeployments(deploymentData);

    setIsLoadingDeployments(false);
  }, []);

  return (
    <>
      <DashboardStats repos={repos} deployments={deployments} members={members} isLoading={reposLoading || membersLoading || isLoadingDeployments}/>

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
            isLoading={reposLoading || clickupLoading || membersLoading}
            />
        </div>
      )}

      {activeTab === 'deployments' && (
        <div className="animate-in fade-in duration-300">
          <DeploymentsTracker
            deployments={deployments}
            repos={repos}
            onLoadDeployments={handleLoadDeployments}
            isLoading={reposLoading || isLoadingDeployments}
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
            isLoading={membersLoading} 
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
            isLoading={clickupLoading} 
            />
        </div>
      )}
    </>
  );
}

export default Dashboard;
