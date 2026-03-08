import { useState, useRef } from 'react';
import { useNavigate } from 'react-router';
import { Navbar } from '../components/navbar';
import { Footer } from '../components/footer';
import { Button } from '../components/button';
import { Upload, Link as LinkIcon, Sparkles, DollarSign } from 'lucide-react';

export function AnalysisPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState('');
  const [country, setCountry] = useState('');
  const [priceRange, setPriceRange] = useState([0, 100]);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      setSelectedImage(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleFileSelect(file);
    }
  };

  const handleUrlSubmit = () => {
    if (imageUrl) {
      setSelectedImage(imageUrl);
    }
  };

  const handleAnalyze = () => {
    if (selectedImage && country) {
      // Navigate to results page with state
      navigate('/results', {
        state: {
          image: selectedImage,
          country,
          priceRange,
        },
      });
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <div className="flex-1 bg-gradient-to-br from-[#F8FAFB] to-[#3EB6B1]/5 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#3EB6B1]/10 border border-[#3EB6B1]/20 mb-4">
              <Sparkles className="w-4 h-4 text-[#3EB6B1]" />
              <span className="text-sm font-medium text-[#3EB6B1]">AI-Powered Analysis</span>
            </div>
            <h1 className="text-4xl font-bold text-[#2B2B2B] mb-4">
              Analyze Your Skin Concern
            </h1>
            <p className="text-lg text-gray-600">
              Upload an image and get personalized skincare recommendations
            </p>
          </div>

          {/* Main Card */}
          <div className="bg-white rounded-3xl shadow-xl p-8 md:p-10 space-y-8">
            {/* Image Upload Section */}
            <div>
              <label className="block text-sm font-semibold text-[#2B2B2B] mb-3">
                Upload Skin Image
              </label>
              
              {/* Drag and Drop Area */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200 ${
                  isDragging
                    ? 'border-[#3EB6B1] bg-[#3EB6B1]/5'
                    : selectedImage
                    ? 'border-[#3EB6B1] bg-[#3EB6B1]/5'
                    : 'border-gray-300 hover:border-[#3EB6B1] hover:bg-gray-50'
                }`}
              >
                {selectedImage ? (
                  <div className="space-y-4">
                    <img
                      src={selectedImage}
                      alt="Selected"
                      className="max-h-64 mx-auto rounded-xl shadow-lg"
                    />
                    <p className="text-sm text-[#3EB6B1] font-medium">
                      Image uploaded successfully! Click to change.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-[#3EB6B1]/10 rounded-2xl flex items-center justify-center mx-auto">
                      <Upload className="w-8 h-8 text-[#3EB6B1]" />
                    </div>
                    <div>
                      <p className="text-lg font-medium text-[#2B2B2B] mb-1">
                        Drag & drop your image here
                      </p>
                      <p className="text-sm text-gray-500">
                        or click to browse from your device
                      </p>
                    </div>
                    <p className="text-xs text-gray-400">
                      Supports: JPG, PNG, JPEG (Max 10MB)
                    </p>
                  </div>
                )}
              </div>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelect(file);
                }}
                className="hidden"
              />
            </div>

            {/* URL Input Section */}
            <div>
              <label className="block text-sm font-semibold text-[#2B2B2B] mb-3">
                Or Paste Image URL
              </label>
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="url"
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                    placeholder="https://example.com/image.jpg"
                    className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-[#3EB6B1] focus:border-transparent transition-all duration-200"
                  />
                </div>
                <Button onClick={handleUrlSubmit} variant="outline">
                  Load Image
                </Button>
              </div>
            </div>

            {/* Divider */}
            <div className="border-t border-gray-200"></div>

            {/* Country Selector */}
            <div>
              <label className="block text-sm font-semibold text-[#2B2B2B] mb-3">
                Select Your Country
              </label>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-[#3EB6B1] focus:border-transparent transition-all duration-200"
              >
                <option value="">Choose your country</option>
                <option value="US">United States</option>
                <option value="UK">United Kingdom</option>
                <option value="IN">India</option>
                <option value="CA">Canada</option>
                <option value="AU">Australia</option>
                <option value="DE">Germany</option>
                <option value="FR">France</option>
                <option value="JP">Japan</option>
                <option value="BR">Brazil</option>
                <option value="MX">Mexico</option>
              </select>
            </div>

            {/* Price Range Slider */}
            <div>
              <label className="block text-sm font-semibold text-[#2B2B2B] mb-3">
                Price Range
              </label>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Budget</span>
                  <span className="font-semibold text-[#3EB6B1]">
                    ${priceRange[0]} - ${priceRange[1]}
                  </span>
                </div>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="0"
                    max="200"
                    value={priceRange[1]}
                    onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#3EB6B1]"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>$0</span>
                    <span>$50</span>
                    <span>$100</span>
                    <span>$150</span>
                    <span>$200+</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Analyze Button */}
            <div className="pt-4">
              <Button
                onClick={handleAnalyze}
                disabled={!selectedImage || !country}
                size="lg"
                className="w-full"
              >
                <Sparkles className="w-5 h-5" />
                Analyze My Skin
              </Button>
              {(!selectedImage || !country) && (
                <p className="text-center text-sm text-gray-500 mt-3">
                  Please upload an image and select your country to continue
                </p>
              )}
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="w-12 h-12 bg-[#3EB6B1]/10 rounded-xl flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-[#3EB6B1]" />
              </div>
              <h3 className="font-semibold text-[#2B2B2B] mb-2">AI Analysis</h3>
              <p className="text-sm text-gray-600">
                Advanced AI detects skin concerns with 98% accuracy
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="w-12 h-12 bg-[#9C8CFF]/10 rounded-xl flex items-center justify-center mb-4">
                <DollarSign className="w-6 h-6 text-[#9C8CFF]" />
              </div>
              <h3 className="font-semibold text-[#2B2B2B] mb-2">Budget Friendly</h3>
              <p className="text-sm text-gray-600">
                Find products that match your budget preferences
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="w-12 h-12 bg-[#FFB6A3]/10 rounded-xl flex items-center justify-center mb-4">
                <Upload className="w-6 h-6 text-[#FFB6A3]" />
              </div>
              <h3 className="font-semibold text-[#2B2B2B] mb-2">Easy Upload</h3>
              <p className="text-sm text-gray-600">
                Drag & drop or paste image URL for quick analysis
              </p>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
