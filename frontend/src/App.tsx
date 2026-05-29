import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import { RequireAuth } from './components/RequireAuth';
import NotFoundPage from './pages/NotFound';
import LoginPage from './pages/Login';
import SettingsPage from './pages/Settings';
import ProfilePage from './pages/Profile';
import { GlobalToaster } from './components/global-toaster';
import { RootLayout } from './components/root-layout';
import Dashboard from './pages/dashboard';
import { BacklogGenerationChat } from './pages/backlog-generation-chat';
import { MeetingTaskManager } from './pages/meeting-task-generation';
import { AxiosErrorBoundary } from './components/axios-error-boundary';
import { BacklogTaskManager } from './pages/backlog-task-generation';
import { ProjectInsights } from './pages/project-insights';

export default function App() {
  return (
    <>
      <BrowserRouter>
        <GlobalToaster />
        <AxiosErrorBoundary />
        <Routes>
           <Route element={<RequireAuth><RootLayout /></RequireAuth>}>
            <Route path="/" element={<Navigate to="/repositories" replace />} />
            <Route path="/repositories" element={<Dashboard activeTab="repos" />} />
            <Route path="/deployments" element={<Dashboard activeTab="deployments" />} />
            <Route path="/members" element={<Dashboard activeTab="members" />} />
            <Route path="/spaces" element={<Dashboard activeTab="spaces" />} />
            <Route path="/spaces/:spaceId/tasks" element={<Dashboard activeTab="space-tasks" />} />
            <Route path="/backlog-generation-chat" element={<BacklogGenerationChat />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/meeting-tasks" element={<MeetingTaskManager />} />
            <Route path="/backlog-tasks" element={<BacklogTaskManager />} />
            <Route path="/project-insights" element={<ProjectInsights />} />
          </Route>
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}
