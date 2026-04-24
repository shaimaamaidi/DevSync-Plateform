import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import { RequireAuth } from './components/RequireAuth';
import HomePage from './pages/Home';
import NotFoundPage from './pages/NotFound';
import LoginPage from './pages/Login';
import { GlobalSuccessToaster } from './components/global-success-toaster';
import { GlobalErrorToaster } from './components/global-error-toaster';
import SettingsPage from './pages/Settings';
import ProfilePage from './pages/Profile';

export default function App() {
  return (
    <>
      <GlobalSuccessToaster />
      <GlobalErrorToaster/>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/repositories" replace />} />
          <Route path="/repositories" element={<RequireAuth><HomePage activeTab="repos" /></RequireAuth>} />
          <Route path="/deployments" element={<RequireAuth><HomePage activeTab="deployments" /></RequireAuth>} />
          <Route path="/members" element={<RequireAuth><HomePage activeTab="members" /></RequireAuth>} />
          <Route path="/spaces" element={<RequireAuth><HomePage activeTab="spaces" /></RequireAuth>} />
          <Route path="/backlog-generation-chat" element={<RequireAuth><HomePage activeTab="backlog-generation" /></RequireAuth>} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/settings" element={<RequireAuth><SettingsPage /></RequireAuth>} />
          <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}
