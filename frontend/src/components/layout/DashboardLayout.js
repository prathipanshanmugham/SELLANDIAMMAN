import { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  LayoutDashboard, 
  Package, 
  Users, 
  ShoppingCart, 
  Search, 
  Plus, 
  LogOut,
  Menu,
  X,
  ChevronRight,
  Zap
} from 'lucide-react';
import { Button } from '../ui/button';

const DashboardLayout = () => {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const adminLinks = [
    { path: '/admin', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/admin/products', label: 'Products', icon: Package },
    { path: '/admin/staff', label: 'Staff', icon: Users },
    { path: '/admin/orders', label: 'Orders', icon: ShoppingCart },
  ];

  const staffLinks = [
    { path: '/staff', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/staff/search', label: 'Search Products', icon: Search },
    { path: '/staff/orders/new', label: 'Create Order', icon: Plus },
    { path: '/staff/orders', label: 'Orders', icon: ShoppingCart },
  ];

  const links = isAdmin() ? adminLinks : staffLinks;

  const isActive = (path) => {
    if (path === '/admin' || path === '/staff') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-slate-100 flex">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-64 bg-slate-900 text-white
        transform transition-transform duration-200 ease-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-4 border-b border-slate-800">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-industrial-orange rounded-sm flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="font-heading text-lg font-bold tracking-tight">SELLANDIAMMAN</h1>
                <p className="text-xs text-slate-400">Traders</p>
              </div>
            </Link>
          </div>

          {/* User info */}
          <div className="p-4 border-b border-slate-800">
            <p className="text-sm text-slate-400">Logged in as</p>
            <p className="font-medium truncate">{user?.name}</p>
            <span className={`
              inline-block mt-1 px-2 py-0.5 text-xs font-bold uppercase tracking-wider rounded
              ${user?.role === 'admin' ? 'bg-industrial-orange' : 'bg-industrial-blue'}
            `}>
              {user?.role}
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {links.map((link) => {
              const Icon = link.icon;
              const active = isActive(link.path);
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setSidebarOpen(false)}
                  data-testid={`nav-${link.label.toLowerCase().replace(' ', '-')}`}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-sm transition-all duration-150
                    ${active 
                      ? 'bg-industrial-orange text-white' 
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'}
                  `}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span className="font-medium">{link.label}</span>
                  {active && <ChevronRight className="w-4 h-4 ml-auto" />}
                </Link>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-slate-800">
            <Button
              onClick={handleLogout}
              variant="ghost"
              data-testid="logout-btn"
              className="w-full justify-start text-slate-300 hover:text-white hover:bg-slate-800"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center gap-4 sticky top-0 z-30">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 hover:bg-slate-100 rounded-sm"
            data-testid="mobile-menu-btn"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          <div className="flex-1">
            <h2 className="font-heading text-xl font-bold text-slate-900 tracking-tight">
              {links.find(l => isActive(l.path))?.label || 'Dashboard'}
            </h2>
          </div>

          <div className="text-right text-sm text-slate-500">
            <span className="hidden sm:inline">Welcome, </span>
            <span className="font-medium text-slate-700">{user?.name}</span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
