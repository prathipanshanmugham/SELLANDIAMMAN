import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { toast } from 'sonner';
import { Settings, Shield, Lock, CheckCircle, Eye, EyeOff } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SECURITY_QUESTIONS = [
  "What was the name of your first pet?",
  "What city were you born in?",
  "What is your mother's maiden name?",
  "What was the name of your first school?",
  "What is your favorite movie?",
  "What is the name of your childhood best friend?",
  "What was the make of your first car?",
  "What is your favorite food?"
];

const SettingsPage = () => {
  const { user } = useAuth();
  const [hasSecurityQuestion, setHasSecurityQuestion] = useState(false);
  const [showPasswordSection, setShowPasswordSection] = useState(false);
  
  // Security question form
  const [securityQuestion, setSecurityQuestion] = useState('');
  const [securityAnswer, setSecurityAnswer] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUserInfo();
  }, []);

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/me`);
      setHasSecurityQuestion(response.data.has_security_question);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  };

  const handleSetSecurityQuestion = async (e) => {
    e.preventDefault();
    
    if (!securityQuestion || !securityAnswer || !currentPassword) {
      toast.error('Please fill in all fields');
      return;
    }
    
    setLoading(true);
    
    try {
      await axios.post(`${API_URL}/api/auth/set-security-question`, {
        security_question: securityQuestion,
        security_answer: securityAnswer,
        current_password: currentPassword
      });
      
      toast.success('Security question set successfully!');
      setHasSecurityQuestion(true);
      setSecurityQuestion('');
      setSecurityAnswer('');
      setCurrentPassword('');
      setShowPasswordSection(false);
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to set security question';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="font-heading text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Settings className="w-6 h-6" />
          Account Settings
        </h1>
        <p className="text-slate-500 text-sm mt-1">Manage your account security settings</p>
      </div>

      {/* Security Question Section */}
      <div className="card-industrial p-6">
        <div className="flex items-start gap-4 mb-6">
          <div className="p-3 bg-industrial-blue/10 rounded-full">
            <Shield className="w-6 h-6 text-industrial-blue" />
          </div>
          <div className="flex-1">
            <h2 className="font-heading text-lg font-bold text-slate-900">Security Question</h2>
            <p className="text-sm text-slate-500 mt-1">
              Set up a security question to recover your admin password if you forget it.
            </p>
          </div>
          {hasSecurityQuestion && (
            <div className="flex items-center gap-1 text-green-600 text-sm">
              <CheckCircle className="w-4 h-4" />
              <span>Configured</span>
            </div>
          )}
        </div>

        {hasSecurityQuestion ? (
          <div className="bg-green-50 border border-green-200 rounded-sm p-4">
            <p className="text-sm text-green-700">
              You have already set up a security question. You can use it to reset your password if you forget it.
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-3"
              onClick={() => setShowPasswordSection(!showPasswordSection)}
            >
              {showPasswordSection ? 'Cancel' : 'Change Security Question'}
            </Button>
          </div>
        ) : (
          <div className="bg-amber-50 border border-amber-200 rounded-sm p-4 mb-4">
            <p className="text-sm text-amber-700">
              You haven't set up a security question yet. It's recommended to set one up for password recovery.
            </p>
          </div>
        )}

        {(!hasSecurityQuestion || showPasswordSection) && (
          <form onSubmit={handleSetSecurityQuestion} className="space-y-4 mt-4">
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Security Question *
              </Label>
              <Select
                value={securityQuestion}
                onValueChange={setSecurityQuestion}
              >
                <SelectTrigger data-testid="security-question-select" className="mt-2 h-12">
                  <SelectValue placeholder="Select a question" />
                </SelectTrigger>
                <SelectContent>
                  {SECURITY_QUESTIONS.map((q, i) => (
                    <SelectItem key={i} value={q}>{q}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Your Answer *
              </Label>
              <Input
                data-testid="security-answer-input"
                type="text"
                value={securityAnswer}
                onChange={(e) => setSecurityAnswer(e.target.value)}
                placeholder="Enter your answer"
                className="mt-2 input-industrial"
                required
              />
              <p className="text-xs text-slate-400 mt-1">This answer is case-insensitive</p>
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Current Password *
              </Label>
              <div className="relative mt-2">
                <Input
                  data-testid="current-password-input"
                  type={showCurrentPassword ? 'text' : 'password'}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Verify your password"
                  className="input-industrial pr-12"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showCurrentPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            
            <div className="flex gap-3 pt-2">
              {hasSecurityQuestion && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowPasswordSection(false);
                    setSecurityQuestion('');
                    setSecurityAnswer('');
                    setCurrentPassword('');
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
              )}
              <Button
                type="submit"
                data-testid="save-security-question-btn"
                disabled={loading}
                className={`btn-primary ${hasSecurityQuestion ? 'flex-1' : 'w-full'}`}
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                ) : (
                  <>
                    <Lock className="w-4 h-4 mr-2" />
                    {hasSecurityQuestion ? 'Update Security Question' : 'Set Security Question'}
                  </>
                )}
              </Button>
            </div>
          </form>
        )}
      </div>

      {/* Account Info */}
      <div className="card-industrial p-6">
        <h2 className="font-heading text-lg font-bold text-slate-900 mb-4">Account Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Name</p>
            <p className="font-medium text-slate-900">{user?.name}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Email</p>
            <p className="font-medium text-slate-900">{user?.email}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Role</p>
            <p className="font-medium text-slate-900 capitalize">{user?.role}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
