import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { Input } from '../components/input';
import { Button } from '../components/button';
import { Sparkles, Loader2 } from 'lucide-react';
import { apiLogin, setToken, setUser } from '../utils/api';

export function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '', remember: false });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await apiLogin({ email: formData.email, password: formData.password });
      if (!res.success) {
        setError(res.error?.message || 'Login failed.');
        return;
      }
      setToken(res.data.token);
      setUser(res.data.user);
      navigate('/analyze');
    } catch {
      setError('Could not reach the server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Illustration (Desktop Only) */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#3EB6B1] to-[#9C8CFF] relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjEiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-20"></div>
        <div className="relative z-10 flex flex-col items-center justify-center w-full p-12 text-white">
          <div className="max-w-md">
            <Sparkles className="w-16 h-16 mb-6" />
            <h2 className="text-4xl font-bold mb-4">Welcome Back!</h2>
            <p className="text-lg text-white/90 leading-relaxed">
              Continue your journey to healthier, more radiant skin with AI-powered skincare analysis.
            </p>
            <div className="mt-12">
              <img
                src="https://images.unsplash.com/photo-1741278232341-33534050414c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxza2luY2FyZSUyMGFuYWx5c2lzJTIwZGVybWF0b2xvZ3l8ZW58MXx8fHwxNzcyOTk0NjQxfDA&ixlib=rb-4.1.0&q=80&w=1080"
                alt="Skincare analysis"
                className="rounded-2xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#F8FAFB]">
        <div className="w-full max-w-md">
          {/* Logo (Mobile) */}
          <Link to="/" className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-10 h-10 bg-gradient-to-br from-[#3EB6B1] to-[#9C8CFF] rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl text-[#2B2B2B]">SkinIntel</span>
          </Link>

          <div className="bg-white rounded-3xl shadow-xl p-8 md:p-10">
            <h1 className="text-3xl font-bold text-[#2B2B2B] mb-2">
              Welcome Back to SkinIntel
            </h1>
            <p className="text-gray-600 mb-8">
              Sign in to access your personalized skincare recommendations
            </p>

            <form onSubmit={handleSubmit} className="space-y-5">
              <Input
                label="Email / Username"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />

              <Input
                label="Password"
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.remember}
                    onChange={(e) => setFormData({ ...formData, remember: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-[#3EB6B1] focus:ring-[#3EB6B1]"
                  />
                  <span className="text-sm text-gray-600">Remember me</span>
                </label>
                <a href="#" className="text-sm text-[#3EB6B1] hover:underline">
                  Forgot Password?
                </a>
              </div>

              <Button type="submit" className="w-full" size="lg" disabled={loading}>
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Signing in...</> : 'Login'}
              </Button>

              {error && <p className="text-sm text-red-500 text-center">{error}</p>}


              <p className="text-center text-sm text-gray-600 mt-6">
                Don't have an account?{' '}
                <Link to="/signup" className="text-[#3EB6B1] font-semibold hover:underline">
                  Sign Up
                </Link>
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
