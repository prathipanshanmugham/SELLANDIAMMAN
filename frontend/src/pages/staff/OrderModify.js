import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';
import { 
  ArrowLeft, 
  Edit3, 
  Plus,
  Trash2,
  Save,
  History,
  AlertTriangle,
  Package,
  User,
  RefreshCw,
  Clock,
  CheckCircle
} from 'lucide-react';
import { format } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const OrderModify = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  
  const [order, setOrder] = useState(null);
  const [modificationHistory, setModificationHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('modify'); // modify | history
  
  // Edit states
  const [editingCustomer, setEditingCustomer] = useState(false);
  const [customerName, setCustomerName] = useState('');
  const [editingQty, setEditingQty] = useState(null);
  const [newQty, setNewQty] = useState(1);
  const [reason, setReason] = useState('');
  
  // Add item states
  const [showAddItem, setShowAddItem] = useState(false);
  const [skuSearch, setSkuSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [addQty, setAddQty] = useState(1);
  const [searching, setSearching] = useState(false);
  
  const [saving, setSaving] = useState(false);

  const basePath = isAdmin() ? '/admin' : '/staff';

  useEffect(() => {
    fetchOrder();
    fetchHistory();
  }, [id]);

  const fetchOrder = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/orders/${id}`);
      setOrder(response.data);
      setCustomerName(response.data.customer_name);
    } catch (error) {
      toast.error('Failed to fetch order');
      navigate(`${basePath}/orders`);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/orders/${id}/modification-history`);
      setModificationHistory(response.data);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const canEdit = () => {
    if (!order) return false;
    if (isAdmin()) return true;
    return order.status === 'pending';
  };

  // Update customer name
  const handleUpdateCustomer = async () => {
    if (!customerName.trim()) {
      toast.error('Customer name cannot be empty');
      return;
    }
    setSaving(true);
    try {
      await axios.patch(`${API_URL}/api/orders/${id}/customer`, {
        customer_name: customerName,
        reason: reason || null
      });
      toast.success('Customer name updated');
      setEditingCustomer(false);
      setReason('');
      fetchOrder();
      fetchHistory();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  // Update item quantity
  const handleUpdateQty = async (itemId) => {
    if (newQty < 1) {
      toast.error('Quantity must be at least 1');
      return;
    }
    setSaving(true);
    try {
      await axios.patch(`${API_URL}/api/orders/${id}/items/${itemId}/quantity`, {
        quantity_required: newQty,
        reason: reason || null
      });
      toast.success('Quantity updated');
      setEditingQty(null);
      setReason('');
      fetchOrder();
      fetchHistory();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  // Remove item
  const handleRemoveItem = async (itemId, sku) => {
    if (!confirm(`Remove ${sku} from order?`)) return;
    
    const removeReason = prompt('Enter reason for removal (optional):');
    
    setSaving(true);
    try {
      await axios.delete(`${API_URL}/api/orders/${id}/items/${itemId}?reason=${encodeURIComponent(removeReason || '')}`);
      toast.success('Item removed');
      fetchOrder();
      fetchHistory();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to remove item');
    } finally {
      setSaving(false);
    }
  };

  // Search products
  const handleSearch = async (query) => {
    setSkuSearch(query);
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    try {
      const response = await axios.get(`${API_URL}/api/products?search=${query}&limit=5`);
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  // Add item
  const handleAddItem = async (sku) => {
    const addReason = prompt('Enter reason for adding item (optional):');
    
    setSaving(true);
    try {
      await axios.post(`${API_URL}/api/orders/${id}/items`, {
        sku: sku,
        quantity_required: addQty,
        reason: addReason || null
      });
      toast.success(`${sku} added to order`);
      setShowAddItem(false);
      setSkuSearch('');
      setSearchResults([]);
      setAddQty(1);
      fetchOrder();
      fetchHistory();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add item');
    } finally {
      setSaving(false);
    }
  };

  // Update status (admin only)
  const handleToggleStatus = async () => {
    const newStatus = order.status === 'pending' ? 'completed' : 'pending';
    const statusReason = prompt(`Reason for changing status to ${newStatus}:`);
    
    setSaving(true);
    try {
      await axios.patch(`${API_URL}/api/orders/${id}/status`, {
        status: newStatus,
        reason: statusReason || null
      });
      toast.success(`Order status changed to ${newStatus}`);
      fetchOrder();
      fetchHistory();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update status');
    } finally {
      setSaving(false);
    }
  };

  const getModTypeIcon = (type) => {
    switch (type) {
      case 'add_item': return <Plus className="w-4 h-4 text-green-600" />;
      case 'remove_item': return <Trash2 className="w-4 h-4 text-red-600" />;
      case 'qty_change': return <Edit3 className="w-4 h-4 text-blue-600" />;
      case 'status_change': return <RefreshCw className="w-4 h-4 text-purple-600" />;
      case 'customer_change': return <User className="w-4 h-4 text-orange-600" />;
      case 'delete_order': return <Trash2 className="w-4 h-4 text-red-600" />;
      default: return <Edit3 className="w-4 h-4 text-slate-600" />;
    }
  };

  const getModTypeLabel = (type) => {
    switch (type) {
      case 'add_item': return 'Added Item';
      case 'remove_item': return 'Removed Item';
      case 'qty_change': return 'Qty Changed';
      case 'status_change': return 'Status Changed';
      case 'customer_change': return 'Customer Changed';
      case 'delete_order': return 'Order Deleted';
      default: return type;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
      </div>
    );
  }

  if (!order) return null;

  return (
    <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={() => navigate(`${basePath}/orders/${id}`)}
            className="p-2"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="font-heading text-xl sm:text-2xl font-bold text-slate-900">
              Modify Order
            </h1>
            <p className="text-slate-500 text-sm font-mono">{order.order_number}</p>
          </div>
        </div>
        {!canEdit() && (
          <div className="flex items-center gap-2 text-amber-600 bg-amber-50 px-3 py-2 rounded-sm">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm font-medium">Read Only</span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <Button
          variant={activeTab === 'modify' ? 'default' : 'outline'}
          onClick={() => setActiveTab('modify')}
          className={activeTab === 'modify' ? 'bg-industrial-blue' : ''}
        >
          <Edit3 className="w-4 h-4 mr-2" />
          Modify
        </Button>
        <Button
          variant={activeTab === 'history' ? 'default' : 'outline'}
          onClick={() => setActiveTab('history')}
          className={activeTab === 'history' ? 'bg-industrial-blue' : ''}
        >
          <History className="w-4 h-4 mr-2" />
          History ({modificationHistory.length})
        </Button>
      </div>

      {activeTab === 'modify' ? (
        <>
          {/* Order Info Section */}
          <div className="card-industrial p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-heading font-bold text-slate-900">Order Details</h2>
              {isAdmin() && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleToggleStatus}
                  disabled={saving}
                  className={order.status === 'pending' ? 'text-green-600' : 'text-amber-600'}
                >
                  {order.status === 'pending' ? (
                    <><CheckCircle className="w-4 h-4 mr-1" /> Mark Complete</>
                  ) : (
                    <><Clock className="w-4 h-4 mr-1" /> Reopen Order</>
                  )}
                </Button>
              )}
            </div>
            
            {/* Customer Name */}
            <div className="mb-4">
              <Label className="text-xs font-semibold text-slate-500 uppercase">Customer Name</Label>
              {editingCustomer ? (
                <div className="flex gap-2 mt-2">
                  <Input
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="flex-1"
                    placeholder="Customer name"
                  />
                  <Input
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    className="w-40"
                    placeholder="Reason (optional)"
                  />
                  <Button onClick={handleUpdateCustomer} disabled={saving} className="btn-primary">
                    <Save className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" onClick={() => { setEditingCustomer(false); setCustomerName(order.customer_name); }}>
                    Cancel
                  </Button>
                </div>
              ) : (
                <div className="flex items-center gap-2 mt-1">
                  <span className="font-medium">{order.customer_name}</span>
                  {canEdit() && (
                    <Button variant="ghost" size="sm" onClick={() => setEditingCustomer(true)}>
                      <Edit3 className="w-4 h-4 text-industrial-blue" />
                    </Button>
                  )}
                </div>
              )}
            </div>

            {/* Status Badge */}
            <div className="flex items-center gap-4 text-sm">
              <div>
                <span className="text-slate-500">Status: </span>
                <span className={`font-bold ${order.status === 'completed' ? 'text-green-600' : 'text-amber-600'}`}>
                  {order.status.toUpperCase()}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Created by: </span>
                <span className="font-medium text-industrial-orange">{order.created_by_name}</span>
              </div>
            </div>
          </div>

          {/* Items Section */}
          <div className="card-industrial">
            <div className="border-b border-slate-100 p-4 bg-slate-50/50 flex items-center justify-between">
              <h2 className="font-heading font-bold text-slate-900">
                Order Items ({order.items.length})
              </h2>
              {canEdit() && (
                <Button
                  onClick={() => setShowAddItem(!showAddItem)}
                  className="btn-action text-sm"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Item
                </Button>
              )}
            </div>

            {/* Add Item Panel */}
            {showAddItem && canEdit() && (
              <div className="p-4 bg-blue-50 border-b border-blue-100">
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="flex-1 relative">
                    <Input
                      value={skuSearch}
                      onChange={(e) => handleSearch(e.target.value)}
                      placeholder="Search SKU or product name..."
                      className="w-full"
                    />
                    {searchResults.length > 0 && (
                      <div className="absolute top-full left-0 right-0 bg-white border border-slate-200 rounded-sm shadow-lg z-10 max-h-48 overflow-y-auto">
                        {searchResults.map((product) => (
                          <button
                            key={product.id}
                            onClick={() => handleAddItem(product.sku)}
                            className="w-full px-3 py-2 text-left hover:bg-slate-50 border-b border-slate-100 last:border-0"
                          >
                            <span className="font-mono text-sm text-industrial-blue">{product.sku}</span>
                            <span className="text-sm text-slate-600 ml-2">{product.product_name}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="w-24">
                    <Input
                      type="number"
                      min={1}
                      value={addQty}
                      onChange={(e) => setAddQty(parseInt(e.target.value) || 1)}
                      placeholder="Qty"
                    />
                  </div>
                  <Button variant="ghost" onClick={() => setShowAddItem(false)}>Cancel</Button>
                </div>
              </div>
            )}

            {/* Items List */}
            <div className="divide-y divide-slate-100">
              {order.items.map((item) => (
                <div key={item.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-sm px-2 py-0.5 bg-industrial-blue text-white rounded">
                          {item.sku}
                        </span>
                        {item.picking_status === 'picked' && (
                          <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded">PICKED</span>
                        )}
                      </div>
                      <p className="font-medium text-slate-900">{item.product_name}</p>
                      <p className="text-xs text-slate-500 font-mono">{item.full_location_code}</p>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {/* Quantity Edit */}
                      {editingQty === item.id ? (
                        <div className="flex items-center gap-2">
                          <Input
                            type="number"
                            min={1}
                            value={newQty}
                            onChange={(e) => setNewQty(parseInt(e.target.value) || 1)}
                            className="w-20 h-10"
                          />
                          <Button size="sm" onClick={() => handleUpdateQty(item.id)} disabled={saving} className="btn-primary">
                            <Save className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => setEditingQty(null)}>Cancel</Button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-lg text-slate-900">×{item.quantity_required}</span>
                          {canEdit() && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => { setEditingQty(item.id); setNewQty(item.quantity_required); }}
                            >
                              <Edit3 className="w-4 h-4 text-industrial-blue" />
                            </Button>
                          )}
                        </div>
                      )}
                      
                      {/* Remove Button */}
                      {canEdit() && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveItem(item.id, item.sku)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        /* History Tab */
        <div className="card-industrial">
          <div className="border-b border-slate-100 p-4 bg-slate-50/50">
            <h2 className="font-heading font-bold text-slate-900">
              Modification History
            </h2>
            <p className="text-xs text-slate-500 mt-1">All changes to this order are logged for accountability</p>
          </div>
          
          {modificationHistory.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {modificationHistory.map((log, index) => (
                <div key={log.id || index} className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                      {getModTypeIcon(log.modification_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-sm">{getModTypeLabel(log.modification_type)}</span>
                        <span className="text-xs text-slate-400">•</span>
                        <span className="text-xs text-slate-500">{log.field_changed}</span>
                      </div>
                      <div className="text-sm mt-1">
                        {log.old_value && (
                          <span className="text-red-600 line-through mr-2">{log.old_value}</span>
                        )}
                        {log.new_value && (
                          <span className="text-green-600 font-medium">{log.new_value}</span>
                        )}
                      </div>
                      {log.reason && (
                        <p className="text-xs text-slate-500 mt-1 italic">Reason: {log.reason}</p>
                      )}
                      <div className="flex items-center gap-2 mt-2 text-xs text-slate-400">
                        <span className="font-medium text-slate-600">{log.modified_by_name}</span>
                        <span>•</span>
                        <span>{format(new Date(log.timestamp), 'dd MMM yyyy, HH:mm:ss')}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400">
              <History className="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p className="font-medium text-slate-600">No modifications yet</p>
              <p className="text-sm">Order has not been modified since creation</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OrderModify;
