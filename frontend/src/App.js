import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Toaster } from "./components/ui/sonner";

// Public Pages
import HomePage from "./pages/public/HomePage";
import CataloguePage from "./pages/public/CataloguePage";
import ContactPage from "./pages/public/ContactPage";
import LoginPage from "./pages/LoginPage";

// Dashboard Layout
import DashboardLayout from "./components/layout/DashboardLayout";

// Admin Pages
import AdminDashboard from "./pages/admin/AdminDashboard";
import ProductsPage from "./pages/admin/ProductsPage";
import ProductFormPage from "./pages/admin/ProductFormPage";
import StaffPage from "./pages/admin/StaffPage";
import OrdersPage from "./pages/admin/OrdersPage";

// Staff Pages
import StaffDashboard from "./pages/staff/StaffDashboard";
import SearchProducts from "./pages/staff/SearchProducts";
import CreateOrder from "./pages/staff/CreateOrder";
import PicklistPage from "./pages/staff/PicklistPage";

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={user.role === 'admin' ? '/admin' : '/staff'} replace />;
  }
  
  return children;
};

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/catalogue" element={<CataloguePage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route 
        path="/login" 
        element={user ? <Navigate to={user.role === 'admin' ? '/admin' : '/staff'} replace /> : <LoginPage />} 
      />
      
      {/* Admin Routes */}
      <Route path="/admin" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <DashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<AdminDashboard />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="products/new" element={<ProductFormPage />} />
        <Route path="products/:id/edit" element={<ProductFormPage />} />
        <Route path="staff" element={<StaffPage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="orders/:id" element={<PicklistPage />} />
      </Route>
      
      {/* Staff Routes */}
      <Route path="/staff" element={
        <ProtectedRoute allowedRoles={['admin', 'staff']}>
          <DashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<StaffDashboard />} />
        <Route path="search" element={<SearchProducts />} />
        <Route path="orders/new" element={<CreateOrder />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="orders/:id" element={<PicklistPage />} />
      </Route>
      
      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <HelmetProvider>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
          <Toaster position="top-right" richColors />
        </BrowserRouter>
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
