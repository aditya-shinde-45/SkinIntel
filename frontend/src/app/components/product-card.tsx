import { Star, ExternalLink } from 'lucide-react';

interface StoreLinks {
  amazon?: string | null;
  nykaa?: string | null;
  flipkart?: string | null;
  product_url?: string | null;
}

interface ProductCardProps {
  image: string;
  name: string;
  brand: string;
  price?: string;
  rating: number;
  description: string;
  availability?: string[];
  links?: StoreLinks;
}

export function ProductCard({ image, name, brand, price, rating, description, links }: ProductCardProps) {
  // Use direct product URL if available, otherwise fall back to store search links
  const primaryUrl = links?.product_url
    || links?.amazon
    || links?.nykaa
    || links?.flipkart;

  const storeLabel = links?.product_url
    ? 'LookFantastic'
    : links?.amazon
    ? 'Amazon'
    : links?.nykaa
    ? 'Nykaa'
    : 'Flipkart';

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 flex flex-col">
      {/* Image */}
      <div className="aspect-square bg-gray-50 flex items-center justify-center p-4">
        <img src={image} alt={name} className="w-full h-full object-contain" />
      </div>

      {/* Info */}
      <div className="p-5 flex flex-col flex-1">
        <p className="text-xs text-[#9C8CFF] font-semibold uppercase tracking-wider mb-1">{brand}</p>
        <h3 className="font-semibold text-base text-[#2B2B2B] line-clamp-2 mb-2">{name}</h3>

        {/* Rating */}
        <div className="flex items-center gap-1 mb-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Star key={i} className={`w-3.5 h-3.5 ${i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />
          ))}
          <span className="text-xs text-gray-500 ml-1">({rating}.0)</span>
        </div>

        <p className="text-sm text-gray-600 line-clamp-2 mb-3 flex-1">{description}</p>

        {/* Price */}
        {price && (
          <div className="text-xl font-bold text-[#3EB6B1] mb-4">{price}</div>
        )}

        {/* Buy button */}
        {primaryUrl ? (
          <a
            href={primaryUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl bg-[#3EB6B1] text-white text-sm font-semibold hover:bg-[#2ea09b] transition-colors"
          >
            View on {storeLabel}
            <ExternalLink className="w-4 h-4" />
          </a>
        ) : (
          <div className="text-xs text-gray-400 text-center py-2">No link available</div>
        )}
      </div>
    </div>
  );
}
