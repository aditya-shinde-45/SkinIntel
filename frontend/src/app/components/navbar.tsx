import { Link, useNavigate } from 'react-router';
import { Button } from './button';
import { Menu, X, Sparkles, LogOut, User } from 'lucide-react';
import { useState } from 'react';
import { isLoggedIn, getUser, clearToken } from '../utils/api';

export function Navbar() {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const loggedIn = isLoggedIn();
  const user = getUser();

  const handleLogout = () => {
    clearToken();
    navigate('/login');
  };

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-[#3EB6B1] to-[#9C8CFF] rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl text-[#2B2B2B]">SkinIntel</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {loggedIn ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#3EB6B1]/10 border border-[#3EB6B1]/20">
                  <User className="w-4 h-4 text-[#3EB6B1]" />
                  <span className="text-sm font-medium text-[#2B2B2B]">{user?.full_name?.split(' ')[0]}</span>
                </div>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOut className="w-4 h-4" />
                  Logout
                </Button>
              </div>
            ) : (
              <>
                <Link to="/login"><Button variant="outline" size="sm">Login</Button></Link>
                <Link to="/signup"><Button size="sm">Sign Up</Button></Link>
              </>
            )}
          </div>

          <button className="md:hidden p-2" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 space-y-4">
            {loggedIn ? (
              <>
                <p className="text-sm text-gray-600">Hi, {user?.full_name}</p>
                <Button variant="outline" size="sm" className="w-full" onClick={handleLogout}>
                  <LogOut className="w-4 h-4" /> Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login" onClick={() => setIsMenuOpen(false)}><Button variant="outline" size="sm" className="w-full">Login</Button></Link>
                <Link to="/signup" onClick={() => setIsMenuOpen(false)}><Button size="sm" className="w-full">Sign Up</Button></Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
