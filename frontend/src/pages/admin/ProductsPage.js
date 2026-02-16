import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { toast } from 'sonner';
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Package,
  MapPin,
  AlertTriangle,
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

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ProductsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState(null);
  
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category: searchParams.get('category') || '',
    zone: searchParams.get('zone') || '',
    low_stock: searchParams.get('low_stock') === 'true'
  });

  useEffect(() => {
    fetchFilters();
  }, []);

  useEffect(() => {
    fetchProducts();
    // Update URL params
    const params = new URLSearchParams();
    if (filters.search) params.set('search', filters.search);
    if (filters.category) params.set('category', filters.category);
    if (filters.zone) params.set('zone', filters.zone);
    if (filters.low_stock) params.set('low_stock', 'true');
    setSearchParams(params);
  }, [filters]);

  const fetchFilters = async () => {
    try {
      const [catRes, zoneRes] = await Promise.all([
        axios.get(`${API_URL}/api/products/categories`),
        axios.get(`${API_URL}/api/products/zones`)
      ]);
      setCategories(catRes.data);
      setZones(zoneRes.data);
    } catch (error) {
      console.error('Failed to fetch filters:', error);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.search) params.append('search', filters.search);
      if (filters.category && filters.category !== 'all') params.append('category', filters.category);
      if (filters.zone && filters.zone !== 'all') params.append('zone', filters.zone);
      if (filters.low_stock) params.append('low_stock', 'true');
      
      const response = await axios.get(`${API_URL}/api/products?${params}`);
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    
    try {
      await axios.delete(`${API_URL}/api/products/${deleteId}`);
      toast.success('Product deleted successfully');
      fetchProducts();
    } catch (error) {
      toast.error('Failed to delete product');
    } finally {
      setDeleteId(null);
    }
  };

  const clearFilters = () => {
    setFilters({ search: '', category: '', zone: '', low_stock: false });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl font-bold text-slate-900">Products</h1>
          <p className="text-slate-500 text-sm mt-1">{products.length} products found</p>
        </div>
        <Link to="/admin/products/new">
          <Button data-testid="add-product-btn" className="btn-action">
            <Plus className="w-5 h-5 mr-2" />
            Add Product
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="card-industrial p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <Input
              data-testid="products-search-input"
              placeholder="Search SKU, name, or location..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="pl-10 input-industrial"
            />
          </div>
          
          <div className="flex gap-2 flex-wrap">
            <Select 
              value={filters.category} 
              onValueChange={(v) => setFilters({ ...filters, category: v })}
            >
              <SelectTrigger data-testid="filter-category" className="w-40 h-12">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select 
              value={filters.zone} 
              onValueChange={(v) => setFilters({ ...filters, zone: v })}
            >
              <SelectTrigger data-testid="filter-zone" className="w-32 h-12">
                <SelectValue placeholder="Zone" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Zones</SelectItem>
                {zones.map((zone) => (
                  <SelectItem key={zone} value={zone}>{zone}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Button
              data-testid="filter-low-stock"
              variant={filters.low_stock ? 'default' : 'outline'}
              onClick={() => setFilters({ ...filters, low_stock: !filters.low_stock })}
              className={`h-12 ${filters.low_stock ? 'bg-red-600 hover:bg-red-700' : ''}`}
            >
              <AlertTriangle className="w-4 h-4 mr-2" />
              Low Stock
            </Button>
            
            {(filters.search || filters.category || filters.zone || filters.low_stock) && (
              <Button
                variant="ghost"
                onClick={clearFilters}
                className="h-12 text-slate-500"
              >
                Clear
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Products Table/Cards */}
      <div className="card-industrial overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
          </div>
        ) : products.length === 0 ? (
          <div className="p-8 sm:p-12 text-center">
            <Package className="w-12 h-12 sm:w-16 sm:h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-heading text-lg sm:text-xl font-bold text-slate-700">No Products Found</h3>
            <p className="text-slate-500 mt-2 mb-6 text-sm">
              {filters.search || filters.category || filters.zone || filters.low_stock
                ? 'Try adjusting your filters'
                : 'Get started by adding your first product'}
            </p>
            <Link to="/admin/products/new">
              <Button className="btn-primary">
                <Plus className="w-4 h-4 mr-2" />
                Add Product
              </Button>
            </Link>
          </div>
        ) : (
          <>
            {/* Desktop Table View */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="table-header text-left">SKU</th>
                    <th className="table-header text-left">Product</th>
                    <th className="table-header text-left">Category</th>
                    <th className="table-header text-left">Location</th>
                    <th className="table-header text-right">Stock</th>
                    <th className="table-header text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((product) => {
                    const isLowStock = product.quantity_available <= product.reorder_level;
                    return (
                      <tr key={product.id} className="table-row" data-testid={`product-row-${product.sku}`}>
                        <td className="table-cell-mono font-medium">{product.sku}</td>
                        <td className="table-cell">
                          <div>
                            <p className="font-medium text-slate-900">{product.product_name}</p>
                            {product.brand && (
                              <p className="text-xs text-slate-500">{product.brand}</p>
                            )}
                          </div>
                        </td>
                        <td className="table-cell">
                          <span className="px-2 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded">
                            {product.category}
                          </span>
                        </td>
                        <td className="table-cell">
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-slate-400" />
                            <span className="font-mono text-sm">{product.full_location_code}</span>
                          </div>
                        </td>
                        <td className="table-cell text-right">
                          <span className={`font-bold ${isLowStock ? 'text-red-600' : 'text-green-600'}`}>
                            {product.quantity_available}
                          </span>
                          {isLowStock && (
                            <AlertTriangle className="w-4 h-4 text-red-500 inline ml-1" />
                          )}
                        </td>
                        <td className="table-cell">
                          <div className="flex items-center justify-center gap-2">
                            <Link to={`/admin/products/${product.id}/edit`}>
                              <Button 
                                variant="ghost" 
                                size="sm"
                                data-testid={`edit-product-${product.sku}`}
                                className="text-industrial-blue hover:text-industrial-blue-dark"
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                            </Link>
                            <Button
                              variant="ghost"
                              size="sm"
                              data-testid={`delete-product-${product.sku}`}
                              onClick={() => setDeleteId(product.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            
            {/* Mobile Card View */}
            <div className="md:hidden divide-y divide-slate-100">
              {products.map((product) => {
                const isLowStock = product.quantity_available <= product.reorder_level;
                return (
                  <div 
                    key={product.id} 
                    data-testid={`product-card-${product.sku}`}
                    className="p-3"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono text-xs px-1.5 py-0.5 bg-industrial-blue text-white rounded">
                            {product.sku}
                          </span>
                          <span className="text-xs px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded">
                            {product.category}
                          </span>
                        </div>
                        <p className="font-medium text-sm mt-1 truncate">{product.product_name}</p>
                        {product.brand && (
                          <p className="text-xs text-slate-500">{product.brand}</p>
                        )}
                      </div>
                      <div className="flex gap-1 flex-shrink-0">
                        <Link to={`/admin/products/${product.id}/edit`}>
                          <Button variant="ghost" size="sm" className="p-2 h-8 w-8">
                            <Edit className="w-4 h-4 text-industrial-blue" />
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteId(product.id)}
                          className="p-2 h-8 w-8"
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-100">
                      <div className="flex items-center gap-1.5 text-industrial-orange">
                        <MapPin className="w-3.5 h-3.5" />
                        <span className="font-mono text-xs font-medium">{product.full_location_code}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className={`font-mono font-bold text-sm ${isLowStock ? 'text-red-600' : 'text-green-600'}`}>
                          {product.quantity_available}
                        </span>
                        {isLowStock && <AlertTriangle className="w-3.5 h-3.5 text-red-500" />}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Product?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the product from your inventory.
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

export default ProductsPage;
