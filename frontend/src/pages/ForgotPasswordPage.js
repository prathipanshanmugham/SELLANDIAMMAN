import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Zap, Shield, ArrowLeft, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1); // 1: email, 2: security question, 3: success
  const [email, setEmail] = useState('');
  const [securityQuestion, setSecurityQuestion] = useState('');
  const [securityAnswer, setSecurityAnswer] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGetSecurityQuestion = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const response = await axios.get(`${API_URL}/api/auth/security-question/${encodeURIComponent(email)}`);
      setSecurityQuestion(response.data.security_question);
      setStep(2);
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to retrieve security question';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');
    
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    setLoading(true);
    
    try {
      await axios.post(`${API_URL}/api/auth/reset-password-with-security`, {
        email: email,
        security_answer: securityAnswer,
        new_password: newPassword
      });
      
      setStep(3);
      toast.success('Password reset successfully!');
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to reset password';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
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
          {step === 1 && (
            <>
              <div className="flex items-center justify-center mb-6">
                <div className="p-3 bg-industrial-blue/10 rounded-full">
                  <Shield className="w-8 h-8 text-industrial-blue" />
                </div>
              </div>
              
              <div className="text-center mb-6">
                <h2 className="font-heading text-xl font-bold text-slate-900">Admin Password Reset</h2>
                <p className="text-slate-500 mt-1 text-sm">
                  Enter your admin email to reset your password
                </p>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-sm flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}

              <form onSubmit={handleGetSecurityQuestion} className="space-y-5">
                <div>
                  <Label htmlFor="email" className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                    Admin Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    data-testid="forgot-email-input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="admin@sellandiamman.com"
                    className="mt-2 input-industrial"
                    required
                    autoFocus
                  />
                </div>

                <Button
                  type="submit"
                  data-testid="continue-btn"
                  disabled={loading}
                  className="w-full btn-primary h-12 text-base"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                  ) : (
                    'Continue'
                  )}
                </Button>
              </form>

              <p className="text-center mt-6 text-sm text-slate-500">
                <Link to="/login" className="text-industrial-blue hover:underline flex items-center justify-center gap-1">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Login
                </Link>
              </p>
            </>
          )}

          {step === 2 && (
            <>
              <div className="flex items-center justify-center mb-6">
                <div className="p-3 bg-industrial-blue/10 rounded-full">
                  <Shield className="w-8 h-8 text-industrial-blue" />
                </div>
              </div>
              
              <div className="text-center mb-6">
                <h2 className="font-heading text-xl font-bold text-slate-900">Security Question</h2>
                <p className="text-slate-500 mt-1 text-sm">
                  Answer your security question to reset password
                </p>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-sm flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}

              <form onSubmit={handleResetPassword} className="space-y-5">
                <div className="p-3 bg-slate-50 rounded-sm border border-slate-200">
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Security Question</p>
                  <p className="font-medium text-slate-800">{securityQuestion}</p>
                </div>

                <div>
                  <Label htmlFor="answer" className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                    Your Answer
                  </Label>
                  <Input
                    id="answer"
                    type="text"
                    data-testid="security-answer-input"
                    value={securityAnswer}
                    onChange={(e) => setSecurityAnswer(e.target.value)}
                    placeholder="Enter your answer"
                    className="mt-2 input-industrial"
                    required
                    autoFocus
                  />
                </div>

                <div>
                  <Label htmlFor="newPassword" className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                    New Password
                  </Label>
                  <div className="relative mt-2">
                    <Input
                      id="newPassword"
                      type={showPassword ? 'text' : 'password'}
                      data-testid="new-password-input"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Min 6 characters"
                      className="input-industrial pr-12"
                      required
                      minLength={6}
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

                <div>
                  <Label htmlFor="confirmPassword" className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                    Confirm Password
                  </Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    data-testid="confirm-password-input"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter new password"
                    className="mt-2 input-industrial"
                    required
                  />
                </div>

                <Button
                  type="submit"
                  data-testid="reset-password-btn"
                  disabled={loading}
                  className="w-full btn-primary h-12 text-base"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                  ) : (
                    'Reset Password'
                  )}
                </Button>
              </form>

              <p className="text-center mt-6 text-sm text-slate-500">
                <button 
                  onClick={() => { setStep(1); setError(''); }}
                  className="text-industrial-blue hover:underline flex items-center justify-center gap-1 mx-auto"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Use different email
                </button>
              </p>
            </>
          )}

          {step === 3 && (
            <div className="text-center py-8">
              <div className="flex items-center justify-center mb-6">
                <div className="p-4 bg-green-100 rounded-full">
                  <CheckCircle className="w-12 h-12 text-green-600" />
                </div>
              </div>
              
              <h2 className="font-heading text-xl font-bold text-slate-900 mb-2">Password Reset!</h2>
              <p className="text-slate-500 mb-6">
                Your password has been reset successfully. You can now login with your new password.
              </p>
              
              <Button
                onClick={() => navigate('/login')}
                data-testid="go-to-login-btn"
                className="btn-primary"
              >
                Go to Login
              </Button>
            </div>
          )}
        </div>

        <p className="text-center mt-6 text-xs text-slate-400">
          This password reset is only available for admin accounts with security questions set up.
        </p>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
