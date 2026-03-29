
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import HomePage from './pages/Home';
import NotFoundPage from './pages/NotFound';
import { GlobalApiAlert } from './components/global-api-alert';
import { GlobalSuccessToaster } from './components/global-success-toaster';

export default function App() {
  return (
    <>
      <GlobalApiAlert />
      <GlobalSuccessToaster />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/repositories" replace />} />
          <Route path="/repositories" element={<HomePage activeTab="repos" />} />
          <Route path="/deployments" element={<HomePage activeTab="deployments" />} />
          <Route path="/members" element={<HomePage activeTab="members" />} />
          <Route path="/spaces" element={<HomePage activeTab="spaces" />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}
