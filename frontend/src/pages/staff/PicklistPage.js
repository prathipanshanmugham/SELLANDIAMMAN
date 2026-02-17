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
  CheckCircle,
  QrCode
} from 'lucide-react';
import { format } from 'date-fns';
import { QRCodeSVG } from 'qrcode.react';

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

  // Generate QR code data for billing software integration
  const qrData = JSON.stringify({
    order_id: order.order_number,
    customer: order.customer_name,
    items: order.items.map(item => ({
      sku: item.sku,
      qty: item.quantity_required
    }))
  });

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
        <div className="card-industrial mb-4 sm:mb-6">
          <div className="p-3 sm:p-4 grid grid-cols-2 sm:grid-cols-5 gap-3 sm:gap-4">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Order #</p>
              <p className="font-mono font-bold text-industrial-blue text-sm sm:text-base truncate">{order.order_number}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Customer</p>
              <p className="font-medium text-sm sm:text-base truncate">{order.customer_name}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Staff</p>
              <p className="font-medium text-industrial-orange text-sm sm:text-base">{order.created_by_name}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Date</p>
              <p className="text-xs sm:text-sm">{format(new Date(order.created_at), 'dd MMM, HH:mm')}</p>
            </div>
            <div className="col-span-2 sm:col-span-1">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Status</p>
              {allPicked ? (
                <span className="inline-flex items-center gap-1 text-green-600 font-bold text-sm">
                  <CheckCircle className="w-4 h-4" />
                  Completed
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-amber-600 font-bold text-sm">
                  <Clock className="w-4 h-4" />
                  Pending
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Items */}
        <div className="space-y-3 sm:space-y-4">
          {order.items.map((item, index) => {
            const isPicked = item.picking_status === 'picked';
            return (
              <div 
                key={item.id}
                data-testid={`picklist-item-${item.sku}`}
                className={`card-industrial overflow-hidden ${isPicked ? 'opacity-60' : ''}`}
              >
                <div className={`
                  flex flex-col gap-3 p-3 sm:p-4
                  ${isPicked ? 'bg-green-50' : 'bg-white'}
                `}>
                  {/* Mobile: Top row with number, SKU, status */}
                  <div className="flex items-center gap-3">
                    <div className={`
                      w-10 h-10 sm:w-12 sm:h-12 rounded-sm flex items-center justify-center font-bold text-lg sm:text-xl flex-shrink-0
                      ${isPicked ? 'bg-green-600 text-white' : 'bg-industrial-blue text-white'}
                    `}>
                      {isPicked ? <Check className="w-5 h-5 sm:w-6 sm:h-6" /> : index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono text-xs sm:text-sm px-2 py-0.5 bg-slate-100 rounded">
                          {item.sku}
                        </span>
                        {isPicked && (
                          <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded font-bold">
                            PICKED
                          </span>
                        )}
                      </div>
                      <h3 className="font-heading text-base sm:text-lg font-bold text-slate-900 truncate">
                        {item.product_name}
                      </h3>
                    </div>
                  </div>

                  {/* Mobile: Location + Qty + Button row */}
                  <div className="flex items-center gap-2 sm:gap-4 flex-wrap sm:flex-nowrap">
                    {/* Location - prominent */}
                    <div className="flex items-center gap-2 px-3 py-2 bg-industrial-orange/10 rounded-sm flex-1 sm:flex-none">
                      <MapPin className="w-4 h-4 sm:w-5 sm:h-5 text-industrial-orange flex-shrink-0" />
                      <span className="font-mono text-base sm:text-lg font-bold text-industrial-orange">
                        {item.full_location_code}
                      </span>
                    </div>

                    {/* Quantity */}
                    <div className="text-center px-3 sm:px-4">
                      <p className="text-xs text-slate-500 uppercase tracking-wider">Qty</p>
                      <p className="font-mono text-2xl sm:text-3xl font-bold text-slate-900">
                        {item.quantity_required}
                      </p>
                    </div>

                    {/* Pick Button */}
                    <div className="flex-shrink-0">
                      {isPicked ? (
                        <div className="w-24 sm:w-32 h-10 sm:h-12 bg-green-600 rounded-sm flex items-center justify-center text-white font-bold text-sm sm:text-base">
                          <Check className="w-4 h-4 sm:w-5 sm:h-5 mr-1 sm:mr-2" />
                          Done
                        </div>
                      ) : (
                        <Button
                          data-testid={`pick-item-${item.sku}`}
                          onClick={() => handleMarkPicked(item.id)}
                          disabled={pickingItem === item.id}
                          className="w-24 sm:w-32 h-10 sm:h-12 btn-action text-sm sm:text-base"
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

        {/* Master Barcode Section */}
        <div className="mt-6 card-industrial p-4 sm:p-6">
          <div className="flex flex-col items-center text-center">
            <div className="flex items-center gap-2 mb-4">
              <QrCode className="w-5 h-5 text-industrial-blue" />
              <h3 className="font-heading text-lg font-bold text-slate-900">Master Barcode</h3>
            </div>
            <div className="bg-white p-4 rounded-sm border-2 border-slate-200">
              <QRCodeSVG 
                value={qrData}
                size={180}
                level="M"
                includeMargin={true}
              />
            </div>
            <p className="text-xs text-slate-500 mt-3 max-w-xs">
              Scan to Auto Load Bill - Contains all {order.items.length} items for billing software
            </p>
            <p className="font-mono text-xs text-slate-400 mt-1">{order.order_number}</p>
          </div>
        </div>
      </div>

      {/* Print View - Thermal (80mm) - Ultra Compact Format */}
      <div className="print-only thermal-print hidden">
        <div style={{ width: '72mm', fontFamily: 'monospace', fontSize: '10px', lineHeight: '1.1' }}>
          {/* Header - Compact */}
          <div style={{ textAlign: 'center', marginBottom: '2px' }}>
            <strong style={{ fontSize: '11px' }}>SELLANDIAMMAN TRADERS</strong>
          </div>
          
          {/* Order Info - Single Line */}
          <div style={{ borderTop: '1px dashed #000', borderBottom: '1px dashed #000', padding: '2px 0', margin: '2px 0', fontSize: '9px' }}>
            <strong>{order.order_number}</strong> | {format(new Date(order.created_at), 'dd/MM HH:mm')} | {order.customer_name}
          </div>

          {/* Items - One Line Each: Product | Location | xQty */}
          {order.items.map((item, idx) => {
            // Compress location code: A-03-R07-S2-B05 -> A03R07S2B05
            const compactLoc = item.full_location_code.replace(/-/g, '').replace(/R/g, 'R').replace(/S/g, 'S').replace(/B/g, 'B');
            // Truncate product name
            const shortName = item.product_name.length > 20 ? item.product_name.substring(0, 20) + '..' : item.product_name;
            return (
              <div key={item.id} style={{ fontSize: '9px', padding: '1px 0', borderBottom: '1px dotted #ccc' }}>
                {idx + 1}. {shortName} | <strong>{compactLoc}</strong> | <strong>x{item.quantity_required}</strong>
              </div>
            );
          })}

          {/* Footer - Minimal */}
          <div style={{ textAlign: 'center', marginTop: '3px', paddingTop: '2px', borderTop: '1px dashed #000' }}>
            <div style={{ margin: '4px auto', display: 'flex', justifyContent: 'center' }}>
              <QRCodeSVG 
                value={qrData}
                size={80}
                level="L"
                includeMargin={false}
              />
            </div>
            <div style={{ fontSize: '8px' }}>
              Scan for Bill | {order.items.length} items | {format(new Date(), 'dd/MM HH:mm')}
            </div>
            <div style={{ fontSize: '8px', marginTop: '2px' }}>Thank You!</div>
          </div>
        </div>
      </div>

      {/* Print styles - Dynamic Height */}
      <style>{`
        @media print {
          @page { 
            size: 80mm auto; 
            margin: 1mm; 
          }
          body * { visibility: hidden; }
          .print-only, .print-only * { visibility: visible !important; display: block !important; }
          .print-only { position: absolute; left: 0; top: 0; }
        }
      `}</style>
    </div>
  );
};

export default PicklistPage;
