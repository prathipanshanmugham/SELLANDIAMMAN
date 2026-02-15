import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import axios from 'axios';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Zap, Search, Package, Phone, ArrowRight } from 'lucide-react';
import WhatsAppButton from '../../components/WhatsAppButton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CataloguePage = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [search, category]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/public/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (category && category !== 'all') params.append('category', category);
      
      const response = await axios.get(`${API_URL}/api/public/catalogue?${params}`);
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Helmet>
        <title>Product Catalogue | Sellandiamman Traders - Electrical Products Perundurai</title>
        <meta name="description" content="Browse 10,000+ electrical products at Sellandiamman Traders. Wires, cables, MCBs, switches, power tools, lighting from top brands like Havells, Schneider, Legrand, Philips." />
        <meta property="og:title" content="Product Catalogue | Sellandiamman Traders" />
        <meta property="og:description" content="Browse our extensive range of electrical products. Quality wires, cables, MCBs, switches, and more." />
        <link rel="canonical" href={window.location.origin + "/catalogue"} />
      </Helmet>
      {/* Navigation */}
      <nav className="bg-industrial-blue text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-industrial-orange rounded-sm flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="font-heading text-lg font-bold tracking-tight">SELLANDIAMMAN</h1>
                <p className="text-xs text-slate-300">Traders</p>
              </div>
            </Link>
            
            <div className="hidden md:flex items-center gap-6">
              <Link to="/" className="text-slate-300 hover:text-white transition-colors">Home</Link>
              <Link to="/catalogue" className="text-white font-medium hover:text-industrial-orange transition-colors">Catalogue</Link>
              <Link to="/contact" className="text-slate-300 hover:text-white transition-colors">Contact</Link>
            </div>
            
            <Link to="/login">
              <Button className="btn-action text-sm">Staff Login</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="font-heading text-3xl lg:text-4xl font-bold text-slate-900 tracking-tight">
            Product Catalogue
          </h1>
          <p className="mt-2 text-slate-600">
            Browse our extensive range of electrical products
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                data-testid="catalogue-search-input"
                placeholder="Search by SKU or product name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 input-industrial"
              />
            </div>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger data-testid="category-filter" className="w-full sm:w-48 h-12">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-industrial-blue"></div>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-16">
            <Package className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-heading text-xl font-bold text-slate-700">No Products Found</h3>
            <p className="text-slate-500 mt-2">Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-500 mb-6">{products.length} products found</p>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map((product) => (
                <div 
                  key={product.sku} 
                  data-testid={`product-card-${product.sku}`}
                  className="card-industrial overflow-hidden hover:shadow-md transition-shadow"
                >
                  <div className="aspect-square bg-slate-100 relative">
                    {product.image_url ? (
                      <img 
                        src={product.image_url} 
                        alt={product.product_name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Package className="w-16 h-16 text-slate-300" />
                      </div>
                    )}
                    <span className="absolute top-2 left-2 bg-industrial-blue text-white text-xs font-mono px-2 py-1 rounded-sm">
                      {product.sku}
                    </span>
                  </div>
                  <div className="p-4">
                    <p className="text-xs text-industrial-orange font-medium uppercase tracking-wider mb-1">
                      {product.category}
                    </p>
                    <h3 className="font-heading text-lg font-bold text-slate-900 mb-1 line-clamp-2">
                      {product.product_name}
                    </h3>
                    {product.brand && (
                      <p className="text-sm text-slate-500 mb-3">{product.brand}</p>
                    )}
                    <div className="pt-3 border-t border-slate-100">
                      <Link to="/contact">
                        <Button 
                          data-testid={`contact-availability-${product.sku}`}
                          className="w-full btn-secondary text-sm"
                        >
                          <Phone className="w-4 h-4 mr-2" />
                          Contact for Availability
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Contact CTA */}
      <div className="bg-industrial-blue text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-heading text-2xl lg:text-3xl font-bold mb-4">
            Can't find what you're looking for?
          </h2>
          <p className="text-slate-300 mb-6 max-w-2xl mx-auto">
            Contact us directly and our team will help you find the right products for your needs.
          </p>
          <Link to="/contact">
            <Button className="btn-action">
              Contact Us <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-industrial-orange rounded-sm flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading font-bold">SELLANDIAMMAN TRADERS</span>
            </div>
            <p className="text-slate-400 text-sm">
              © {new Date().getFullYear()} Sellandiamman Traders. All rights reserved.
            </p>
          </div>
        </div>
      </footer>

      {/* WhatsApp Floating Button */}
      <WhatsAppButton />
    </div>
  );
};

export default CataloguePage;
