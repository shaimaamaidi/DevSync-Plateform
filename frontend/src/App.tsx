import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import { RequireAuth } from './components/require-auth';
import { AxiosErrorBoundary } from './components/axios-error-boundary';
import { GlobalToaster } from './components/global-toaster';
import { RootLayout } from './components/root-layout';
import NotFoundPage from './pages/not-found-page';
import SettingsPage from './pages/settings-page';
import ProfilePage from './pages/profile-page';
import Dashboard from './pages/dashboard-page';
import BacklogGenerationChatPage from './pages/backlog-generation-chat-page';
import MeetingTaskGenerationPage from './pages/meeting-task-generation-page';
import BacklogTaskGenerationPage from './pages/backlog-task-generation-page';
import ProjectInsightsPage from './pages/project-insights-page';
import LoginPage from './pages/login-page';
import { RequireAdminRoute } from './components/require-admin-route';

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
            <Route path="/members" element={
              <RequireAdminRoute>
                <Dashboard activeTab="members" />
              </RequireAdminRoute>
            } />
            <Route path="/spaces" element={<Dashboard activeTab="spaces" />} />
            <Route path="/spaces/:spaceId/tasks" element={<Dashboard activeTab="space-tasks" />} />
            <Route path="/backlog-generation-chat" element={<BacklogGenerationChatPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/meeting-tasks" element={<MeetingTaskGenerationPage />} />
            <Route path="/backlog-tasks" element={<BacklogTaskGenerationPage />} />
            <Route path="/project-insights" element={<ProjectInsightsPage />} />
          </Route>
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}
