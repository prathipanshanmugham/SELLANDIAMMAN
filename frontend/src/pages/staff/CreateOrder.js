import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';
import { 
  Plus, 
  Trash2, 
  ShoppingCart,
  Search,
  Package,
  MapPin,
  ArrowRight
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CreateOrder = () => {
  const navigate = useNavigate();
  const [customerName, setCustomerName] = useState('');
  const [items, setItems] = useState([]);
  const [skuInput, setSkuInput] = useState('');
  const [qtyInput, setQtyInput] = useState(1);
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  const skuInputRef = useRef(null);
  const qtyInputRef = useRef(null);

  useEffect(() => {
    skuInputRef.current?.focus();
  }, []);

  // Search products as user types
  useEffect(() => {
    const timer = setTimeout(() => {
      if (skuInput.trim().length >= 2) {
        searchProducts();
      } else {
        setSearchResults([]);
      }
    }, 200);
    return () => clearTimeout(timer);
  }, [skuInput]);

  const searchProducts = async () => {
    setSearching(true);
    try {
      const response = await axios.get(`${API_URL}/api/products?search=${encodeURIComponent(skuInput)}`);
      setSearchResults(response.data.slice(0, 5));
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  const addItem = (product) => {
    const existing = items.find(i => i.sku === product.sku);
    if (existing) {
      setItems(items.map(i => 
        i.sku === product.sku 
          ? { ...i, quantity_required: i.quantity_required + qtyInput }
          : i
      ));
    } else {
      setItems([...items, {
        sku: product.sku,
        product_name: product.product_name,
        full_location_code: product.full_location_code,
        quantity_required: qtyInput,
        quantity_available: product.quantity_available
      }]);
    }
    
    setSkuInput('');
    setQtyInput(1);
    setSearchResults([]);
    skuInputRef.current?.focus();
    toast.success(`Added ${product.product_name}`);
  };

  const removeItem = (sku) => {
    setItems(items.filter(i => i.sku !== sku));
  };

  const updateQuantity = (sku, qty) => {
    if (qty < 1) return;
    setItems(items.map(i => i.sku === sku ? { ...i, quantity_required: qty } : i));
  };

  const handleSubmit = async () => {
    if (!customerName.trim()) {
      toast.error('Please enter customer name');
      return;
    }
    if (items.length === 0) {
      toast.error('Please add at least one item');
      return;
    }

    setSubmitting(true);
    try {
      const response = await axios.post(`${API_URL}/api/orders`, {
        customer_name: customerName,
        items: items.map(i => ({ sku: i.sku, quantity_required: i.quantity_required }))
      });
      
      toast.success('Order created successfully!');
      navigate(`/staff/orders/${response.data.id}`);
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to create order';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && searchResults.length > 0) {
      e.preventDefault();
      addItem(searchResults[0]);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="font-heading text-2xl font-bold text-slate-900">Create Order</h1>
        <p className="text-slate-500 text-sm mt-1">Add items to create a new sales order</p>
      </div>

      {/* Customer Name */}
      <div className="card-industrial p-4">
        <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
          Customer Name *
        </Label>
        <Input
          data-testid="customer-name-input"
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
          placeholder="Enter customer name"
          className="mt-2 input-industrial"
        />
      </div>

      {/* Add Item */}
      <div className="card-industrial p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
              SKU / Product Name
            </Label>
            <div className="relative mt-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                ref={skuInputRef}
                data-testid="sku-search-input"
                value={skuInput}
                onChange={(e) => setSkuInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type SKU or name..."
                className="pl-10 input-industrial"
              />
            </div>
            
            {/* Search Results Dropdown */}
            {searchResults.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-slate-200 rounded-sm shadow-lg max-h-60 overflow-auto">
                {searchResults.map((product) => (
                  <button
                    key={product.sku}
                    data-testid={`search-option-${product.sku}`}
                    onClick={() => addItem(product)}
                    className="w-full px-4 py-3 text-left hover:bg-slate-50 border-b border-slate-100 last:border-b-0"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-mono text-sm text-industrial-blue font-bold">{product.sku}</span>
                        <p className="text-sm font-medium">{product.product_name}</p>
                      </div>
                      <div className="text-right text-xs">
                        <p className="font-mono text-industrial-orange">{product.full_location_code}</p>
                        <p className="text-slate-500">Stock: {product.quantity_available}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
          
          <div className="w-24">
            <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
              Qty
            </Label>
            <Input
              ref={qtyInputRef}
              data-testid="qty-input"
              type="number"
              value={qtyInput}
              onChange={(e) => setQtyInput(parseInt(e.target.value) || 1)}
              min={1}
              className="mt-2 input-industrial text-center font-mono"
            />
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Type to search • Press Enter to add first result • [Tab] to move between fields
        </p>
      </div>

      {/* Items List */}
      <div className="card-industrial overflow-hidden">
        <div className="border-b border-slate-100 p-4 bg-slate-50/50 flex items-center justify-between">
          <h3 className="font-heading font-bold text-slate-900">
            Order Items
            {items.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-industrial-blue text-white text-xs font-bold rounded">
                {items.length}
              </span>
            )}
          </h3>
        </div>
        
        {items.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {items.map((item, idx) => (
              <div 
                key={item.sku}
                data-testid={`order-item-${item.sku}`}
                className="flex items-center gap-4 p-4"
              >
                <div className="w-8 h-8 bg-industrial-blue text-white rounded-sm flex items-center justify-center font-bold">
                  {idx + 1}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="font-mono text-sm text-industrial-blue">{item.sku}</p>
                  <p className="font-medium truncate">{item.product_name}</p>
                </div>
                
                <div className="flex items-center gap-2 text-industrial-orange">
                  <MapPin className="w-4 h-4" />
                  <span className="font-mono text-sm">{item.full_location_code}</span>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => updateQuantity(item.sku, item.quantity_required - 1)}
                    className="w-8 h-8 border border-slate-300 rounded-sm hover:bg-slate-100"
                  >
                    -
                  </button>
                  <Input
                    type="number"
                    value={item.quantity_required}
                    onChange={(e) => updateQuantity(item.sku, parseInt(e.target.value) || 1)}
                    className="w-16 h-8 text-center font-mono"
                    min={1}
                  />
                  <button
                    onClick={() => updateQuantity(item.sku, item.quantity_required + 1)}
                    className="w-8 h-8 border border-slate-300 rounded-sm hover:bg-slate-100"
                  >
                    +
                  </button>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeItem(item.sku)}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <Package className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500">No items added yet</p>
            <p className="text-xs text-slate-400 mt-1">Search and add products above</p>
          </div>
        )}
      </div>

      {/* Submit */}
      <div className="flex gap-4 justify-end">
        <Button
          variant="outline"
          onClick={() => navigate('/staff/orders')}
          className="btn-secondary"
        >
          Cancel
        </Button>
        <Button
          data-testid="create-order-submit"
          onClick={handleSubmit}
          disabled={submitting || items.length === 0}
          className="btn-action"
        >
          {submitting ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
          ) : (
            <>
              <ShoppingCart className="w-5 h-5 mr-2" />
              Create Order ({items.length} items)
              <ArrowRight className="w-5 h-5 ml-2" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

export default CreateOrder;
