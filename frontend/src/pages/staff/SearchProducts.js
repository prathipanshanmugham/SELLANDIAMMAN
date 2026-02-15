import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { 
  Search, 
  Package,
  MapPin,
  AlertTriangle
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SearchProducts = () => {
  const [search, setSearch] = useState('');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (search.trim()) {
        fetchProducts();
      } else {
        setProducts([]);
        setSearched(false);
      }
    }, 300);
    
    return () => clearTimeout(timer);
  }, [search]);

  const fetchProducts = async () => {
    setLoading(true);
    setSearched(true);
    try {
      const response = await axios.get(`${API_URL}/api/products?search=${encodeURIComponent(search)}`);
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to search:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Search Box */}
      <div className="card-industrial p-6">
        <div className="max-w-2xl mx-auto">
          <h1 className="font-heading text-2xl font-bold text-slate-900 text-center mb-2">
            Product Search
          </h1>
          <p className="text-slate-500 text-center mb-6">
            Search by SKU, product name, or location code
          </p>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400" />
            <Input
              ref={inputRef}
              data-testid="product-search-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Type SKU or product name..."
              className="h-14 pl-14 text-lg border-2 border-slate-300 focus:border-industrial-orange"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                Clear
              </button>
            )}
          </div>
          <p className="text-xs text-slate-400 text-center mt-2">
            Press Tab to navigate • Results update as you type
          </p>
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-industrial-blue"></div>
        </div>
      ) : searched ? (
        products.length > 0 ? (
          <div className="space-y-3">
            <p className="text-sm text-slate-500">{products.length} results found</p>
            {products.map((product) => {
              const isLowStock = product.quantity_available <= product.reorder_level;
              return (
                <div 
                  key={product.id}
                  data-testid={`search-result-${product.sku}`}
                  className="card-industrial overflow-hidden hover:shadow-md transition-shadow"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center gap-4 p-4">
                    {/* Product Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-sm px-2 py-0.5 bg-industrial-blue text-white rounded">
                          {product.sku}
                        </span>
                        <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded">
                          {product.category}
                        </span>
                      </div>
                      <h3 className="font-heading text-lg font-bold text-slate-900">
                        {product.product_name}
                      </h3>
                      {product.brand && (
                        <p className="text-sm text-slate-500">{product.brand}</p>
                      )}
                    </div>

                    {/* Location - Highlighted */}
                    <div className="flex items-center gap-3 px-4 py-3 bg-industrial-orange/10 rounded-sm">
                      <MapPin className="w-6 h-6 text-industrial-orange" />
                      <div>
                        <p className="text-xs text-industrial-orange uppercase tracking-wider font-semibold">Location</p>
                        <p className="font-mono text-xl font-bold text-industrial-orange">
                          {product.full_location_code}
                        </p>
                      </div>
                    </div>

                    {/* Stock */}
                    <div className={`
                      text-center px-4 py-3 rounded-sm
                      ${isLowStock ? 'bg-red-50' : 'bg-green-50'}
                    `}>
                      <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Stock</p>
                      <div className="flex items-center gap-2 justify-center">
                        <span className={`
                          font-mono text-2xl font-bold
                          ${isLowStock ? 'text-red-600' : 'text-green-600'}
                        `}>
                          {product.quantity_available}
                        </span>
                        {isLowStock && <AlertTriangle className="w-5 h-5 text-red-500" />}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="card-industrial p-12 text-center">
            <Package className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-heading text-xl font-bold text-slate-700">No Products Found</h3>
            <p className="text-slate-500 mt-2">
              Try a different search term or SKU
            </p>
          </div>
        )
      ) : (
        <div className="card-industrial p-12 text-center">
          <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="font-heading text-xl font-bold text-slate-700">Start Searching</h3>
          <p className="text-slate-500 mt-2">
            Enter a SKU or product name to find location
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchProducts;
