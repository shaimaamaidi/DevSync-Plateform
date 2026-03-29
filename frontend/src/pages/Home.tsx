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

interface HomePageProps {
  activeTab?: 'repos' | 'deployments';
}

export default function HomePage({ activeTab: initialTab }: HomePageProps) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [activeTab, setActiveTab] = useState<'repos' | 'deployments'>(initialTab || 'repos');
  const [repos, setRepos] = useState<GitRepoDetailDTO[]>([]);
  const [deployments, setDeployments] = useState<DeploymentDTO[]>([]);
  const [clickUpSpaces, setClickUpSpaces] = useState<ClickUpSpaceLightDTO[]>([]);
  const [members, setMembers] = useState<MemberDTO[]>([]);


  useReactEffect(() => {
    if (pathname === '/repositories' && activeTab !== 'repos') {
      setActiveTab('repos');
    } else if (pathname === '/deployments' && activeTab !== 'deployments') {
      setActiveTab('deployments');
    }
    // eslint-disable-next-line
  }, [pathname]);

  // Navigue lors du changement d'onglet
  const handleTabChange = (tab: 'repos' | 'deployments') => {
    setActiveTab(tab);
    if (tab === 'repos') {
      navigate('/repositories');
    } else {
      navigate('/deployments');
    }
  };

  useEffect(() => {
    let isActive = true;

    const loadData = async () => {
      const [reposData, spacesData, membersData] = await Promise.all([
        repoService.getAllReposWithDetails(),
        clickUpService.getAllSpacesLight(),
        memberService.getAllWithRepos(),
      ]);

      if (!isActive) return;

      setRepos(reposData);
      setClickUpSpaces(spacesData);
      setMembers(membersData.map(memberService.mapToMemberDTO));
    };

    loadData();

    return () => {
      isActive = false;
    };
  }, []);

  const handleUpdateRepo = useCallback(async (updatedRepo: GitRepoDetailDTO) => {
    const nextRepo = await repoService.updateRepo(updatedRepo);
    if (!nextRepo) return;
    setRepos((prevRepos) =>
      prevRepos.map((repo) => (repo.id === nextRepo.id ? nextRepo : repo))
    );
  }, []);

  const handleDeleteRepo = useCallback(async (id: number) => {
    const deleted = await repoService.deleteRepo(id);
    if (!deleted) return;
    setRepos((prevRepos) => prevRepos.filter((repo) => repo.id !== id));
  }, []);

  const handleAddRepo = useCallback(async (newRepo: GitRepoDetailDTO) => {
    const createdRepo = await repoService.createRepo(newRepo);
    if (!createdRepo) return;
    setRepos((prevRepos) => [...prevRepos, createdRepo]);
  }, []);

  const handleLoadDeployments = useCallback(async (repoUrl: string) => {
    const deploymentData = await deploymentService.listByRepoUrl(repoUrl);
    setDeployments(deploymentData);
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation activeTab={activeTab} onTabChange={handleTabChange} />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <DashboardStats repos={repos} deployments={deployments} />

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
      </main>

      <AppFooter />
    </div>
  );
}
