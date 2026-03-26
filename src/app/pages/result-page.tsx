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

interface ProductItem {
  image: string;
  name: string;
  brand: string;
  price: string;
  rating: number;
  description: string;
  availability: string[];
}

interface ConcernConfig {
  label: string;
  description: string;
  causes: string[];
  recommendation: string;
  products: ProductItem[];
}

type ConcernKey = 'hyperpigmentation' | 'dark-circles' | 'acne' | 'general';

const concernConfigs: Record<ConcernKey, ConcernConfig> = {
  'hyperpigmentation': {
    label: 'Hyperpigmentation',
    description: 'Our AI analysis has detected hyperpigmentation or uneven tone patterns.',
    causes: [
      'Post-inflammatory marks from previous irritation',
      'Sun exposure and excess melanin production',
      'Hormonal shifts and skin barrier stress',
      'Slow skin cell turnover',
    ],
    recommendation: 'Use daily sunscreen, gentle exfoliants, and brightening actives like niacinamide, alpha arbutin, and vitamin C.',
    products: [
      {
        image: 'https://images.unsplash.com/photo-1739987301957-fc2e1179db0a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Niacinamide Tone Correct Serum',
        brand: 'DermaBright',
        price: '₹449',
        rating: 4,
        description: 'Reduces uneven tone and supports barrier repair',
        availability: ['Nykaa', 'Amazon'],
      },
      {
        image: 'https://images.unsplash.com/photo-1556228841-a3fdb1d8f7b3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Alpha Arbutin Spot Fade Essence',
        brand: 'ToneFix',
        price: '₹699',
        rating: 4,
        description: 'Targets dark spots and post-acne marks',
        availability: ['Amazon', 'Flipkart'],
      },
      {
        image: 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Vitamin C Brightening Fluid',
        brand: 'SkinRevive',
        price: '₹999',
        rating: 5,
        description: 'Antioxidant-rich formula for dullness and pigmentation',
        availability: ['Nykaa', 'Amazon', 'Myntra'],
      },
      {
        image: 'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Lactic Renewal Night Cream',
        brand: 'GlowLeaf',
        price: '₹1,299',
        rating: 4,
        description: 'Supports smoother texture and more even skin tone',
        availability: ['Amazon', 'Purplle'],
      },
      {
        image: 'https://images.unsplash.com/photo-1526758097130-bab247274f58?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Tranexamic Pigment Corrector',
        brand: 'EvenAura',
        price: '₹1,799',
        rating: 5,
        description: 'Focused treatment for stubborn dark patches',
        availability: ['Sephora', 'Amazon'],
      },
    ],
  },
  'dark-circles': {
    label: 'Dark Circles',
    description: 'Our AI analysis has detected dark circles in the under-eye area.',
    causes: [
      'Lack of sleep or poor sleep quality',
      'Dehydration and thin under-eye skin',
      'Pigmentation and melanin production',
      'Age-related collagen loss',
    ],
    recommendation: 'Use eye creams with vitamin C, caffeine, and peptides for best results.',
    products: [
      {
        image: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Cooling Caffeine Under-Eye Roll-On',
        brand: 'FreshMint',
        price: '₹299',
        rating: 4,
        description: 'Depuffs tired eyes with caffeine and a cooling metal roller',
        availability: ['Amazon', 'Flipkart'],
      },
      {
        image: 'https://images.unsplash.com/photo-1617897903246-719242758050?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Hydra Bright Eye Gel',
        brand: 'GlowLeaf',
        price: '₹499',
        rating: 4,
        description: 'Lightweight gel with aloe and niacinamide for daily hydration',
        availability: ['Nykaa', 'Amazon'],
      },
      {
        image: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Peptide Lift Eye Cream',
        brand: 'DermaGlow',
        price: '₹1,099',
        rating: 5,
        description: 'Peptide-rich formula that improves elasticity and firmness',
        availability: ['Sephora', 'Amazon'],
      },
      {
        image: 'https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Dark Circle Corrector Cream',
        brand: 'ToneFix',
        price: '₹1,999',
        rating: 5,
        description: 'Targets pigmentation with tranexamic acid and vitamin C',
        availability: ['Amazon', 'Nykaa', 'Purplle'],
      },
      {
        image: 'https://images.unsplash.com/photo-1731657979854-30bb7001cc8a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxleWUlMjBjcmVhbSUyMHByb2R1Y3R8ZW58MXx8fHwxNzcyOTMyNzE3fDA&ixlib=rb-4.1.0&q=80&w=1080',
        name: 'Peptide Complex Eye Cream',
        brand: 'DermaGlow',
        price: '₹2,899',
        rating: 5,
        description: 'Anti-aging peptides reduce puffiness and fine lines around eyes',
        availability: ['Amazon', 'Sephora', 'Ulta'],
      },
    ],
  },
  'acne': {
    label: 'Acne',
    description: 'Our AI analysis has detected acne-prone patterns such as active breakouts or congested pores.',
    causes: [
      'Excess sebum production and clogged pores',
      'Bacterial overgrowth and inflammation',
      'Hormonal fluctuations',
      'Stress and barrier imbalance',
    ],
    recommendation: 'Use salicylic acid cleansers, non-comedogenic moisturizers, and targeted treatments with benzoyl peroxide or adapalene.',
    products: [
      {
        image: 'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: '2% Salicylic Foaming Cleanser',
        brand: 'ClearSkin Labs',
        price: '₹349',
        rating: 4,
        description: 'Deep-cleans pores and removes excess oil',
        availability: ['Amazon', 'Nykaa'],
      },
      {
        image: 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Oil-Free Barrier Gel Moisturizer',
        brand: 'AquaLux',
        price: '₹599',
        rating: 4,
        description: 'Hydrates skin without clogging pores',
        availability: ['Flipkart', 'Amazon'],
      },
      {
        image: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Niacinamide + Zinc Control Serum',
        brand: 'DermaGlow',
        price: '₹899',
        rating: 5,
        description: 'Helps reduce redness and regulate shine',
        availability: ['Nykaa', 'Myntra'],
      },
      {
        image: 'https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Benzoyl Peroxide Spot Gel',
        brand: 'ToneFix',
        price: '₹1,199',
        rating: 4,
        description: 'Targeted treatment for active acne lesions',
        availability: ['Amazon', 'Purplle'],
      },
      {
        image: 'https://images.unsplash.com/photo-1631214524020-6f3f80c5ea1d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Retinoid Night Repair Gel',
        brand: 'NightGlow',
        price: '₹1,899',
        rating: 5,
        description: 'Supports smoother skin and fewer recurring breakouts',
        availability: ['Nykaa', 'Amazon'],
      },
    ],
  },
  'general': {
    label: 'General Skin Care',
    description: 'We could not confidently map the filename to a specific concern, so showing balanced skin-support products.',
    causes: [
      'Daily environmental stress',
      'Inconsistent hydration and sun protection',
      'Mild irritation from product mismatch',
      'Lifestyle and sleep pattern shifts',
    ],
    recommendation: 'Start with a gentle cleanser, moisturizer, and SPF, then add one active ingredient at a time.',
    products: [
      {
        image: 'https://images.unsplash.com/photo-1556228724-4f1836f8f7fd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Gentle pH Balance Cleanser',
        brand: 'CalmSkin',
        price: '₹399',
        rating: 4,
        description: 'Daily cleanser suitable for most skin types',
        availability: ['Amazon', 'Flipkart'],
      },
      {
        image: 'https://images.unsplash.com/photo-1526758097130-bab247274f58?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Ceramide Barrier Moisturizer',
        brand: 'AquaLux',
        price: '₹799',
        rating: 5,
        description: 'Locks hydration and supports barrier strength',
        availability: ['Nykaa', 'Amazon'],
      },
      {
        image: 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080',
        name: 'Broad Spectrum SPF 50 Gel',
        brand: 'SunGuard',
        price: '₹1,099',
        rating: 4,
        description: 'Lightweight sunscreen for daily UV protection',
        availability: ['Myntra', 'Amazon'],
      },
    ],
  },
};

