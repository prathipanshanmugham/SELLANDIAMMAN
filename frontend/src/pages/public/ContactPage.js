import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Zap, MapPin, Phone, Clock, Mail, ArrowRight } from 'lucide-react';
import WhatsAppButton from '../../components/WhatsAppButton';

const ContactPage = () => {
  return (
    <div className="min-h-screen bg-slate-50">
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
              <Link to="/catalogue" className="text-slate-300 hover:text-white transition-colors">Catalogue</Link>
              <Link to="/contact" className="text-white font-medium hover:text-industrial-orange transition-colors">Contact</Link>
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
            Contact Us
          </h1>
          <p className="mt-2 text-slate-600">
            Get in touch with us for all your electrical needs
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Info */}
          <div>
            <h2 className="font-heading text-2xl font-bold text-slate-900 mb-6">
              Visit Our Store
            </h2>
            
            <div className="space-y-6">
              <div className="card-industrial p-6 flex gap-4">
                <div className="w-12 h-12 bg-industrial-orange/10 rounded-sm flex items-center justify-center flex-shrink-0">
                  <MapPin className="w-6 h-6 text-industrial-orange" />
                </div>
                <div>
                  <h3 className="font-heading font-bold text-slate-900 mb-1">Address</h3>
                  <p className="text-slate-600">
                    199, Kunnathur Rd - Perundurai<br />
                    Erode, Perundurai<br />
                    Tamil Nadu 638052
                  </p>
                </div>
              </div>
              
              <div className="card-industrial p-6 flex gap-4">
                <div className="w-12 h-12 bg-industrial-blue/10 rounded-sm flex items-center justify-center flex-shrink-0">
                  <Phone className="w-6 h-6 text-industrial-blue" />
                </div>
                <div>
                  <h3 className="font-heading font-bold text-slate-900 mb-1">Phone</h3>
                  <p className="text-slate-600">
                    <a href="tel:9698786056" className="hover:text-industrial-blue transition-colors">
                      96987 86056
                    </a>
                  </p>
                  <p className="text-slate-600">
                    <a href="tel:9842823300" className="hover:text-industrial-blue transition-colors">
                      9842823300
                    </a>
                  </p>
                </div>
              </div>
              
              <div className="card-industrial p-6 flex gap-4">
                <div className="w-12 h-12 bg-green-100 rounded-sm flex items-center justify-center flex-shrink-0">
                  <Clock className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="font-heading font-bold text-slate-900 mb-1">Business Hours</h3>
                  <p className="text-slate-600">
                    Monday - Saturday<br />
                    9:00 AM - 8:00 PM
                  </p>
                  <p className="text-slate-500 text-sm mt-1">Sunday: Closed</p>
                </div>
              </div>
            </div>

            {/* Quick Links */}
            <div className="mt-8">
              <h3 className="font-heading font-bold text-slate-900 mb-4">Quick Links</h3>
              <div className="flex gap-4">
                <a 
                  href="tel:9698786056"
                  className="flex-1"
                >
                  <Button data-testid="call-now-btn" className="w-full btn-action">
                    <Phone className="w-4 h-4 mr-2" />
                    Call Now
                  </Button>
                </a>
                <Link to="/catalogue" className="flex-1">
                  <Button data-testid="browse-products-btn" className="w-full btn-primary">
                    Browse Products
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          {/* Map */}
          <div>
            <h2 className="font-heading text-2xl font-bold text-slate-900 mb-6">
              Find Us
            </h2>
            <div className="card-industrial overflow-hidden">
              <iframe
                title="Store Location"
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3914.6095!2d77.5796709!3d11.2798728!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3ba96d4149029327%3A0xc71a50067b55a08d!2sSellandiamman%20Traders!5e0!3m2!1sen!2sin!4v1234567890"
                width="100%"
                height="400"
                style={{ border: 0 }}
                allowFullScreen=""
                loading="lazy"
              />
            </div>
            
            <div className="mt-6 p-4 bg-industrial-blue/5 border border-industrial-blue/20 rounded-sm">
              <p className="text-sm text-slate-700">
                <strong>Landmark:</strong> Located on Kunnathur Road, easily accessible from Perundurai main junction. 
                Look for the Sellandiamman Traders signboard.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-industrial-blue text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-heading text-2xl lg:text-3xl font-bold mb-4">
            Ready to Order?
          </h2>
          <p className="text-slate-300 mb-6 max-w-2xl mx-auto">
            Visit our store or call us now. We offer wholesale and retail pricing with the best service in Perundurai.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <a href="tel:9698786056">
              <Button className="btn-action">
                <Phone className="w-4 h-4 mr-2" />
                Call: 96987 86056
              </Button>
            </a>
            <Link to="/catalogue">
              <Button className="bg-white text-industrial-blue hover:bg-slate-100">
                View Catalogue
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
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

export default ContactPage;
