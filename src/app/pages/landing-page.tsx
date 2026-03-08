import { Navbar } from '../components/navbar';
import { Footer } from '../components/footer';
import { Button } from '../components/button';
import { Link } from 'react-router';
import { Sparkles, MapPin, DollarSign, TrendingUp, Scan } from 'lucide-react';

export function LandingPage() {
  const features = [
    {
      icon: <Scan className="w-8 h-8 text-[#3EB6B1]" />,
      title: 'AI Skin Analysis',
      description: 'Advanced AI technology analyzes your skin concerns with precision and accuracy.',
      gradient: 'from-[#3EB6B1]/10 to-[#3EB6B1]/5',
    },
    {
      icon: <MapPin className="w-8 h-8 text-[#9C8CFF]" />,
      title: 'Country Based Product Suggestions',
      description: 'Get product recommendations available in your specific country and region.',
      gradient: 'from-[#9C8CFF]/10 to-[#9C8CFF]/5',
    },
    {
      icon: <DollarSign className="w-8 h-8 text-[#FFB6A3]" />,
      title: 'Price Range Filtering',
      description: 'Find products that fit your budget with customizable price range filters.',
      gradient: 'from-[#FFB6A3]/10 to-[#FFB6A3]/5',
    },
    {
      icon: <TrendingUp className="w-8 h-8 text-[#3EB6B1]" />,
      title: 'Smart Skincare Recommendations',
      description: 'Receive personalized product recommendations based on your skin analysis.',
      gradient: 'from-[#3EB6B1]/10 to-[#3EB6B1]/5',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[#F8FAFB] via-white to-[#3EB6B1]/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#3EB6B1]/10 border border-[#3EB6B1]/20">
                <Sparkles className="w-4 h-4 text-[#3EB6B1]" />
                <span className="text-sm font-medium text-[#3EB6B1]">AI-Powered Technology</span>
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#2B2B2B] leading-tight">
                AI Powered Skin Concern Analyzer
              </h1>

              <p className="text-lg text-gray-600 leading-relaxed">
                Upload your skin image and get AI-powered skincare recommendations tailored to your country and budget.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/analyze">
                  <Button size="lg" className="w-full sm:w-auto">
                    <Sparkles className="w-5 h-5" />
                    Analyze My Skin
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button variant="outline" size="lg" className="w-full sm:w-auto">
                    Sign Up Free
                  </Button>
                </Link>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-6 pt-8">
                <div>
                  <div className="text-3xl font-bold text-[#3EB6B1]">98%</div>
                  <div className="text-sm text-gray-600">Accuracy</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-[#9C8CFF]">1000+</div>
                  <div className="text-sm text-gray-600">Products</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-[#FFB6A3]">50+</div>
                  <div className="text-sm text-gray-600">Countries</div>
                </div>
              </div>
            </div>

            {/* Right Image */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-[#3EB6B1] to-[#9C8CFF] rounded-3xl blur-3xl opacity-20"></div>
              <div className="relative rounded-3xl overflow-hidden shadow-2xl">
                <img
                  src="https://images.unsplash.com/photo-1741278232341-33534050414c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxza2luY2FyZSUyMGFuYWx5c2lzJTIwZGVybWF0b2xvZ3l8ZW58MXx8fHwxNzcyOTk0NjQxfDA&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Skincare Analysis"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Decorative Elements */}
        <div className="absolute top-20 right-10 w-72 h-72 bg-[#9C8CFF]/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-10 w-96 h-96 bg-[#FFB6A3]/10 rounded-full blur-3xl"></div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[#2B2B2B] mb-4">
              Why Choose SkinIntel?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Advanced AI technology meets personalized skincare recommendations
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className={`bg-gradient-to-br ${feature.gradient} backdrop-blur-sm rounded-2xl p-6 hover:shadow-xl transition-all duration-300 border border-gray-100`}
              >
                <div className="bg-white w-16 h-16 rounded-xl flex items-center justify-center mb-4 shadow-md">
                  {feature.icon}
                </div>
                <h3 className="font-semibold text-lg text-[#2B2B2B] mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-[#3EB6B1] to-[#9C8CFF] relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjEiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-40"></div>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Skincare Routine?
          </h2>
          <p className="text-lg text-white/90 mb-8">
            Get personalized AI-powered recommendations in seconds
          </p>
          <Link to="/analyze">
            <Button size="lg" variant="accent" className="shadow-xl">
              <Sparkles className="w-5 h-5" />
              Start Your Analysis Now
            </Button>
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
