import { BrowserRouter, Route, Routes } from 'react-router-dom';
import ClickUpSpacesPage from './pages/ClickUpSpaces';
import HomePage from './pages/Home';
import MembersPage from './pages/Members';
import NotFoundPage from './pages/NotFound';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/members" element={<MembersPage />} />
        <Route path="/clickup-spaces" element={<ClickUpSpacesPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
