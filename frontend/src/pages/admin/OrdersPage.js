import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { toast } from 'sonner';
import { 
  ShoppingCart, 
  Eye, 
  Trash2,
  Clock,
  CheckCircle,
  Plus,
  Filter
} from 'lucide-react';
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
import { format } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const OrdersPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAdmin } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState(null);
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || 'all');

  useEffect(() => {
    fetchOrders();
    if (statusFilter && statusFilter !== 'all') {
      setSearchParams({ status: statusFilter });
    } else {
      setSearchParams({});
    }
  }, [statusFilter]);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter && statusFilter !== 'all') {
        params.append('status', statusFilter);
      }
      const response = await axios.get(`${API_URL}/api/orders?${params}`);
      setOrders(response.data);
    } catch (error) {
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    
    try {
      await axios.delete(`${API_URL}/api/orders/${deleteId}`);
      toast.success('Order deleted');
      fetchOrders();
    } catch (error) {
      toast.error('Failed to delete order');
    } finally {
      setDeleteId(null);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 text-xs font-bold rounded">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded">
            <CheckCircle className="w-3 h-3" />
            Completed
          </span>
        );
      default:
        return (
          <span className="px-2 py-1 bg-slate-100 text-slate-700 text-xs font-bold rounded">
            {status}
          </span>
        );
    }
  };

  const basePath = isAdmin() ? '/admin' : '/staff';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl font-bold text-slate-900">Orders</h1>
          <p className="text-slate-500 text-sm mt-1">{orders.length} orders found</p>
        </div>
        <div className="flex gap-3">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger data-testid="filter-order-status" className="w-40 h-10">
              <Filter className="w-4 h-4 mr-2" />
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>
          <Link to={`${basePath === '/admin' ? '/staff' : basePath}/orders/new`}>
            <Button data-testid="create-order-btn" className="btn-action">
              <Plus className="w-5 h-5 mr-2" />
              New Order
            </Button>
          </Link>
        </div>
      </div>

      {/* Orders List */}
      <div className="card-industrial overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
          </div>
        ) : orders.length === 0 ? (
          <div className="p-12 text-center">
            <ShoppingCart className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-heading text-xl font-bold text-slate-700">No Orders Found</h3>
            <p className="text-slate-500 mt-2 mb-6">
              {statusFilter !== 'all' ? 'Try changing the filter' : 'Create your first order'}
            </p>
            <Link to={`${basePath === '/admin' ? '/staff' : basePath}/orders/new`}>
              <Button className="btn-primary">
                <Plus className="w-4 h-4 mr-2" />
                Create Order
              </Button>
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="table-header text-left">Order #</th>
                  <th className="table-header text-left">Customer</th>
                  <th className="table-header text-center">Items</th>
                  <th className="table-header text-center">Status</th>
                  <th className="table-header text-left">Created By</th>
                  <th className="table-header text-left">Date</th>
                  <th className="table-header text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id} className="table-row" data-testid={`order-row-${order.order_number}`}>
                    <td className="table-cell-mono font-bold text-industrial-blue">
                      {order.order_number}
                    </td>
                    <td className="table-cell font-medium">{order.customer_name}</td>
                    <td className="table-cell text-center">
                      <span className="px-2 py-1 bg-slate-100 text-slate-700 text-sm font-bold rounded">
                        {order.items.length}
                      </span>
                    </td>
                    <td className="table-cell text-center">
                      {getStatusBadge(order.status)}
                    </td>
                    <td className="table-cell text-slate-600">{order.created_by_name}</td>
                    <td className="table-cell text-slate-500 text-sm">
                      {format(new Date(order.created_at), 'dd MMM yyyy, HH:mm')}
                    </td>
                    <td className="table-cell">
                      <div className="flex items-center justify-center gap-2">
                        <Link to={`${basePath}/orders/${order.id}`}>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            data-testid={`view-order-${order.order_number}`}
                            className="text-industrial-blue hover:text-industrial-blue-dark"
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                        </Link>
                        {isAdmin() && (
                          <Button
                            variant="ghost"
                            size="sm"
                            data-testid={`delete-order-${order.order_number}`}
                            onClick={() => setDeleteId(order.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Order?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the order.
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

export default OrdersPage;
