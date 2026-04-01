
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import { RequireAuth } from './components/RequireAuth';
import HomePage from './pages/Home';
import NotFoundPage from './pages/NotFound';
import LoginPage from './pages/Login';
import { GlobalApiAlert } from './components/global-api-alert';
import { GlobalSuccessToaster } from './components/global-success-toaster';
import SettingsPage from './pages/Settings';

export default function App() {
  return (
    <>
      <GlobalApiAlert />
      <GlobalSuccessToaster />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/repositories" replace />} />
          <Route path="/repositories" element={<RequireAuth><HomePage activeTab="repos" /></RequireAuth>} />
          <Route path="/deployments" element={<RequireAuth><HomePage activeTab="deployments" /></RequireAuth>} />
          <Route path="/members" element={<RequireAuth><HomePage activeTab="members" /></RequireAuth>} />
          <Route path="/spaces" element={<RequireAuth><HomePage activeTab="spaces" /></RequireAuth>} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/settings" element={<RequireAuth><SettingsPage /></RequireAuth>} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}
