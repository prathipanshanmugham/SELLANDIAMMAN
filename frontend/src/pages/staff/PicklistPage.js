import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/button';
import { toast } from 'sonner';
import { 
  ArrowLeft, 
  Printer, 
  Check,
  MapPin,
  Package,
  Clock,
  CheckCircle
} from 'lucide-react';
import { format } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PicklistPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pickingItem, setPickingItem] = useState(null);
  const printRef = useRef();

  useEffect(() => {
    fetchOrder();
  }, [id]);

  const fetchOrder = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/orders/${id}`);
      setOrder(response.data);
    } catch (error) {
      toast.error('Failed to load order');
      navigate(isAdmin() ? '/admin/orders' : '/staff/orders');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkPicked = async (itemId) => {
    setPickingItem(itemId);
    try {
      await axios.patch(`${API_URL}/api/orders/${id}/items/${itemId}/pick`);
      toast.success('Item marked as picked! Stock deducted.');
      fetchOrder();
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to mark item';
      toast.error(message);
    } finally {
      setPickingItem(null);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
      </div>
    );
  }

  if (!order) return null;

  const allPicked = order.items.every(item => item.picking_status === 'picked');
  const basePath = isAdmin() ? '/admin' : '/staff';

  return (
    <div className="animate-fade-in">
      {/* Screen View */}
      <div className="no-print">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              onClick={() => navigate(`${basePath}/orders`)}
              className="p-2"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="font-heading text-2xl font-bold text-slate-900">
                Pick List
              </h1>
              <p className="text-slate-500 text-sm font-mono">{order.order_number}</p>
            </div>
          </div>
          <Button
            data-testid="print-picklist-btn"
            onClick={handlePrint}
            className="btn-action"
          >
            <Printer className="w-5 h-5 mr-2" />
            Print
          </Button>
        </div>

        {/* Order Info */}
        <div className="card-industrial mb-6">
          <div className="p-4 grid sm:grid-cols-5 gap-4">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Order #</p>
              <p className="font-mono font-bold text-industrial-blue">{order.order_number}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Customer</p>
              <p className="font-medium">{order.customer_name}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Created By</p>
              <p className="font-medium text-industrial-orange">{order.created_by_name}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Date</p>
              <p className="text-sm">{format(new Date(order.created_at), 'dd MMM yyyy, HH:mm')}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Status</p>
              {allPicked ? (
                <span className="inline-flex items-center gap-1 text-green-600 font-bold">
                  <CheckCircle className="w-4 h-4" />
                  Completed
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-amber-600 font-bold">
                  <Clock className="w-4 h-4" />
                  Pending
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Items */}
        <div className="space-y-4">
          {order.items.map((item, index) => {
            const isPicked = item.picking_status === 'picked';
            return (
              <div 
                key={item.id}
                data-testid={`picklist-item-${item.sku}`}
                className={`card-industrial overflow-hidden ${isPicked ? 'opacity-60' : ''}`}
              >
                <div className={`
                  flex flex-col sm:flex-row sm:items-center gap-4 p-4
                  ${isPicked ? 'bg-green-50' : 'bg-white'}
                `}>
                  {/* Item Number */}
                  <div className={`
                    w-12 h-12 rounded-sm flex items-center justify-center font-bold text-xl flex-shrink-0
                    ${isPicked ? 'bg-green-600 text-white' : 'bg-industrial-blue text-white'}
                  `}>
                    {isPicked ? <Check className="w-6 h-6" /> : index + 1}
                  </div>

                  {/* Product Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-2 mb-1">
                      <span className="font-mono text-sm px-2 py-0.5 bg-slate-100 rounded">
                        {item.sku}
                      </span>
                      {isPicked && (
                        <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded font-bold">
                          PICKED
                        </span>
                      )}
                    </div>
                    <h3 className="font-heading text-lg font-bold text-slate-900">
                      {item.product_name}
                    </h3>
                  </div>

                  {/* Location */}
                  <div className="flex items-center gap-2 px-4 py-2 bg-industrial-orange/10 rounded-sm">
                    <MapPin className="w-5 h-5 text-industrial-orange" />
                    <span className="font-mono text-lg font-bold text-industrial-orange">
                      {item.full_location_code}
                    </span>
                  </div>

                  {/* Quantity */}
                  <div className="text-center px-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Qty</p>
                    <p className="font-mono text-3xl font-bold text-slate-900">
                      {item.quantity_required}
                    </p>
                  </div>

                  {/* Pick Button */}
                  <div className="flex-shrink-0">
                    {isPicked ? (
                      <div className="w-32 h-12 bg-green-600 rounded-sm flex items-center justify-center text-white font-bold">
                        <Check className="w-5 h-5 mr-2" />
                        Done
                      </div>
                    ) : (
                      <Button
                        data-testid={`pick-item-${item.sku}`}
                        onClick={() => handleMarkPicked(item.id)}
                        disabled={pickingItem === item.id}
                        className="w-32 h-12 btn-action"
                      >
                        {pickingItem === item.id ? (
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                        ) : (
                          <>
                            <Check className="w-5 h-5 mr-2" />
                            Pick
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className="mt-6 card-industrial p-4 flex items-center justify-between">
          <div>
            <span className="text-slate-500">Total Items: </span>
            <span className="font-bold">{order.items.length}</span>
          </div>
          <div>
            <span className="text-slate-500">Picked: </span>
            <span className="font-bold text-green-600">
              {order.items.filter(i => i.picking_status === 'picked').length}
            </span>
            <span className="text-slate-500"> / {order.items.length}</span>
          </div>
        </div>
      </div>

      {/* Print View - Thermal (80mm) - Compact for minimal paper */}
      <div className="print-only thermal-print hidden">
        <div style={{ width: '72mm', fontFamily: 'monospace', fontSize: '11px', lineHeight: '1.2' }}>
          <div style={{ textAlign: 'center', marginBottom: '4px' }}>
            <strong style={{ fontSize: '12px' }}>SELLANDIAMMAN TRADERS</strong>
          </div>
          
          <div style={{ borderTop: '1px dashed black', padding: '2px 0', marginBottom: '4px', fontSize: '10px' }}>
            <strong>{order.order_number}</strong> | {format(new Date(order.created_at), 'dd/MM HH:mm')}
            <br />
            {order.customer_name} | Staff: {order.created_by_name}
          </div>

          {order.items.map((item, idx) => (
            <div key={item.id} style={{ padding: '2px 0', borderBottom: '1px dotted #999', fontSize: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <strong>{idx + 1}.{item.sku}</strong>
                <strong>x{item.quantity_required}</strong>
              </div>
              <div>{item.product_name.length > 28 ? item.product_name.substring(0, 28) + '..' : item.product_name}</div>
              <strong style={{ fontSize: '12px' }}>{item.full_location_code}</strong>
            </div>
          ))}

          <div style={{ textAlign: 'center', marginTop: '4px', borderTop: '1px dashed black', paddingTop: '2px', fontSize: '10px' }}>
            <strong>Items: {order.items.length}</strong> | {format(new Date(), 'dd/MM HH:mm')}
          </div>
        </div>
      </div>

      {/* Print styles */}
      <style>{`
        @media print {
          @page { size: 80mm auto; margin: 2mm; }
          body * { visibility: hidden; }
          .print-only, .print-only * { visibility: visible !important; display: block !important; }
          .print-only { position: absolute; left: 0; top: 0; }
        }
      `}</style>
    </div>
  );
};

export default PicklistPage;
