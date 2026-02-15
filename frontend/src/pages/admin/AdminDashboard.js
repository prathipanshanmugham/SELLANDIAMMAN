import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { 
  Package, 
  ShoppingCart, 
  AlertTriangle, 
  TrendingUp,
  ArrowRight,
  Plus,
  Clock
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [zoneData, setZoneData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [lowStockItems, setLowStockItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, zoneRes, categoryRes, lowStockRes] = await Promise.all([
        axios.get(`${API_URL}/api/dashboard/stats`),
        axios.get(`${API_URL}/api/dashboard/zone-distribution`),
        axios.get(`${API_URL}/api/dashboard/category-distribution`),
        axios.get(`${API_URL}/api/dashboard/low-stock-items`)
      ]);
      
      setStats(statsRes.data);
      setZoneData(zoneRes.data);
      setCategoryData(categoryRes.data);
      setLowStockItems(lowStockRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#002D62', '#F97316', '#16A34A', '#EAB308', '#0284C7', '#DC2626'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card-industrial p-4" data-testid="stat-total-products">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Total Products</p>
              <p className="font-heading text-3xl font-bold text-slate-900 mt-1">
                {stats?.total_products?.toLocaleString() || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-industrial-blue/10 rounded-sm flex items-center justify-center">
              <Package className="w-6 h-6 text-industrial-blue" />
            </div>
          </div>
        </div>

        <div className="card-industrial p-4" data-testid="stat-total-stock">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Stock Units</p>
              <p className="font-heading text-3xl font-bold text-slate-900 mt-1">
                {stats?.total_stock_units?.toLocaleString() || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-sm flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card-industrial p-4" data-testid="stat-low-stock">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Low Stock</p>
              <p className="font-heading text-3xl font-bold text-red-600 mt-1">
                {stats?.low_stock_items || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-sm flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="card-industrial p-4" data-testid="stat-orders-today">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Orders Today</p>
              <p className="font-heading text-3xl font-bold text-slate-900 mt-1">
                {stats?.sales_today || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-industrial-orange/10 rounded-sm flex items-center justify-center">
              <ShoppingCart className="w-6 h-6 text-industrial-orange" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/admin/products/new">
          <Button data-testid="quick-add-product" className="w-full btn-primary h-12 justify-start">
            <Plus className="w-5 h-5 mr-2" />
            Add Product
          </Button>
        </Link>
        <Link to="/staff/orders/new">
          <Button data-testid="quick-create-order" className="w-full btn-action h-12 justify-start">
            <ShoppingCart className="w-5 h-5 mr-2" />
            Create Order
          </Button>
        </Link>
        <Link to="/admin/products?low_stock=true">
          <Button data-testid="quick-view-low-stock" className="w-full btn-secondary h-12 justify-start">
            <AlertTriangle className="w-5 h-5 mr-2" />
            View Low Stock
          </Button>
        </Link>
        <Link to="/admin/orders?status=pending">
          <Button data-testid="quick-pending-orders" className="w-full btn-secondary h-12 justify-start">
            <Clock className="w-5 h-5 mr-2" />
            Pending: {stats?.orders_pending || 0}
          </Button>
        </Link>
      </div>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Zone Distribution */}
        <div className="card-industrial">
          <div className="border-b border-slate-100 p-4 bg-slate-50/50">
            <h3 className="font-heading text-lg font-bold text-slate-900">Zone Distribution</h3>
          </div>
          <div className="p-4">
            {zoneData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={zoneData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="zone" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#fff', 
                      border: '1px solid #E2E8F0',
                      borderRadius: '4px'
                    }} 
                  />
                  <Bar dataKey="count" fill="#002D62" name="Products" />
                  <Bar dataKey="stock" fill="#F97316" name="Stock" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-400">
                No zone data available
              </div>
            )}
          </div>
        </div>

        {/* Category Distribution */}
        <div className="card-industrial">
          <div className="border-b border-slate-100 p-4 bg-slate-50/50">
            <h3 className="font-heading text-lg font-bold text-slate-900">Top Categories</h3>
          </div>
          <div className="p-4">
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    dataKey="count"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ category, count }) => `${category}: ${count}`}
                    labelLine={false}
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-400">
                No category data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Low Stock Items */}
      <div className="card-industrial">
        <div className="border-b border-slate-100 p-4 bg-slate-50/50 flex items-center justify-between">
          <h3 className="font-heading text-lg font-bold text-slate-900">
            Low Stock Alerts
            {lowStockItems.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-red-100 text-red-700 text-xs font-bold rounded">
                {lowStockItems.length}
              </span>
            )}
          </h3>
          <Link to="/admin/products?low_stock=true">
            <Button variant="ghost" size="sm" className="text-industrial-blue">
              View All <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
        <div className="overflow-x-auto">
          {lowStockItems.length > 0 ? (
            <table className="w-full">
              <thead>
                <tr>
                  <th className="table-header text-left">SKU</th>
                  <th className="table-header text-left">Product</th>
                  <th className="table-header text-left">Location</th>
                  <th className="table-header text-right">Available</th>
                  <th className="table-header text-right">Reorder Level</th>
                </tr>
              </thead>
              <tbody>
                {lowStockItems.map((item) => (
                  <tr key={item.sku} className="table-row">
                    <td className="table-cell-mono">{item.sku}</td>
                    <td className="table-cell font-medium">{item.product_name}</td>
                    <td className="table-cell-mono text-slate-500">{item.full_location_code}</td>
                    <td className="table-cell text-right">
                      <span className={`font-bold ${item.quantity_available <= 0 ? 'text-red-600' : 'text-amber-600'}`}>
                        {item.quantity_available}
                      </span>
                    </td>
                    <td className="table-cell text-right text-slate-500">{item.reorder_level}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-slate-400">
              <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-green-500" />
              <p className="font-medium text-slate-600">All items are well stocked!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
