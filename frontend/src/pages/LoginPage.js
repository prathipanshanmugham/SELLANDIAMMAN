import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Zap, LogIn, Eye, EyeOff, AlertCircle } from 'lucide-react';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.name}!`);
      navigate(user.role === 'admin' ? '/admin' : '/staff');
    } catch (err) {
      const message = err.response?.data?.detail || 'Invalid credentials';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-industrial-blue text-white p-12 flex-col justify-between relative overflow-hidden">
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: 'url(https://images.unsplash.com/photo-1584175053565-c757cdff0e9a?w=1920)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-12 h-12 bg-industrial-orange rounded-sm flex items-center justify-center">
              <Zap className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="font-heading text-2xl font-bold tracking-tight">SELLANDIAMMAN</h1>
              <p className="text-slate-300">Traders</p>
            </div>
          </Link>
        </div>
        
        <div className="relative z-10">
          <h2 className="font-heading text-4xl font-bold tracking-tight mb-4">
            Inventory Management System
          </h2>
          <p className="text-xl text-slate-300 mb-8">
            Streamline your warehouse operations with our powerful inventory and sales management system.
          </p>
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-sm p-4">
              <p className="font-heading text-3xl font-bold text-industrial-orange">10,000+</p>
              <p className="text-slate-300">Products</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-sm p-4">
              <p className="font-heading text-3xl font-bold text-industrial-orange">Fast</p>
              <p className="text-slate-300">Billing</p>
            </div>
          </div>
        </div>
        
        <div className="relative z-10 text-sm text-slate-400">
          © {new Date().getFullYear()} Sellandiamman Traders
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <Link to="/" className="inline-flex items-center gap-2">
              <div className="w-10 h-10 bg-industrial-orange rounded-sm flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <h1 className="font-heading text-lg font-bold text-slate-900">SELLANDIAMMAN</h1>
                <p className="text-xs text-slate-500">Traders</p>
              </div>
            </Link>
          </div>

          <div className="card-industrial p-8">
            <div className="text-center mb-8">
              <h2 className="font-heading text-2xl font-bold text-slate-900">Staff Login</h2>
              <p className="text-slate-500 mt-1">Sign in to access the dashboard</p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-sm flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="email" className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                  Email Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  data-testid="login-email-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@sellandiamman.com"
                  className="mt-2 input-industrial"
                  required
                  autoFocus
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                  Password
                </Label>
                <div className="relative mt-2">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    data-testid="login-password-input"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="input-industrial pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                data-testid="login-submit-btn"
                disabled={loading}
                className="w-full btn-primary h-12 text-base"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                ) : (
                  <>
                    <LogIn className="w-5 h-5 mr-2" />
                    Sign In
                  </>
                )}
              </Button>
            </form>

            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-center text-sm text-slate-500">
                Default Admin: <span className="font-mono text-xs">admin@sellandiamman.com / admin123</span>
              </p>
            </div>
          </div>

          <p className="text-center mt-6 text-sm text-slate-500">
            <Link to="/" className="text-industrial-blue hover:underline">
              ← Back to Website
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
