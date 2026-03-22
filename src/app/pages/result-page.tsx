import { useState } from 'react';
import { useLocation, Link } from 'react-router';
import { Navbar } from '../components/navbar';
import { Footer } from '../components/footer';
import { ProductCard } from '../components/product-card';
import { Button } from '../components/button';
import { Sparkles, CheckCircle, X, MapPin, CreditCard, Smartphone } from 'lucide-react';

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  productName: string;
}

function CheckoutModal({ isOpen, onClose, productName }: CheckoutModalProps) {
  const [paymentMethod, setPaymentMethod] = useState('');
  const [orderPlaced, setOrderPlaced] = useState(false);

  if (!isOpen) return null;

  const handlePlaceOrder = () => {
    if (paymentMethod === 'cod') {
      setOrderPlaced(true);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 relative">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        {orderPlaced ? (
          <div className="text-center py-8">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-12 h-12 text-green-500" />
            </div>
            <h3 className="text-2xl font-bold text-[#2B2B2B] mb-3">
              Order Placed Successfully!
            </h3>
            <p className="text-gray-600 mb-6">
              Your order for {productName} has been confirmed.
            </p>
            <Button onClick={onClose} className="w-full">
              Continue Shopping
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-[#2B2B2B]">Checkout</h3>
            
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-[#2B2B2B]">
                Delivery Address
              </label>
              <div className="p-4 rounded-xl border border-gray-200 bg-gray-50">
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-[#3EB6B1] mt-0.5" />
                  <div>
                    <p className="font-medium text-[#2B2B2B]">Home</p>
                    <p className="text-sm text-gray-600">
                      123 Main Street, Apt 4B<br />
                      New York, NY 10001
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-semibold text-[#2B2B2B]">
                Payment Method
              </label>
              <div className="space-y-2">
                <label className="flex items-center gap-3 p-4 rounded-xl border-2 border-gray-200 cursor-pointer hover:border-[#3EB6B1] transition-colors">
                  <input
                    type="radio"
                    name="payment"
                    value="cod"
                    checked={paymentMethod === 'cod'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-4 h-4 text-[#3EB6B1] focus:ring-[#3EB6B1]"
                  />
                  <Sparkles className="w-5 h-5 text-gray-600" />
                  <span className="font-medium text-[#2B2B2B]">Cash on Delivery</span>
                </label>

                <label className="flex items-center gap-3 p-4 rounded-xl border-2 border-gray-200 cursor-pointer hover:border-[#3EB6B1] transition-colors">
                  <input
                    type="radio"
                    name="payment"
                    value="card"
                    checked={paymentMethod === 'card'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-4 h-4 text-[#3EB6B1] focus:ring-[#3EB6B1]"
                  />
                  <CreditCard className="w-5 h-5 text-gray-600" />
                  <span className="font-medium text-[#2B2B2B]">Credit/Debit Card</span>
                </label>

                <label className="flex items-center gap-3 p-4 rounded-xl border-2 border-gray-200 cursor-pointer hover:border-[#3EB6B1] transition-colors">
                  <input
                    type="radio"
                    name="payment"
                    value="upi"
                    checked={paymentMethod === 'upi'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-4 h-4 text-[#3EB6B1] focus:ring-[#3EB6B1]"
                  />
                  <Smartphone className="w-5 h-5 text-gray-600" />
                  <span className="font-medium text-[#2B2B2B]">UPI</span>
                </label>
              </div>
            </div>

            <Button
              onClick={handlePlaceOrder}
              disabled={!paymentMethod}
              className="w-full"
              size="lg"
            >
              {paymentMethod === 'cod' ? 'Place Order' : 'Proceed to Payment'}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

export function ResultPage() {
  const location = useLocation();
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);

  const { image } = location.state || {};

  const mockProducts = [
    {
      image: 'https://images.unsplash.com/photo-1643379850623-7eb6442cd262?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzZXJ1bSUyMGJvdHRsZSUyMHNraW5jYXJlfGVufDF8fHx8MTc3Mjk5NDgwMHww&ixlib=rb-4.1.0&q=80&w=1080',
      name: 'Advanced Vitamin C Eye Serum',
      brand: 'SkinRevive',
      price: '₹2,899',
      rating: 5,
      description: 'Reduces dark circles and brightens under-eye area with 15% Vitamin C',
      availability: ['Amazon', 'Nykaa', 'Flipkart'],
    },
    {
      image: 'https://images.unsplash.com/photo-1731657979854-30bb7001cc8a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxleWUlMjBjcmVhbSUyMHByb2R1Y3R8ZW58MXx8fHwxNzcyOTMyNzE3fDA&ixlib=rb-4.1.0&q=80&w=1080',
      name: 'Peptide Complex Eye Cream',
      brand: 'DermaGlow',
      price: '₹3,499',
      rating: 5,
      description: 'Anti-aging peptides reduce puffiness and fine lines around eyes',
      availability: ['Amazon', 'Sephora', 'Ulta'],
    },
    {
      image: 'https://images.unsplash.com/photo-1634449277883-534da4f7c97a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjcmVhbSUyMGphciUyMGNvc21ldGljfGVufDF8fHx8MTc3Mjk5NDgwMHww&ixlib=rb-4.1.0&q=80&w=1080',
      name: 'Hydrating Eye Treatment Gel',
      brand: 'AquaLux',
      price: '₹2,399',
      rating: 4,
      description: 'Cooling gel formula with hyaluronic acid for instant hydration',
      availability: ['Amazon', 'Nykaa'],
    },
    {
      image: 'https://images.unsplash.com/photo-1583334516865-e4240dc3fc79?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2lzdHVyaXplciUyMGJvdHRsZSUyMGJlYXV0eXxlbnwxfHx8fDE3NzI5OTQ4MDF8MA&ixlib=rb-4.1.0&q=80&w=1080',
      name: 'Retinol Eye Recovery Night Cream',
      brand: 'NightGlow',
      price: '₹3,299',
      rating: 5,
      description: 'Overnight treatment with retinol to diminish dark circles',
      availability: ['Flipkart', 'Nykaa', 'Amazon'],
    },
  ];

  if (!image) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <Navbar />
        <div className="text-center">
          <p className="text-lg text-gray-600 mb-4">No analysis data found</p>
          <Link to="/analyze">
            <Button>Go to Analysis Page</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <div className="flex-1 bg-gradient-to-br from-[#F8FAFB] to-[#3EB6B1]/5 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 border border-green-200 mb-4">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">Analysis Complete</span>
            </div>
            <h1 className="text-4xl font-bold text-[#2B2B2B] mb-4">
              Your Skin Analysis Results
            </h1>
          </div>

          {/* Analysis Result Card */}
          <div className="bg-white rounded-3xl shadow-xl p-8 md:p-10 mb-12">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              {/* Uploaded Image */}
              <div>
                <h3 className="font-semibold text-lg text-[#2B2B2B] mb-4">
                  Uploaded Image
                </h3>
                <div className="rounded-2xl overflow-hidden shadow-lg">
                  <img
                    src={image}
                    alt="Uploaded skin"
                    className="w-full h-auto"
                  />
                </div>
              </div>

              {/* AI Analysis */}
              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold text-lg text-[#2B2B2B] mb-2">
                    Detected Skin Concern
                  </h3>
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#FFB6A3]/20 border border-[#FFB6A3]">
                    <span className="text-lg font-semibold text-[#2B2B2B]">Dark Circles</span>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-lg text-[#2B2B2B] mb-3">
                    AI Explanation
                  </h3>
                  <div className="bg-gradient-to-br from-[#3EB6B1]/5 to-[#9C8CFF]/5 rounded-2xl p-6 border border-gray-100">
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Our AI analysis has detected <span className="font-semibold text-[#3EB6B1]">dark circles</span> in the under-eye area. This common concern is often caused by:
                    </p>
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-start gap-2">
                        <span className="text-[#3EB6B1] mt-1">•</span>
                        <span>Lack of sleep or poor sleep quality</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-[#3EB6B1] mt-1">•</span>
                        <span>Dehydration and thin under-eye skin</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-[#3EB6B1] mt-1">•</span>
                        <span>Pigmentation and melanin production</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-[#3EB6B1] mt-1">•</span>
                        <span>Age-related collagen loss</span>
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <p className="text-sm text-blue-900">
                    <span className="font-semibold">Recommendation:</span> Use eye creams with Vitamin C, caffeine, and peptides for best results.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6 mb-8">
            <h4 className="font-semibold text-[#2B2B2B] mb-2 flex items-center gap-2">
              <span className="text-yellow-600">⚠️</span>
              Important Disclaimer
            </h4>
            <p className="text-sm text-gray-700 leading-relaxed">
              SkinIntel provides AI-based skincare awareness and product suitability guidance for informational and academic purposes only. It does not offer medical diagnosis or replace professional dermatological advice. For serious or persistent skin concerns, please consult a licensed dermatologist.
            </p>
          </div>

          {/* Product Recommendations */}
          <div className="mb-12">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-[#2B2B2B] mb-3">
                Recommended Products
              </h2>
              <p className="text-lg text-gray-600">
                Personalized product suggestions for your skin concern
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {mockProducts.map((product, index) => (
                <ProductCard
                  key={index}
                  {...product}
                  onBuyNow={() => setSelectedProduct(product.name)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      <Footer />

      {selectedProduct && (
        <CheckoutModal
          isOpen={!!selectedProduct}
          onClose={() => setSelectedProduct(null)}
          productName={selectedProduct}
        />
      )}
    </div>
  );
}
