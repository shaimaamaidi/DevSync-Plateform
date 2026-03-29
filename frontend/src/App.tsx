
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import ClickUpSpacesPage from './pages/ClickUpSpaces';
import HomePage from './pages/Home';
import MembersPage from './pages/Members';
import NotFoundPage from './pages/NotFound';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/repositories" replace />} />
        <Route path="/repositories" element={<HomePage activeTab="repos" />} />
        <Route path="/deployments" element={<HomePage activeTab="deployments" />} />
        <Route path="/members" element={<MembersPage />} />
        <Route path="/spaces" element={<ClickUpSpacesPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
