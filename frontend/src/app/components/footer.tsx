import { Facebook, Twitter, Instagram, Linkedin } from 'lucide-react';
import { Link } from 'react-router';

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About Section */}
          <div>
            <h4 className="font-bold text-lg mb-4 text-[#2B2B2B]">About SkinIntel</h4>
            <p className="text-sm text-gray-600 leading-relaxed">
              AI-powered skincare analysis and recommendations tailored to your needs.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-bold text-lg mb-4 text-[#2B2B2B]">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-sm text-gray-600 hover:text-[#3EB6B1] transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/analyze" className="text-sm text-gray-600 hover:text-[#3EB6B1] transition-colors">
                  Analyze Skin
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-bold text-lg mb-4 text-[#2B2B2B]">Legal</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-[#3EB6B1] transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-[#3EB6B1] transition-colors">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-[#3EB6B1] transition-colors">
                  Disclaimer
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-bold text-lg mb-4 text-[#2B2B2B]">Connect</h4>
            <div className="flex gap-4">
              <a href="#" className="text-gray-600 hover:text-[#3EB6B1] transition-colors">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-600 hover:text-[#3EB6B1] transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-600 hover:text-[#3EB6B1] transition-colors">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-600 hover:text-[#3EB6B1] transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
            <p className="text-sm text-gray-600 mt-4">contact@skinintel.com</p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
            <p className="text-xs text-gray-700 leading-relaxed">
              ⚠️ <span className="font-semibold">Disclaimer:</span> SkinIntel provides AI-based skincare awareness and product suitability guidance for informational and academic purposes only. It does not offer medical diagnosis or replace professional dermatological advice. For serious or persistent skin concerns, please consult a licensed dermatologist.
            </p>
          </div>
          <p className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} SkinIntel. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
