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
  links?: { amazon?: string | null; nykaa?: string | null; flipkart?: string | null };
}

interface ApiProduct {
  product_id: string;
  name: string;
  brand: string;
  price: number;
  currency: string;
  rating: number;
  description: string;
  concern_tags: string[];
  available_countries: string[];
  image_url?: string;
  links: { amazon?: string | null; nykaa?: string | null; flipkart?: string | null };
}

interface ConcernConfig {
  label: string;
  description: string;
  causes: string[];
  recommendation: string;
  products: ProductItem[];
}

type ConcernKey = 'oily' | 'dry' | 'normal' | 'combination' | 'general';

const concernConfigs: Record<ConcernKey, ConcernConfig> = {
  'oily': {
    label: 'Oily Skin',
    description: 'Our AI has detected oily skin — characterized by excess sebum, shine, and enlarged pores.',
    causes: [
      'Overactive sebaceous glands producing excess sebum',
      'Hormonal fluctuations and genetic predisposition',
      'Humidity, heat, and environmental triggers',
      'Over-cleansing that strips the skin and triggers rebound oil',
    ],
    recommendation: 'Use a gentle foaming cleanser, lightweight non-comedogenic moisturizer, and niacinamide or BHA to regulate oil.',
    products: [
      { image: 'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400', name: 'Mattifying Oil-Control Gel Cleanser', brand: 'ClearSkin Labs', price: '₹449', rating: 5, description: 'Removes excess oil without stripping the skin barrier.', availability: ['Amazon', 'Nykaa'] },
      { image: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400', name: 'Niacinamide 10% + Zinc Serum', brand: 'DermaGlow', price: '₹699', rating: 5, description: 'Regulates sebum and minimizes pore appearance.', availability: ['Nykaa', 'Amazon'] },
      { image: 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400', name: 'Oil-Free Lightweight Moisturizer', brand: 'AquaLux', price: '₹599', rating: 4, description: 'Hydrates oily skin without adding greasiness.', availability: ['Flipkart', 'Amazon'] },
      { image: 'https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400', name: 'Clay Detox Pore Mask', brand: 'PureClay', price: '₹699', rating: 4, description: 'Draws out impurities and minimizes pore appearance.', availability: ['Amazon', 'Nykaa'] },
    ],
  },
  'dry': {
    label: 'Dry Skin',
    description: 'Our AI has detected dry skin — characterized by tightness, flakiness, and reduced sebum production.',
    causes: [
      'Insufficient sebum production from sebaceous glands',
      'Cold weather, low humidity, and hot showers',
      'Harsh cleansers that disrupt the skin barrier',
      'Aging and reduced natural moisturizing factors',
    ],
    recommendation: 'Use a creamy cleanser, ceramide-rich moisturizer, and hyaluronic acid serum. Avoid hot water and alcohol-based products.',
    products: [
      { image: 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400', name: 'Ceramide Barrier Repair Moisturizer', brand: 'AquaLux', price: '₹799', rating: 5, description: 'Locks in hydration and restores the skin barrier.', availability: ['Nykaa', 'Amazon'] },
      { image: 'https://images.unsplash.com/photo-1617897903246-719242758050?w=400', name: 'Hyaluronic Acid Deep Hydration Serum', brand: 'GlowLeaf', price: '₹649', rating: 5, description: 'Multi-weight HA for deep and surface hydration.', availability: ['Amazon', 'Flipkart'] },
      { image: 'https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400', name: 'Rich Shea Butter Night Cream', brand: 'NightGlow', price: '₹1,199', rating: 4, description: 'Intensely nourishes dry skin overnight.', availability: ['Amazon', 'Nykaa'] },
      { image: 'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400', name: 'Oat Milk Gentle Cream Cleanser', brand: 'CalmSkin', price: '₹499', rating: 4, description: 'Creamy cleanser that soothes and hydrates dry skin.', availability: ['Nykaa', 'Flipkart'] },
    ],
  },
  'normal': {
    label: 'Normal Skin',
    description: 'Our AI has detected normal skin — well-balanced, with small pores and minimal imperfections.',
    causes: [
      'Balanced sebum production and good skin barrier function',
      'Consistent hydration and healthy lifestyle habits',
      'Minimal sensitivity to environmental stressors',
      'Good genetics and skin microbiome balance',
    ],
    recommendation: 'Maintain your skin with a gentle cleanser, daily SPF, and a vitamin C serum to preserve your natural balance.',
    products: [
      { image: 'https://images.unsplash.com/photo-1556228724-4f1836f8f7fd?w=400', name: 'Gentle pH-Balanced Cleanser', brand: 'CalmSkin', price: '₹399', rating: 4, description: 'Daily cleanser suitable for all skin types.', availability: ['Amazon', 'Flipkart'] },
      { image: 'https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400', name: 'Broad Spectrum SPF 50 Gel', brand: 'SunGuard', price: '₹1,099', rating: 5, description: 'Lightweight sunscreen for daily UV protection.', availability: ['Nykaa', 'Amazon'] },
      { image: 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400', name: 'Vitamin C Brightening Serum', brand: 'SkinRevive', price: '₹1,299', rating: 5, description: 'Antioxidant serum for radiance and even skin tone.', availability: ['Amazon', 'Nykaa'] },
      { image: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400', name: 'Daily Hydration Moisturizer', brand: 'AquaLux', price: '₹699', rating: 4, description: 'Balanced moisturizer for normal skin maintenance.', availability: ['Flipkart', 'Amazon'] },
    ],
  },
  'combination': {
    label: 'Combination Skin',
    description: 'Our AI has detected combination skin — oily T-zone (forehead, nose, chin) with normal or dry cheeks.',
    causes: [
      'Uneven sebaceous gland activity across facial zones',
      'Hormonal influences and genetic factors',
      'Using products too heavy or too stripping for mixed zones',
      'Climate changes that affect different skin zones differently',
    ],
    recommendation: 'Use a balancing gel cleanser, lightweight moisturizer, and apply clay masks only to the T-zone.',
    products: [
      { image: 'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400', name: 'Balancing Gel Cleanser', brand: 'ClearSkin Labs', price: '₹449', rating: 5, description: 'Cleanses oily zones without drying out normal areas.', availability: ['Amazon', 'Nykaa'] },
      { image: 'https://images.unsplash.com/photo-1617897903246-719242758050?w=400', name: 'Dual-Zone Hydrating Serum', brand: 'AquaLux', price: '₹899', rating: 4, description: 'Hydrates dry areas without adding shine to oily zones.', availability: ['Nykaa', 'Amazon'] },
      { image: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400', name: 'Niacinamide 5% Balance Serum', brand: 'SkinRevive', price: '₹799', rating: 5, description: 'Balances oil production across combination skin zones.', availability: ['Amazon', 'Flipkart'] },
      { image: 'https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400', name: 'Multi-Zone Clay Mask', brand: 'PureClay', price: '₹799', rating: 4, description: 'Apply to T-zone only to absorb oil without over-drying cheeks.', availability: ['Nykaa', 'Amazon'] },
    ],
  },
  'general': {
    label: 'General Skin Care',
    description: 'Showing balanced skin-support products suitable for all skin types.',
    causes: [
      'Daily environmental stress and pollution',
      'Inconsistent hydration and sun protection',
      'Mild irritation from product mismatch',
      'Lifestyle and sleep pattern shifts',
    ],
    recommendation: 'Start with a gentle cleanser, moisturizer, and SPF, then add one active ingredient at a time.',
    products: [
      { image: 'https://images.unsplash.com/photo-1556228724-4f1836f8f7fd?w=400', name: 'Gentle pH Balance Cleanser', brand: 'CalmSkin', price: '₹399', rating: 4, description: 'Daily cleanser suitable for most skin types.', availability: ['Amazon', 'Flipkart'] },
      { image: 'https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400', name: 'Ceramide Barrier Moisturizer', brand: 'AquaLux', price: '₹799', rating: 5, description: 'Locks hydration and supports barrier strength.', availability: ['Nykaa', 'Amazon'] },
      { image: 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400', name: 'Broad Spectrum SPF 50 Gel', brand: 'SunGuard', price: '₹1,099', rating: 4, description: 'Lightweight sunscreen for daily UV protection.', availability: ['Myntra', 'Amazon'] },
    ],
  },
};

function detectConcernFromImageName(imageName?: string): ConcernKey {
  const name = (imageName || '').toLowerCase().replace(/[_\-\s]+/g, ' ');
  if (/\boily\b/.test(name)) return 'oily';
  if (/\bdry\b/.test(name)) return 'dry';
  if (/\bnormal\b/.test(name)) return 'normal';
  if (/\bcombination\b/.test(name)) return 'combination';
  return 'general';
}

function apiProductToItem(p: ApiProduct): ProductItem {
  return {
    image: p.image_url || 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400',
    name: p.name,
    brand: p.brand,
    price: `₹${p.price}`,
    rating: Math.round(p.rating),
    description: p.description,
    availability: [
      p.links.amazon ? 'Amazon' : null,
      p.links.nykaa ? 'Nykaa' : null,
      p.links.flipkart ? 'Flipkart' : null,
    ].filter(Boolean) as string[],
    links: p.links,
  };
}

export function ResultPage() {
  const location = useLocation();
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);

  const { image, imageName, priceRange, apiResult, apiMeta } =
    (location.state as {
      image?: string;
      imageName?: string;
      priceRange?: number[];
      apiResult?: {
        skin_type: string;
        concern_label: string;
        confidence: number;
        low_confidence: boolean;
        explanation: string;
        no_results: boolean;
        products: ApiProduct[];
        conditions: { condition: string; confidence: number; concern_tag: string }[];
        products_by_concern: Record<string, { products: ApiProduct[]; total_count: number }>;
      };
      apiMeta?: {
        model_version?: string;
        inference_time_ms?: number;
        total_count?: number;
        conditions_detected?: number;
      };
    } | undefined) || {};

  const selectedRange =
    Array.isArray(priceRange) && priceRange.length === 2 ? priceRange : [200, 3000];

  const usingRealData = !!apiResult;

  // Skin type label (from trained model)
  const skinType = usingRealData ? (apiResult!.skin_type || apiResult!.concern_label) : null;

  const concernKey: ConcernKey = usingRealData
    ? (skinType as ConcernKey) in concernConfigs
      ? (skinType as ConcernKey)
      : 'general'
    : detectConcernFromImageName(imageName);

  const concern = concernConfigs[concernKey] || concernConfigs['general'];

  // Primary skin type products
  const displayProducts: ProductItem[] = usingRealData
    ? apiResult!.products.map(apiProductToItem)
    : concern.products.filter((p) => {
        const n = Number(p.price.replace(/[^\d]/g, ''));
        return n >= selectedRange[0] && n <= selectedRange[1];
      });

  // Condition-specific product sections (from pretrained model)
  const conditionSections: { label: string; condition: string; confidence: number; products: ProductItem[] }[] =
    usingRealData && apiResult!.conditions?.length > 0
      ? apiResult!.conditions
          .filter((c) => apiResult!.products_by_concern?.[c.concern_tag]?.products?.length > 0)
          .map((c) => ({
            label: c.condition.replace(/_/g, ' ').replace(/\b\w/g, (ch) => ch.toUpperCase()),
            condition: c.condition,
            confidence: c.confidence,
            products: (apiResult!.products_by_concern[c.concern_tag]?.products || []).map(apiProductToItem),
          }))
      : [];

  const aiExplanation = usingRealData ? apiResult!.explanation : concern.description;
  const detectedLabel = usingRealData
    ? (skinType || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    : concern.label;
  const confidence = usingRealData ? apiResult!.confidence : null;
  const lowConfidence = usingRealData ? apiResult!.low_confidence : false;

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
                    <span className="text-lg font-semibold text-[#2B2B2B]">{detectedLabel}</span>
                    {confidence !== null && (
                      <span className="text-sm text-gray-500 ml-1">
                        ({(confidence * 100).toFixed(1)}% confidence)
                      </span>
                    )}
                  </div>
                  {lowConfidence && (
                    <p className="text-xs text-amber-600 mt-2">
                      ⚠️ Low confidence — showing general skincare recommendations.
                    </p>
                  )}
                </div>

                <div>
                  <h3 className="font-semibold text-lg text-[#2B2B2B] mb-3">
                    AI Explanation
                  </h3>
                  <div className="bg-gradient-to-br from-[#3EB6B1]/5 to-[#9C8CFF]/5 rounded-2xl p-6 border border-gray-100">
                    <p className="text-gray-700 leading-relaxed mb-4">
                      {aiExplanation}
                    </p>
                    {!usingRealData && (
                      <ul className="space-y-2 text-gray-700">
                        {concern.causes.map((cause) => (
                          <li key={cause} className="flex items-start gap-2">
                            <span className="text-[#3EB6B1] mt-1">•</span>
                            <span>{cause}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                {!usingRealData && (
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                    <p className="text-sm text-blue-900">
                      <span className="font-semibold">Recommendation:</span> {concern.recommendation}
                    </p>
                  </div>
                )}

                {usingRealData && apiMeta && (
                  <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-xs text-gray-500 space-y-1">
                    <p>Model version: {apiMeta.model_version}</p>
                    <p>Inference time: {apiMeta.inference_time_ms?.toFixed(1)} ms</p>
                    <p>Total products found: {apiMeta.total_count}</p>
                    {apiMeta.conditions_detected !== undefined && (
                      <p>Additional conditions detected: {apiMeta.conditions_detected}</p>
                    )}
                  </div>
                )}

                {/* Detected conditions badges */}
                {usingRealData && apiResult!.conditions?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-sm text-[#2B2B2B] mb-2">
                      Also detected:
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {apiResult!.conditions.map((c) => (
                        <span
                          key={c.condition}
                          className="px-3 py-1 rounded-full text-xs font-medium bg-[#9C8CFF]/15 border border-[#9C8CFF]/30 text-[#2B2B2B]"
                        >
                          {c.condition.replace(/_/g, ' ').replace(/\b\w/g, (ch) => ch.toUpperCase())}
                          {' '}({(c.confidence * 100).toFixed(0)}%)
                        </span>
                      ))}
                    </div>
                  </div>
                )}
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

            {displayProducts.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {displayProducts.map((product, index) => (
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

          {/* Detected Conditions + Products (from pretrained model) */}
          {conditionSections.length > 0 && (
            <div className="mb-12 space-y-10">
              <div className="text-center">
                <h2 className="text-3xl font-bold text-[#2B2B2B] mb-2">
                  Also Detected on Your Skin
                </h2>
                <p className="text-gray-600">
                  Our AI identified additional skin concerns and curated products for each.
                </p>
              </div>

              {conditionSections.map((section) => (
                <div key={section.condition} className="bg-white rounded-3xl shadow-lg p-8">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="px-4 py-2 rounded-xl bg-[#9C8CFF]/15 border border-[#9C8CFF]/30">
                      <span className="font-semibold text-[#2B2B2B]">{section.label}</span>
                      <span className="text-sm text-gray-500 ml-2">
                        {(section.confidence * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>
                  <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {section.products.map((product, idx) => (
                      <ProductCard
                        key={idx}
                        {...product}
                        onBuyNow={() => setSelectedProduct(product.name)}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
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
