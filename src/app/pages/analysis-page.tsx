import { useState, useRef } from 'react';
import { useNavigate } from 'react-router';
import { Navbar } from '../components/navbar';
import { Footer } from '../components/footer';
import { Button } from '../components/button';
import { Upload, Sparkles, Loader2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export function AnalysisPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedImageName, setSelectedImageName] = useState('');
  const [country, setCountry] = useState('');
  const [priceRange, setPriceRange] = useState([200, 2000]);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      setSelectedImage(e.target?.result as string);
      setSelectedImageName(file.name);
    };
    reader.readAsDataURL(file);
    setSelectedFile(file);
    setError(null);
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

  const handleAnalyze = async () => {
    if (!selectedFile || !country) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('country', country);
      formData.append('min_price', String(priceRange[0]));
      formData.append('max_price', String(priceRange[1]));
      formData.append('limit', '10');

      const res = await fetch(`${API_BASE}/api/v1/analyze`, {
        method: 'POST',
        body: formData,
      });

      const json = await res.json();

      if (!json.success) {
        setError(json.error?.message || 'Analysis failed. Please try again.');
        return;
      }

      navigate('/results', {
        state: {
          image: selectedImage,
          imageName: selectedImageName,
          country,
          priceRange,
          apiResult: json.data,
          apiMeta: json.meta,
        },
      });
    } catch (err) {
      setError('Could not reach the analysis server. Please check your connection.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleMinPriceChange = (value: number) => {
    setPriceRange((prev) => [Math.min(value, prev[1]), prev[1]]);
  };

  const handleMaxPriceChange = (value: number) => {
    setPriceRange((prev) => [prev[0], Math.max(value, prev[0])]);
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
              <span className="text-sm font-medium text-[#3EB6B1]">
                AI-Powered Analysis
              </span>
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

            {/* Image Upload */}
            <div>
              <label className="block text-sm font-semibold text-[#2B2B2B] mb-3">
                Upload Skin Image
              </label>

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

            <div className="border-t border-gray-200"></div>

            {/* Country */}
            <div>
              <label className="block text-sm font-semibold text-[#2B2B2B] mb-3">
                Select Your Country
              </label>

              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-[#3EB6B1]"
              >
                <option value="">Choose your country</option>
                <option value="IN">India</option>
                <option value="US">United States</option>
                <option value="UK">United Kingdom</option>
                <option value="CA">Canada</option>
                <option value="AU">Australia</option>
                <option value="DE">Germany</option>
                <option value="FR">France</option>
                <option value="JP">Japan</option>
              </select>
            </div>

            {/* Price Range */}
            <div>
              <label className="block text-sm font-semibold text-[#2B2B2B] mb-3">
                Price Range
              </label>

              <div className="space-y-4">

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Budget</span>

                  <span className="font-semibold text-[#3EB6B1]">
                    ₹{priceRange[0]} - ₹{priceRange[1]}
                  </span>
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Minimum</span>
                      <span>₹{priceRange[0]}</span>
                    </div>
                    <input
                      type="range"
                      min="200"
                      max="3000"
                      step="100"
                      value={priceRange[0]}
                      onChange={(e) => handleMinPriceChange(parseInt(e.target.value, 10))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#3EB6B1]"
                    />
                  </div>

                  <div>
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Maximum</span>
                      <span>₹{priceRange[1]}</span>
                    </div>
                    <input
                      type="range"
                      min="200"
                      max="3000"
                      step="100"
                      value={priceRange[1]}
                      onChange={(e) => handleMaxPriceChange(parseInt(e.target.value, 10))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#3EB6B1]"
                    />
                  </div>
                </div>

                <div className="flex justify-between text-xs text-gray-500">
                  <span>₹200</span>
                  <span>₹500</span>
                  <span>₹1000</span>
                  <span>₹2000</span>
                  <span>₹3000+</span>
                </div>
              </div>
            </div>

            {/* Analyze Button */}
            <div className="pt-4">
              <Button
                onClick={handleAnalyze}
                disabled={!selectedImage || !country || isAnalyzing}
                size="lg"
                className="w-full"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Analyze My Skin
                  </>
                )}
              </Button>

              {error && (
                <p className="text-center text-sm text-red-500 mt-3">{error}</p>
              )}

              {(!selectedImage || !country) && !error && (
                <p className="text-center text-sm text-gray-500 mt-3">
                  Please upload an image and select your country to continue
                </p>
              )}
            </div>

          </div>

        </div>
      </div>

      <Footer />
    </div>
  );
}