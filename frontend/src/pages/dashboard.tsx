import { useCallback, useEffect, useMemo, useState } from 'react';
import { DashboardStats } from '@/components/dashboard-stats';
import { DeploymentsTracker } from '@/components/deployments-tracker';
import { ReposTable } from '@/components/repos-table';
import type {
  AssociateClickUpSpaceRequest,
  ClickUpMemberRole,
  ClickUpSpaceLightDTO,
  ClickUpSpaceRegisterDTO,
  ClickUpSpaceUpdateDTO,
  CreateSpaceRequest,
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
import { defaultOnError } from '@/utils/error-handler';
import { useRemoveClickUpSpace } from '@/hooks/clickup-space-hooks/use-remove-clickup-sapce';
import { clickUpStructureCreationService } from '@/services/clickup-workspace-creation-service';


type WorkspaceSection = 'repos' | 'deployments' | 'members' | 'spaces' | 'space-tasks' | 'backlog-generation';
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
  const { mutateAsync: removeClickUpSpace } = useRemoveClickUpSpace();
  const { mutateAsync: createClickUpSpace } = useCreateClickUpSpace();
  const { mutateAsync: registerClickUpSpace } = useRegisterClickUpSpace();

  const { mutateAsync: associateClickUpSpace } = useAssociateRepoWithClickUpSpace();
  const [showNotFoundDialog, setShowNotFoundDialog] = useState(false);
  const [showNameMismatchDialog, setShowNameMismatchDialog] = useState(false);

  const refreshClickUpData = useCallback(async () => {
    setClickupLoading(true);

    const [spacesData] = await Promise.all([
      withErrorHandling(() => clickUpService.getAllSpacesLight(), 'Load click up spaces', onError),
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
      () => clickUpStructureCreationService.removeMemberFromWorkspace(memberId),
      'Remove member from ClickUp',
      onError
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
      () => clickUpStructureCreationService.inviteMember({ email, role }),
      'Invite member to ClickUp',
      onError
    );
    if (!result)
      return Promise.resolve(false);
    showSuccessToast('Member invited to ClickUp successfully');
    return Promise.resolve(true);
  }, [clickUpStructureCreationService]);

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
            onAssociate={handleAssociateClickUpSpace}
            refreshSpaces={refreshClickUpData}
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
            onInviteToClickUp={handleInviteMmeberToClickUp}
            onRemoveFromClickUp={handleRemoveMemberFromClickUp}
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
            onRemove={handleRemoveClickUpSpace}
            onCreate={handleCreateClickUpSpace}
            onRegister={handleRegisterClickUpSpace}
            isLoading={clickupLoading} 
            showNotFoundDialog={showNotFoundDialog}
            onNotFoundDialogChange={setShowNotFoundDialog}
            showNameMismatchDialog={showNameMismatchDialog}
            onNameMismatchDialogChange={setShowNameMismatchDialog}
            repositories={repos}
            onAssociate={handleAssociateClickUpSpace}
            refreshSpaces={refreshClickUpData}
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

export default Dashboard;
