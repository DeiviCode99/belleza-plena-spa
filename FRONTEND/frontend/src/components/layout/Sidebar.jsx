import { useNavigate, useLocation } from 'react-router-dom';
import { Calendar, Users, FileText, BarChart3, Settings, FileBarChart } from 'lucide-react';
import logo from '../../assets/icon.png';

const menuItems = [
  { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
  { path: '/citas', label: 'Citas', icon: Calendar },
  { path: '/pacientes', label: 'Pacientes', icon: Users },
  { path: '/historias-clinicas', label: 'Historias Clínicas', icon: FileText },
  { path: '/reportes', label: 'Reportes', icon: FileBarChart },
  { path: '/configuracion', label: 'Configuración', icon: Settings },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="w-64 bg-gradient-to-b from-emerald-50 to-teal-50 border-r border-emerald-100 h-screen flex flex-col">
      <div className="p-6 border-b border-emerald-100">
        <div className="flex space-x-3">
          <img src={logo} alt="Logo" />
        </div>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <li key={item.path}>
                <button
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                    isActive
                      ? 'bg-emerald-500 text-white shadow-lg transform scale-105'
                      : 'text-gray-700 hover:bg-emerald-100 hover:text-emerald-700'
                  }`}
                >
                  <IconComponent className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-emerald-100">
        <div className="text-xs text-gray-500 text-center">
          <p>SerenSpa Management</p>
          <p>v1.0.0</p>
        </div>
      </div>
    </div>
  );
}
