import { useCallback, useState } from 'react';
import { DashboardStats } from '@/components/dashboard-stats';
import { DeploymentsTracker } from '@/components/deployments-tracker';
import { ReposTable } from '@/components/repos-table';
import type {
  AssociateClickUpSpaceRequest,
  ClickUpMemberRole,
  ClickUpSpaceRegisterDTO,
  ClickUpSpaceUpdateDTO,
  CreateSpaceRequest,
  DeploymentDTO,
  GitRepoCreateDTO,
  GitRepoUpdateDTO,
  MemberCreateDTO,
  MemberUpdateDTO,
} from '@/api/api';
import { deploymentService } from '@/services/deployment-service';
import { useNavigate } from 'react-router-dom';
import { MembersTable } from '@/components/members-table';
import { ClickUpSpacesTable } from '@/components/clickup-spaces-table';
import { showSuccessToast } from '@/components/global-toaster';
import { defaultOnError, withErrorHandling } from '@/services/api-error';
import { useUpdateClickUpSpace } from '@/hooks/clickup-space-hooks/use-update-clickup-space';
import { useDeleteClickUpSpace } from '@/hooks/clickup-space-hooks/use-delete-clickup-space';
import { useMembers } from '@/hooks/member-hooks/use-members';
import { useUpdateMember } from '@/hooks/member-hooks/use-update-member';
import { useDeleteMember } from '@/hooks/member-hooks/use-delete-member';
import { useAddMember } from '@/hooks/member-hooks/use-add-member';
import { useRepos } from '@/hooks/repository-hooks/use-repos';
import { useUpdateRepo } from '@/hooks/repository-hooks/use-update-repo';
import { useDeleteRepo } from '@/hooks/repository-hooks/use-delete-repo';
import { useAddRepo } from '@/hooks/repository-hooks/use-add-repo';
import { useCreateClickUpSpace } from '@/hooks/clickup-structure-hooks/use-create-space';
import { useRegisterClickUpSpace } from '@/hooks/clickup-structure-hooks/use-register-space';
import { useAssociateRepoWithClickUpSpace } from '@/hooks/use-association-github-clickup';
import { SpaceTasksViewer } from '@/components/space-tasks-viewer';
import { useRemoveClickUpSpace } from '@/hooks/clickup-space-hooks/use-remove-clickup-sapce';
import { clickUpStructureManagementService } from '@/services/clickup-workspace-management-service';
import { useClickUpSpacesLight } from '@/hooks/clickup-space-hooks/use-clickup-sapce-light';
import { useCurrentUser } from '@/hooks/current-user-hooks/use-current-user';


type WorkspaceSection = 'repos' | 'deployments' | 'members' | 'spaces' | 'space-tasks' | 'backlog-generation';
interface WorkspaceDashboardPageProps {
  activeTab?: WorkspaceSection;
}