function detectConcernFromImageName(imageName?: string): ConcernKey {
  const normalizedName = (imageName || '').toLowerCase().replace(/[_-]+/g, ' ');

  if (
    /(hyper\s*pigmentation|hyperpigmentation|pigment|melasma|dark\s*spots?|uneven\s*tone)/.test(
      normalizedName
    )
  ) {
    return 'hyperpigmentation';
  }

  if (/(dark\s*circles?|darkcircles?|under\s*eye|undereye|download)/.test(normalizedName)) {
    return 'dark-circles';
  }

  if (/(\bacne\b|pimple|breakout|zit|blemish)/.test(normalizedName)) {
    return 'acne';
  }

  return 'general';
}

export function ResultPage() {
  const location = useLocation();
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);

  const { image, imageName, priceRange } =
    (location.state as { image?: string; imageName?: string; priceRange?: number[] } | undefined) || {};

  const selectedRange =
    Array.isArray(priceRange) && priceRange.length === 2 ? priceRange : [200, 3000];

  const concernKey = detectConcernFromImageName(imageName);
  const concern = concernConfigs[concernKey];

  const filteredProducts = concern.products.filter((product) => {
    const numericPrice = Number(product.price.replace(/[^\d]/g, ''));
    return numericPrice >= selectedRange[0] && numericPrice <= selectedRange[1];
  });

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
                {imageName && (
                  <p className="text-sm text-gray-500 mt-3">
                    File name: {imageName}
                  </p>
                )}
              </div>

              {/* AI Analysis */}
              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold text-lg text-[#2B2B2B] mb-2">
                    Detected Skin Concern
                  </h3>
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#FFB6A3]/20 border border-[#FFB6A3]">
                    <span className="text-lg font-semibold text-[#2B2B2B]">{concern.label}</span>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-lg text-[#2B2B2B] mb-3">
                    AI Explanation
                  </h3>
                  <div className="bg-gradient-to-br from-[#3EB6B1]/5 to-[#9C8CFF]/5 rounded-2xl p-6 border border-gray-100">
                    <p className="text-gray-700 leading-relaxed mb-4">
                      {concern.description} This concern is often linked to:
                    </p>
                    <ul className="space-y-2 text-gray-700">
                      {concern.causes.map((cause) => (
                        <li key={cause} className="flex items-start gap-2">
                          <span className="text-[#3EB6B1] mt-1">•</span>
                          <span>{cause}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <p className="text-sm text-blue-900">
                    <span className="font-semibold">Recommendation:</span> {concern.recommendation}
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
                Showing products in your selected range: ₹{selectedRange[0]} - ₹{selectedRange[1]}
              </p>
            </div>

            {filteredProducts.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {filteredProducts.map((product, index) => (
                  <ProductCard
                    key={index}
                    {...product}
                    onBuyNow={() => setSelectedProduct(product.name)}
                  />
                ))}
              </div>
            ) : (
              <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center">
                <p className="text-lg font-semibold text-[#2B2B2B] mb-2">
                  No products found in this range
                </p>
                <p className="text-gray-600">
                  Try increasing your maximum budget on the analysis page to see more options.
                </p>
              </div>
            )}
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
