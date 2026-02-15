import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Zap, Package, MapPin, Phone, ArrowRight, Shield, Truck, Clock } from 'lucide-react';
import WhatsAppButton from '../../components/WhatsAppButton';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-white">
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
              <Link to="/" className="text-white font-medium hover:text-industrial-orange transition-colors">Home</Link>
              <Link to="/catalogue" className="text-slate-300 hover:text-white transition-colors">Catalogue</Link>
              <Link to="/contact" className="text-slate-300 hover:text-white transition-colors">Contact</Link>
            </div>
            
            <Link to="/login">
              <Button 
                data-testid="staff-login-btn"
                className="btn-action text-sm"
              >
                Staff Login
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative bg-slate-900 text-white overflow-hidden">
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: 'url(https://images.unsplash.com/photo-1584175053565-c757cdff0e9a?w=1920)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="max-w-2xl">
            <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6 animate-fade-in">
              Your Trusted <span className="text-industrial-orange">Electrical</span> Partner
            </h1>
            <p className="text-lg sm:text-xl text-slate-300 mb-8" style={{ animationDelay: '0.1s' }}>
              10,000+ quality electrical products for retail & wholesale. 
              Serving Perundurai and surrounding areas with excellence since establishment.
            </p>
            <div className="flex flex-wrap gap-4" style={{ animationDelay: '0.2s' }}>
              <Link to="/catalogue">
                <Button data-testid="view-catalogue-btn" className="btn-action px-6 py-3 text-base">
                  View Catalogue
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Link to="/contact">
                <Button data-testid="contact-us-btn" className="btn-secondary px-6 py-3 text-base">
                  Contact Us
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 lg:py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="font-heading text-3xl lg:text-4xl font-bold text-slate-900 tracking-tight">
              Why Choose Us
            </h2>
            <p className="mt-3 text-slate-600 max-w-2xl mx-auto">
              Quality products, competitive prices, and reliable service for all your electrical needs.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card-industrial p-6 text-center hover:shadow-md transition-shadow">
              <div className="w-14 h-14 bg-industrial-blue/10 rounded-sm flex items-center justify-center mx-auto mb-4">
                <Package className="w-7 h-7 text-industrial-blue" />
              </div>
              <h3 className="font-heading text-xl font-bold text-slate-900 mb-2">10,000+ Products</h3>
              <p className="text-slate-600">
                Extensive range of wires, cables, switches, MCBs, tools and electrical accessories.
              </p>
            </div>
            
            <div className="card-industrial p-6 text-center hover:shadow-md transition-shadow">
              <div className="w-14 h-14 bg-industrial-orange/10 rounded-sm flex items-center justify-center mx-auto mb-4">
                <Shield className="w-7 h-7 text-industrial-orange" />
              </div>
              <h3 className="font-heading text-xl font-bold text-slate-900 mb-2">Quality Assured</h3>
              <p className="text-slate-600">
                Only genuine products from trusted brands. ISI marked and quality certified items.
              </p>
            </div>
            
            <div className="card-industrial p-6 text-center hover:shadow-md transition-shadow">
              <div className="w-14 h-14 bg-green-100 rounded-sm flex items-center justify-center mx-auto mb-4">
                <Truck className="w-7 h-7 text-green-600" />
              </div>
              <h3 className="font-heading text-xl font-bold text-slate-900 mb-2">Fast Service</h3>
              <p className="text-slate-600">
                Quick billing, efficient order processing, and local delivery available.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Product Categories Preview */}
      <section className="py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-12">
            <div>
              <h2 className="font-heading text-3xl lg:text-4xl font-bold text-slate-900 tracking-tight">
                Product Categories
              </h2>
              <p className="mt-2 text-slate-600">Browse our extensive electrical inventory</p>
            </div>
            <Link to="/catalogue">
              <Button className="btn-primary hidden sm:flex">
                View All <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { name: 'Wires & Cables', img: 'https://images.unsplash.com/photo-1648020265916-7d1d3a183a4c?w=400' },
              { name: 'Power Tools', img: 'https://images.unsplash.com/photo-1606676539940-12768ce0e762?w=400' },
              { name: 'Circuit Breakers', img: 'https://images.unsplash.com/photo-1769013649427-31c0d746bd7b?w=400' },
            ].map((cat, i) => (
              <Link 
                key={i} 
                to="/catalogue" 
                className="group relative overflow-hidden rounded-sm aspect-[4/3] card-industrial"
              >
                <img 
                  src={cat.img} 
                  alt={cat.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-4">
                  <h3 className="font-heading text-xl font-bold text-white">{cat.name}</h3>
                  <p className="text-slate-300 text-sm mt-1 flex items-center gap-1 group-hover:text-industrial-orange transition-colors">
                    Browse Products <ArrowRight className="w-4 h-4" />
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Contact CTA */}
      <section className="py-16 lg:py-24 bg-industrial-blue text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="font-heading text-3xl lg:text-4xl font-bold tracking-tight mb-4">
                Visit Our Store
              </h2>
              <p className="text-slate-300 text-lg mb-6">
                Come visit us for the best deals on electrical products. 
                Our knowledgeable staff is ready to assist you.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-industrial-orange mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-medium">Address</p>
                    <p className="text-slate-300">199, Kunnathur Rd - Perundurai, Erode, Tamil Nadu 638052</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <Phone className="w-5 h-5 text-industrial-orange mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-medium">Phone</p>
                    <p className="text-slate-300">96987 86056 | 9842823300</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <Clock className="w-5 h-5 text-industrial-orange mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-medium">Business Hours</p>
                    <p className="text-slate-300">Mon - Sat: 9:00 AM - 8:00 PM</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="card-industrial p-1">
              <iframe
                title="Store Location"
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3914.6095!2d77.5796709!3d11.2798728!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3ba96d4149029327%3A0xc71a50067b55a08d!2sSellandiamman%20Traders!5e0!3m2!1sen!2sin!4v1234567890"
                width="100%"
                height="300"
                style={{ border: 0 }}
                allowFullScreen=""
                loading="lazy"
                className="rounded-sm"
              />
            </div>
          </div>
        </div>
      </section>

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

export default HomePage;
