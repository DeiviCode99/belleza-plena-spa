import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { ToastContainer } from 'react-toastify';

const PATH_TITLES = {
  '/dashboard': 'Dashboard',
  '/citas': 'Citas',
  '/pacientes': 'Pacientes',
  '/historias-clinicas': 'Historias Clínicas',
  '/reportes': 'Reportes',
  '/configuracion': 'Configuración',
};

export default function Layout() {
  const location = useLocation();
  const title = PATH_TITLES[location.pathname] || 'Dashboard';

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={title} />
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
        <ToastContainer position="top-right" autoClose={2000} />
      </div>
    </div>
  );
}
