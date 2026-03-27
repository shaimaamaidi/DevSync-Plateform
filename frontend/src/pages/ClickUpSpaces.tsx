import { useEffect, useState } from 'react';
import { ClickUpSpacesTable } from '@/components/clickup-spaces-table';
import { DashboardStats } from '@/components/dashboard-stats';
import { Navigation } from '@/components/navigation';
import { clickUpService } from '@/services/clickup-service';
import type { ClickUpSpaceLightDTO, DeploymentDTO, GitRepoDetailDTO } from '@/api/api';

export default function ClickUpSpacesPage() {
  const [spaces, setSpaces] = useState<ClickUpSpaceLightDTO[]>([]);
  const [repos] = useState<GitRepoDetailDTO[]>([]);
  const [deployments] = useState<DeploymentDTO[]>([]);

  useEffect(() => {
    let isActive = true;

    const loadSpaces = async () => {
      const spacesData = await clickUpService.getAllSpacesLight();
      if (isActive) {
        setSpaces(spacesData);
      }
    };

    loadSpaces();

    return () => {
      isActive = false;
    };
  }, []);

  const handleUpdate = async (updatedSpace: ClickUpSpaceLightDTO) => {
    const nextSpace = await clickUpService.updateSpace(updatedSpace);
    if (!nextSpace) return;
    setSpaces((prev) => prev.map((s) => (s.id === nextSpace.id ? nextSpace : s)));
  };

  const handleDelete = async (id: number) => {
    const deleted = await clickUpService.deleteSpace(id);
    if (!deleted) return;
    setSpaces((prev) => prev.filter((s) => s.id !== id));
  };

  const handleAdd = async (newSpace: ClickUpSpaceLightDTO) => {
    const createdSpace = await clickUpService.createSpace(newSpace);
    if (!createdSpace) return;
    setSpaces((prev) => [...prev, createdSpace]);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <DashboardStats repos={repos} deployments={deployments} />

        <div className="my-8 border-t border-border" />

        <ClickUpSpacesTable
          spaces={spaces}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
          onAdd={handleAdd}
        />
      </main>
    </div>
  );
}