export default function DashboardPage({ activeTab = 'repos' }: WorkspaceDashboardPageProps) {
  const { user: currentUser, loading: userLoading } = useCurrentUser();
  const isAdmin = !userLoading && currentUser?.role === 'admin';

  const [isLoadingDeployments, setIsLoadingDeployments] = useState(false);

  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const { repos, loading: reposLoading, isFetching: isFetchingRepos, error: errorRepos, refetch: refetchRepos } = useRepos();
  const { mutateAsync: updateRepo } = useUpdateRepo();
  const { mutateAsync: deleteRepo } = useDeleteRepo();
  const { mutateAsync: addRepo } = useAddRepo();

  const [deployments, setDeployments] = useState<DeploymentDTO[]>([]);
  const [deploymentsError, setDeploymentsError] = useState<string | null>(null);
  const [lastRepoUrl, setLastRepoUrl] = useState<string>('');

  const { spaces: clickUpSpaces, loading: clickupLoading, isFetching: isFetchingClickUpSpaces, error: clickupError, refetch: refreshClickUpData } = useClickUpSpacesLight();
  const { mutateAsync: updateClickUpSpace } = useUpdateClickUpSpace();
  const { mutateAsync: deleteClickUpSpace } = useDeleteClickUpSpace();
  const { mutateAsync: removeClickUpSpace } = useRemoveClickUpSpace();
  const { mutateAsync: createClickUpSpace } = useCreateClickUpSpace();
  const { mutateAsync: registerClickUpSpace } = useRegisterClickUpSpace();

  const { members, loading: membersLoading, isFetching: isFetchingMembers, error: errorMembers, refetch: refetchMembers } = useMembers();
  const { mutateAsync: updateMember } = useUpdateMember();
  const { mutateAsync: deleteMember } = useDeleteMember();
  const { mutateAsync: addMember } = useAddMember();
    

  const { mutateAsync: associateClickUpSpace } = useAssociateRepoWithClickUpSpace();
  const [showNotFoundDialog, setShowNotFoundDialog] = useState(false);
  const [showNameMismatchDialog, setShowNameMismatchDialog] = useState(false);

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

    showSuccessToast('Click up space updated successfully');
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

  const handleRemoveMemberFromClickUp = useCallback(async (memberId: number) => {
    const result = await withErrorHandling(
      () => clickUpStructureManagementService.removeMemberFromWorkspace(memberId),
      'Remove member from ClickUp',
      onError(),
    );
    if (!result)
      return Promise.resolve(false);

    showSuccessToast('Member removed from ClickUp successfully');
    return Promise.resolve(true);
  }, []);

  const handleDeleteClickUpSpace = useCallback(async (id: number) => {
    const result = await deleteClickUpSpace(id);
    
    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('Click up space deleted successfully');
    return Promise.resolve(true);
  }, [deleteClickUpSpace]);

  const handleRemoveClickUpSpace = useCallback(async (id: number) => {
    const result = await removeClickUpSpace(id);
    
    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('Click up space removed successfully');
    return Promise.resolve(true);
  }, [removeClickUpSpace]);

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

  const handleInviteMmeberToClickUp = useCallback(async (email: string, role: ClickUpMemberRole) => {
    const result = await withErrorHandling(
      () => clickUpStructureManagementService.inviteMember({ email, role }),
      'Invite member to ClickUp',
      onError(),
    );
    if (!result)
      return Promise.resolve(false);
    showSuccessToast('Member invited to ClickUp successfully');
    return Promise.resolve(true);
  }, [clickUpStructureManagementService]);

  const handleCreateClickUpSpace = useCallback(async (newSpace: CreateSpaceRequest) => {
    const result = await createClickUpSpace(newSpace);

    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('Click up space created successfully');
    return Promise.resolve(true);
  }, [createClickUpSpace]);

  const handleRegisterClickUpSpace = useCallback(async (newSpace: ClickUpSpaceRegisterDTO) => {
    const result = await registerClickUpSpace(newSpace);

  if (result.ok) {
    showSuccessToast('Click up space registered successfully');
    return Promise.resolve(true);
  }

  if (result.reason === 'not_found') {
    setShowNotFoundDialog(true);
    return Promise.resolve(false);
  }

  if (result.reason === 'name_mismatch') {
    setShowNameMismatchDialog(true);
    return Promise.resolve(false);
  }
  }, [registerClickUpSpace]);

  const handleAssociateClickUpSpace = useCallback(async (association: AssociateClickUpSpaceRequest) => {
    const result = await associateClickUpSpace(association);
    if (!result) 
      return Promise.resolve(false);

    showSuccessToast('GitHub repository associated with click up space successfully');
    return Promise.resolve(true);
  }, [associateClickUpSpace]);

  const handleLoadDeployments = useCallback(async (repoUrl: string) => {
    setIsLoadingDeployments(true);
    setDeploymentsError(null);       
    setLastRepoUrl(repoUrl);

    const deploymentData = await withErrorHandling(
      () => deploymentService.listByRepoUrl(repoUrl),
      'Load deployments',
      onError(),
    );
    if (deploymentData){ 
      setDeployments(deploymentData);
    }else {
      setDeploymentsError('Failed to load deployments.');  
    }

    setIsLoadingDeployments(false);
  }, []);

  return (
    <>
      <DashboardStats 
        repos={repos} 
        members={members} 
        isLoading={reposLoading || membersLoading }
        userLoading={userLoading}
        isAdmin={isAdmin}
      />

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
            isLoading={reposLoading || isFetchingRepos || clickupLoading || isFetchingClickUpSpaces || membersLoading || isFetchingMembers}
            onAssociate={handleAssociateClickUpSpace}
            error={errorRepos}
            refreshRepos={refetchRepos}
          />
        </div>
      )}

      {activeTab === 'deployments' && (
        <div className="animate-in fade-in duration-300">
          <DeploymentsTracker
            deployments={deployments}
            repos={repos}
            onLoadDeployments={handleLoadDeployments}
            isLoading={reposLoading || isFetchingRepos || isLoadingDeployments}
            error={deploymentsError}                            
            onRetry={() => lastRepoUrl && handleLoadDeployments(lastRepoUrl)}
          />
        </div>
      )}

      {activeTab === 'members' && isAdmin && (
        <div className="animate-in fade-in duration-300">
          <MembersTable
            members={members}
            onUpdate={handleUpdateMember}
            onDelete={handleDeleteMember}
            onAdd={handleAddMember}
            onInviteToClickUp={handleInviteMmeberToClickUp}
            onRemoveFromClickUp={handleRemoveMemberFromClickUp}
            isLoading={membersLoading || isFetchingMembers} 
            error={errorMembers}
            refetchMembers={refetchMembers}
          />
        </div>
      )}

      {activeTab === 'spaces' && (
        <div className="animate-in fade-in duration-300">
          <ClickUpSpacesTable
            spaces={clickUpSpaces}
            onUpdate={handleUpdateClickUpSpace}
            onDelete={handleDeleteClickUpSpace}
            onRemove={handleRemoveClickUpSpace}
            onCreate={handleCreateClickUpSpace}
            onRegister={handleRegisterClickUpSpace}
            isLoading={clickupLoading || isFetchingClickUpSpaces || reposLoading || isFetchingRepos } 
            showNotFoundDialog={showNotFoundDialog}
            onNotFoundDialogChange={setShowNotFoundDialog}
            showNameMismatchDialog={showNameMismatchDialog}
            onNameMismatchDialogChange={setShowNameMismatchDialog}
            repositories={repos}
            onAssociate={handleAssociateClickUpSpace}
            error={clickupError}
            refetchSpaces={refreshClickUpData}
          />
        </div>
      )}
      {activeTab === 'space-tasks' && (
        <div className="animate-in fade-in duration-300">
          <SpaceTasksViewer />
        </div>
      )}
    </>
  );
}

