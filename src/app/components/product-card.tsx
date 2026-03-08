import { Star, ShoppingCart } from 'lucide-react';
import { Button } from './button';

interface ProductCardProps {
  image: string;
  name: string;
  brand: string;
  price: string;
  rating: number;
  description: string;
  availability: string[];
  onBuyNow: () => void;
}

export function ProductCard({
  image,
  name,
  brand,
  price,
  rating,
  description,
  availability,
  onBuyNow,
}: ProductCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100">
      {/* Product Image */}
      <div className="aspect-square bg-gray-50 flex items-center justify-center p-6">
        <img
          src={image}
          alt={name}
          className="w-full h-full object-contain"
        />
      </div>

      {/* Product Info */}
      <div className="p-6">
        <div className="mb-3">
          <p className="text-xs text-[#9C8CFF] font-semibold uppercase tracking-wider mb-1">
            {brand}
          </p>
          <h3 className="font-semibold text-lg text-[#2B2B2B] line-clamp-2">
            {name}
          </h3>
        </div>

        {/* Rating */}
        <div className="flex items-center gap-1 mb-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Star
              key={i}
              className={`w-4 h-4 ${
                i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
              }`}
            />
          ))}
          <span className="text-sm text-gray-600 ml-1">({rating}.0)</span>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 line-clamp-2 mb-4">
          {description}
        </p>

        {/* Price */}
        <div className="mb-4">
          <span className="text-2xl font-bold text-[#3EB6B1]">{price}</span>
        </div>

        {/* Buy Button */}
        <Button onClick={onBuyNow} className="w-full" size="md">
          <ShoppingCart className="w-4 h-4" />
          Buy Now
        </Button>

        {/* Availability */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-xs text-gray-500 mb-2">Available on:</p>
          <div className="flex flex-wrap gap-2">
            {availability.map((store) => (
              <a
                key={store}
                href="#"
                className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-700 hover:bg-[#3EB6B1] hover:text-white transition-colors"
              >
                {store}
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
