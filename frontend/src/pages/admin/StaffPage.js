import { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { toast } from 'sonner';
import { 
  Plus, 
  Users, 
  Trash2,
  UserCog,
  Shield,
  ToggleLeft,
  ToggleRight,
  Key,
  AlertTriangle
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../../components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../../components/ui/alert-dialog';
import { Checkbox } from '../../components/ui/checkbox';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const StaffPage = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [resetPasswordEmployee, setResetPasswordEmployee] = useState(null);
  const [resetPasswordForm, setResetPasswordForm] = useState({
    new_password: '',
    force_change_on_login: true
  });
  
  const [newEmployee, setNewEmployee] = useState({
    name: '',
    email: '',
    password: '',
    role: 'staff'
  });

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/employees`);
      setEmployees(response.data);
    } catch (error) {
      toast.error('Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`${API_URL}/api/employees`, newEmployee);
      toast.success('Employee added successfully');
      setShowAddDialog(false);
      setNewEmployee({ name: '', email: '', password: '', role: 'staff' });
      fetchEmployees();
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to add employee';
      toast.error(message);
    }
  };

  const handleToggleStatus = async (id) => {
    try {
      await axios.patch(`${API_URL}/api/employees/${id}/status`);
      toast.success('Status updated');
      fetchEmployees();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    
    try {
      await axios.delete(`${API_URL}/api/employees/${deleteId}`);
      toast.success('Employee deleted');
      fetchEmployees();
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to delete employee';
      toast.error(message);
    } finally {
      setDeleteId(null);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!resetPasswordEmployee) return;
    
    try {
      await axios.post(`${API_URL}/api/employees/${resetPasswordEmployee.id}/reset-password`, resetPasswordForm);
      toast.success(`Password reset for ${resetPasswordEmployee.name}`);
      setResetPasswordEmployee(null);
      setResetPasswordForm({ new_password: '', force_change_on_login: true });
      fetchEmployees();
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to reset password';
      toast.error(message);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl font-bold text-slate-900">Staff Management</h1>
          <p className="text-slate-500 text-sm mt-1">{employees.length} employees</p>
        </div>
        <Button 
          data-testid="add-staff-btn"
          onClick={() => setShowAddDialog(true)} 
          className="btn-action"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add Staff
        </Button>
      </div>

      {/* Staff List */}
      <div className="card-industrial overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
          </div>
        ) : employees.length === 0 ? (
          <div className="p-8 sm:p-12 text-center">
            <Users className="w-12 h-12 sm:w-16 sm:h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-heading text-lg sm:text-xl font-bold text-slate-700">No Employees</h3>
            <p className="text-slate-500 mt-2 mb-6 text-sm">Add staff members to manage your inventory</p>
            <Button onClick={() => setShowAddDialog(true)} className="btn-primary">
              <Plus className="w-4 h-4 mr-2" />
              Add Staff
            </Button>
          </div>
        ) : (
          <>
            {/* Desktop Table View */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="table-header text-left">Name</th>
                    <th className="table-header text-left">Email</th>
                    <th className="table-header text-center">Role</th>
                    <th className="table-header text-center">Status</th>
                    <th className="table-header text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.map((emp) => (
                    <tr key={emp.id} className="table-row" data-testid={`staff-row-${emp.email}`}>
                      <td className="table-cell">
                        <div className="flex items-center gap-3">
                          <div className={`
                            w-10 h-10 rounded-full flex items-center justify-center font-bold text-white
                            ${emp.role === 'admin' ? 'bg-industrial-orange' : 'bg-industrial-blue'}
                          `}>
                            {emp.name.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <span className="font-medium">{emp.name}</span>
                            {emp.force_password_change && (
                              <span className="ml-2 text-[10px] px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded font-medium">
                                Pwd Reset Required
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="table-cell text-slate-600">{emp.email}</td>
                      <td className="table-cell text-center">
                        <span className={`
                          inline-flex items-center gap-1 px-2 py-1 text-xs font-bold uppercase tracking-wider rounded
                          ${emp.role === 'admin' 
                            ? 'bg-industrial-orange/10 text-industrial-orange' 
                            : 'bg-industrial-blue/10 text-industrial-blue'}
                        `}>
                          {emp.role === 'admin' ? <Shield className="w-3 h-3" /> : <UserCog className="w-3 h-3" />}
                          {emp.role}
                        </span>
                      </td>
                      <td className="table-cell text-center">
                        <button
                          onClick={() => handleToggleStatus(emp.id)}
                          data-testid={`toggle-status-${emp.email}`}
                          className="inline-flex items-center gap-2"
                        >
                          {emp.status === 'active' ? (
                            <>
                              <ToggleRight className="w-6 h-6 text-green-600" />
                              <span className="text-sm text-green-600 font-medium">Active</span>
                            </>
                          ) : (
                            <>
                              <ToggleLeft className="w-6 h-6 text-slate-400" />
                              <span className="text-sm text-slate-400">Inactive</span>
                            </>
                          )}
                        </button>
                      </td>
                      <td className="table-cell text-center">
                        <div className="flex items-center justify-center gap-1">
                          {emp.role !== 'admin' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              data-testid={`reset-password-${emp.email}`}
                              onClick={() => setResetPasswordEmployee(emp)}
                              className="text-amber-600 hover:text-amber-700"
                              title="Reset Password"
                            >
                              <Key className="w-4 h-4" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            data-testid={`delete-staff-${emp.email}`}
                            onClick={() => setDeleteId(emp.id)}
                            className="text-red-600 hover:text-red-700"
                            disabled={emp.role === 'admin'}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Mobile Card View */}
            <div className="md:hidden divide-y divide-slate-100">
              {employees.map((emp) => (
                <div key={emp.id} data-testid={`staff-card-${emp.email}`} className="p-3">
                  <div className="flex items-start gap-3">
                    <div className={`
                      w-10 h-10 rounded-full flex items-center justify-center font-bold text-white flex-shrink-0
                      ${emp.role === 'admin' ? 'bg-industrial-orange' : 'bg-industrial-blue'}
                    `}>
                      {emp.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-sm">{emp.name}</span>
                        <span className={`
                          text-[10px] px-1.5 py-0.5 font-bold uppercase rounded
                          ${emp.role === 'admin' 
                            ? 'bg-industrial-orange/10 text-industrial-orange' 
                            : 'bg-industrial-blue/10 text-industrial-blue'}
                        `}>
                          {emp.role}
                        </span>
                        {emp.force_password_change && (
                          <span className="text-[10px] px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded font-medium">
                            Pwd Reset
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 truncate">{emp.email}</p>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <button
                        onClick={() => handleToggleStatus(emp.id)}
                        className="p-1"
                      >
                        {emp.status === 'active' ? (
                          <ToggleRight className="w-6 h-6 text-green-600" />
                        ) : (
                          <ToggleLeft className="w-6 h-6 text-slate-400" />
                        )}
                      </button>
                      {emp.role !== 'admin' && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setResetPasswordEmployee(emp)}
                            className="p-1 h-8 w-8"
                          >
                            <Key className="w-4 h-4 text-amber-600" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeleteId(emp.id)}
                            className="p-1 h-8 w-8"
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Add Employee Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="font-heading text-xl">Add New Staff</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddEmployee} className="space-y-4 mt-4">
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Name *
              </Label>
              <Input
                data-testid="new-staff-name"
                value={newEmployee.name}
                onChange={(e) => setNewEmployee({ ...newEmployee, name: e.target.value })}
                placeholder="John Doe"
                className="mt-2 input-industrial"
                required
              />
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Email *
              </Label>
              <Input
                data-testid="new-staff-email"
                type="email"
                value={newEmployee.email}
                onChange={(e) => setNewEmployee({ ...newEmployee, email: e.target.value })}
                placeholder="john@example.com"
                className="mt-2 input-industrial"
                required
              />
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Password *
              </Label>
              <Input
                data-testid="new-staff-password"
                type="password"
                value={newEmployee.password}
                onChange={(e) => setNewEmployee({ ...newEmployee, password: e.target.value })}
                placeholder="Min 6 characters"
                className="mt-2 input-industrial"
                required
                minLength={6}
              />
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Role *
              </Label>
              <Select
                value={newEmployee.role}
                onValueChange={(v) => setNewEmployee({ ...newEmployee, role: v })}
              >
                <SelectTrigger data-testid="new-staff-role" className="mt-2 h-12">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="staff">Staff</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowAddDialog(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                data-testid="submit-new-staff"
                className="flex-1 btn-action"
              >
                Add Staff
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Employee?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will remove the employee from the system.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default StaffPage;
