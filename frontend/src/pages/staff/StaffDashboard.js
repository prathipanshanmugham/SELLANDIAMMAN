import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/button';
import { 
  Package, 
  ShoppingCart, 
  Search,
  Plus,
  Clock,
  CheckCircle,
  ArrowRight
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const StaffDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentOrders, setRecentOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, ordersRes] = await Promise.all([
        axios.get(`${API_URL}/api/dashboard/stats`),
        axios.get(`${API_URL}/api/orders?status=pending`)
      ]);
      setStats(statsRes.data);
      setRecentOrders(ordersRes.data.slice(0, 5));
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome */}
      <div className="card-industrial p-6 bg-gradient-to-r from-industrial-blue to-industrial-blue-dark text-white">
        <h1 className="font-heading text-2xl font-bold mb-2">
          Welcome back, {user?.name}!
        </h1>
        <p className="text-slate-300">
          Ready to pick some orders? Here's your quick action panel.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid sm:grid-cols-3 gap-4">
        <Link to="/staff/orders/new" className="block">
          <div className="card-industrial p-6 hover:shadow-md transition-shadow cursor-pointer group h-full">
            <div className="w-12 h-12 bg-industrial-orange/10 rounded-sm flex items-center justify-center mb-4 group-hover:bg-industrial-orange/20 transition-colors">
              <Plus className="w-6 h-6 text-industrial-orange" />
            </div>
            <h3 className="font-heading text-lg font-bold text-slate-900 mb-1">Create Order</h3>
            <p className="text-sm text-slate-500">Start a new sales order</p>
          </div>
        </Link>

        <Link to="/staff/search" className="block">
          <div className="card-industrial p-6 hover:shadow-md transition-shadow cursor-pointer group h-full">
            <div className="w-12 h-12 bg-industrial-blue/10 rounded-sm flex items-center justify-center mb-4 group-hover:bg-industrial-blue/20 transition-colors">
              <Search className="w-6 h-6 text-industrial-blue" />
            </div>
            <h3 className="font-heading text-lg font-bold text-slate-900 mb-1">Search Products</h3>
            <p className="text-sm text-slate-500">Find product locations</p>
          </div>
        </Link>

        <Link to="/staff/orders" className="block">
          <div className="card-industrial p-6 hover:shadow-md transition-shadow cursor-pointer group h-full">
            <div className="w-12 h-12 bg-green-100 rounded-sm flex items-center justify-center mb-4 group-hover:bg-green-200 transition-colors">
              <ShoppingCart className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-heading text-lg font-bold text-slate-900 mb-1">View Orders</h3>
            <p className="text-sm text-slate-500">
              {stats?.orders_pending || 0} pending orders
            </p>
          </div>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card-industrial p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Products</p>
              <p className="font-heading text-2xl font-bold text-slate-900 mt-1">
                {stats?.total_products?.toLocaleString() || 0}
              </p>
            </div>
            <Package className="w-8 h-8 text-industrial-blue opacity-50" />
          </div>
        </div>

        <div className="card-industrial p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Stock Units</p>
              <p className="font-heading text-2xl font-bold text-slate-900 mt-1">
                {stats?.total_stock_units?.toLocaleString() || 0}
              </p>
            </div>
            <Package className="w-8 h-8 text-green-600 opacity-50" />
          </div>
        </div>

        <div className="card-industrial p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Pending</p>
              <p className="font-heading text-2xl font-bold text-amber-600 mt-1">
                {stats?.orders_pending || 0}
              </p>
            </div>
            <Clock className="w-8 h-8 text-amber-600 opacity-50" />
          </div>
        </div>

        <div className="card-industrial p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Completed</p>
              <p className="font-heading text-2xl font-bold text-green-600 mt-1">
                {stats?.orders_completed || 0}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600 opacity-50" />
          </div>
        </div>
      </div>

      {/* Pending Orders */}
      <div className="card-industrial">
        <div className="border-b border-slate-100 p-4 bg-slate-50/50 flex items-center justify-between">
          <h3 className="font-heading text-lg font-bold text-slate-900">
            Pending Orders
            {recentOrders.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-bold rounded">
                {recentOrders.length}
              </span>
            )}
          </h3>
          <Link to="/staff/orders">
            <Button variant="ghost" size="sm" className="text-industrial-blue">
              View All <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
        
        {recentOrders.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {recentOrders.map((order) => (
              <Link 
                key={order.id}
                to={`/staff/orders/${order.id}`}
                className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
              >
                <div>
                  <p className="font-mono font-bold text-industrial-blue">{order.order_number}</p>
                  <p className="text-sm text-slate-500">{order.customer_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">{order.items.length} items</p>
                  <p className="text-xs text-slate-400">
                    {order.items.filter(i => i.picking_status === 'picked').length} picked
                  </p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400">
            <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500" />
            <p className="font-medium text-slate-600">No pending orders!</p>
            <p className="text-sm">All orders have been picked.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StaffDashboard;
