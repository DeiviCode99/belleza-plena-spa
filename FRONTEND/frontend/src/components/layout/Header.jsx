import { Bell, Search, User, LogOut, Menu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Header({ title, onMenuToggle }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-gray-200 px-3 sm:px-4 md:px-6 py-3 md:py-4">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-3 min-w-0">
          <button
            onClick={onMenuToggle}
            className="btn-icon lg:hidden p-2 text-gray-600 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
            aria-label="Abrir menú"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="min-w-0">
            <h2 className="text-lg md:text-2xl font-bold text-gray-800 truncate">{title}</h2>
            <p className="text-xs sm:text-sm text-gray-600 hidden sm:block">
              {new Date().toLocaleDateString('es-ES', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-4">
          <div className="relative hidden sm:block">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Buscar..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500 focus:outline-none w-40 md:w-auto"
            />
          </div>

          <button className="btn-icon relative p-2 text-gray-600 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
          </button>

          <div className="items-center gap-2 hidden sm:flex">
            <div className="text-right hidden md:block">
              <p className="text-sm font-medium text-gray-800 truncate max-w-[120px]">{user?.email || 'Usuario'}</p>
              <p className="text-xs text-gray-600">Sistema Principal</p>
            </div>
            <div className="bg-emerald-500 p-2 rounded-full shrink-0">
              <User className="h-4 w-4 md:h-5 md:w-5 text-white" />
            </div>
            <button
              onClick={handleLogout}
              className="btn-icon p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              title="Cerrar sesión"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
