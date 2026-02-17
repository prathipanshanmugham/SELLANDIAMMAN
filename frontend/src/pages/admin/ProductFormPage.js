import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';
import { ArrowLeft, Save, Package, MapPin, IndianRupee } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ProductFormPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  const [form, setForm] = useState({
    sku: '',
    product_name: '',
    category: '',
    brand: '',
    zone: '',
    aisle: 1,
    rack: 1,
    shelf: 1,
    bin: 1,
    quantity_available: 0,
    reorder_level: 10,
    supplier: '',
    image_url: '',
    selling_price: 0,
    mrp: 0,
    unit: 'piece',
    gst_percentage: 18
  });

  useEffect(() => {
    if (isEdit) {
      fetchProduct();
    }
  }, [id]);

  const fetchProduct = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/products/${id}`);
      setForm(response.data);
    } catch (error) {
      toast.error('Failed to load product');
      navigate('/admin/products');
    } finally {
      setLoading(false);
    }
  };

  const generateLocationCode = () => {
    const { zone, aisle, rack, shelf, bin } = form;
    if (!zone) return '';
    return `${zone}-${String(aisle).padStart(2, '0')}-R${String(rack).padStart(2, '0')}-S${shelf}-B${String(bin).padStart(2, '0')}`;
  };

  const handleChange = (field, value) => {
    setForm({ ...form, [field]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      if (isEdit) {
        await axios.put(`${API_URL}/api/products/${id}`, form);
        toast.success('Product updated successfully');
      } else {
        await axios.post(`${API_URL}/api/products`, form);
        toast.success('Product created successfully');
      }
      navigate('/admin/products');
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to save product';
      toast.error(message);
    } finally {
      setSaving(false);
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
    <div className="max-w-4xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate('/admin/products')}
          className="p-2"
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="font-heading text-2xl font-bold text-slate-900">
            {isEdit ? 'Edit Product' : 'Add New Product'}
          </h1>
          <p className="text-slate-500 text-sm">
            {isEdit ? 'Update product details and location' : 'Enter product details to add to inventory'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="card-industrial">
          <div className="border-b border-slate-100 p-4 bg-slate-50/50 flex items-center gap-2">
            <Package className="w-5 h-5 text-industrial-blue" />
            <h2 className="font-heading font-bold text-slate-900">Product Information</h2>
          </div>
          <div className="p-6 grid sm:grid-cols-2 gap-6">
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                SKU *
              </Label>
              <Input
                data-testid="product-sku-input"
                value={form.sku}
                onChange={(e) => handleChange('sku', e.target.value.toUpperCase())}
                placeholder="ELX1001"
                className="mt-2 input-industrial font-mono"
                required
                disabled={isEdit}
              />
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Category *
              </Label>
              <Input
                data-testid="product-category-input"
                value={form.category}
                onChange={(e) => handleChange('category', e.target.value)}
                placeholder="Wires & Cables"
                className="mt-2 input-industrial"
                required
              />
            </div>
            
            <div className="sm:col-span-2">
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Product Name *
              </Label>
              <Input
                data-testid="product-name-input"
                value={form.product_name}
                onChange={(e) => handleChange('product_name', e.target.value)}
                placeholder="2.5 Sqmm Copper Wire"
                className="mt-2 input-industrial"
                required
              />
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Brand
              </Label>
              <Input
                data-testid="product-brand-input"
                value={form.brand}
                onChange={(e) => handleChange('brand', e.target.value)}
                placeholder="Havells"
                className="mt-2 input-industrial"
              />
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Supplier
              </Label>
              <Input
                data-testid="product-supplier-input"
                value={form.supplier}
                onChange={(e) => handleChange('supplier', e.target.value)}
                placeholder="ABC Distributors"
                className="mt-2 input-industrial"
              />
            </div>
            
            <div className="sm:col-span-2">
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Image URL
              </Label>
              <Input
                data-testid="product-image-input"
                value={form.image_url}
                onChange={(e) => handleChange('image_url', e.target.value)}
                placeholder="https://example.com/image.jpg"
                className="mt-2 input-industrial"
              />
            </div>
          </div>
        </div>

        {/* Location */}
        <div className="card-industrial">
          <div className="border-b border-slate-100 p-4 bg-slate-50/50 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-industrial-orange" />
            <h2 className="font-heading font-bold text-slate-900">Warehouse Location</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-6">
              <div>
                <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                  Zone *
                </Label>
                <Input
                  data-testid="product-zone-input"
                  value={form.zone}
                  onChange={(e) => handleChange('zone', e.target.value.toUpperCase())}
                  placeholder="A"
                  className="mt-2 input-industrial font-mono text-center"
                  maxLength={2}
                  required
                />
              </div>
              
              <div>
                <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                  Aisle *
                </Label>
                <Input
                  data-testid="product-aisle-input"
                  type="number"
                  value={form.aisle}
                  onChange={(e) => handleChange('aisle', parseInt(e.target.value) || 1)}
                  min={1}
                  max={99}
                  className="mt-2 input-industrial font-mono text-center"
                  required
                />
              </div>
              
              <div>
                <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                  Rack *
                </Label>
                <Input
                  data-testid="product-rack-input"
                  type="number"
                  value={form.rack}
                  onChange={(e) => handleChange('rack', parseInt(e.target.value) || 1)}
                  min={1}
                  max={99}
                  className="mt-2 input-industrial font-mono text-center"
                  required
                />
              </div>
              
              <div>
                <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                  Shelf *
                </Label>
                <Input
                  data-testid="product-shelf-input"
                  type="number"
                  value={form.shelf}
                  onChange={(e) => handleChange('shelf', parseInt(e.target.value) || 1)}
                  min={1}
                  max={9}
                  className="mt-2 input-industrial font-mono text-center"
                  required
                />
              </div>
              
              <div>
                <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                  Bin *
                </Label>
                <Input
                  data-testid="product-bin-input"
                  type="number"
                  value={form.bin}
                  onChange={(e) => handleChange('bin', parseInt(e.target.value) || 1)}
                  min={1}
                  max={99}
                  className="mt-2 input-industrial font-mono text-center"
                  required
                />
              </div>
            </div>
            
            {/* Location Preview */}
            <div className="bg-slate-100 rounded-sm p-4 text-center">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Generated Location Code</p>
              <p className="font-mono text-2xl font-bold text-industrial-blue">
                {generateLocationCode() || 'Enter zone to generate'}
              </p>
            </div>
          </div>
        </div>

        {/* Stock */}
        <div className="card-industrial">
          <div className="border-b border-slate-100 p-4 bg-slate-50/50">
            <h2 className="font-heading font-bold text-slate-900">Stock Information</h2>
          </div>
          <div className="p-6 grid sm:grid-cols-2 gap-6">
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Quantity Available *
              </Label>
              <Input
                data-testid="product-quantity-input"
                type="number"
                value={form.quantity_available}
                onChange={(e) => handleChange('quantity_available', parseInt(e.target.value) || 0)}
                min={0}
                className="mt-2 input-industrial font-mono"
                required
              />
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                Reorder Level
              </Label>
              <Input
                data-testid="product-reorder-input"
                type="number"
                value={form.reorder_level}
                onChange={(e) => handleChange('reorder_level', parseInt(e.target.value) || 0)}
                min={0}
                className="mt-2 input-industrial font-mono"
              />
              <p className="text-xs text-slate-500 mt-1">Alert when stock falls below this level</p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4 justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/admin/products')}
            className="btn-secondary"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            data-testid="save-product-btn"
            disabled={saving}
            className="btn-action"
          >
            {saving ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
            ) : (
              <>
                <Save className="w-5 h-5 mr-2" />
                {isEdit ? 'Update Product' : 'Add Product'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ProductFormPage;
