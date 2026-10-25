import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  ShoppingBag,
  Menu as MenuIcon,
  X,
  CalendarCheck,
  Shield,
  LayoutDashboard,
  ChefHat,
  LogOut,
  UtensilsCrossed,
  Grid,
  PhoneCall,
  Flame,
  Award
} from 'lucide-react';

interface NavbarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPath, onNavigate }) => {
  const { settings, cartCount, currentUser, logout, login } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNav = (path: string) => {
    onNavigate(path);
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <header className="sticky top-0 z-50 w-full transition-all duration-300">
      {/* Demo Banner */}
      <div className="bg-[#1e3a8a] text-white px-4 py-2 text-xs md:text-sm font-medium flex items-center justify-between flex-wrap gap-2 border-b border-white/10 shadow-sm">
        <div className="flex items-center gap-2 mx-auto sm:mx-0">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>
            Live Demo: <strong>Restaurant CMS Pro</strong> (La Bella Cucina v2.0)
          </span>
        </div>
        <div className="flex items-center gap-3 mx-auto sm:mx-0">
          {currentUser ? (
            <span className="text-slate-200 text-xs">
              Signed in as <strong className="text-amber-300">{currentUser.username}</strong> ({currentUser.role})
            </span>
          ) : (
            <button
              onClick={() => {
                login('admin', 'admin');
                handleNav('/dashboard');
              }}
              className="text-amber-300 hover:text-white underline font-semibold transition-colors flex items-center gap-1"
            >
              <Shield className="w-3.5 h-3.5" /> Quick Demo Admin Access
            </button>
          )}
          <span className="text-slate-400 hidden sm:inline">|</span>
          <button
            onClick={() => handleNav('/kitchen')}
            className="text-slate-200 hover:text-amber-300 transition-colors flex items-center gap-1 font-medium"
          >
            <ChefHat className="w-3.5 h-3.5" /> Kitchen Screen
          </button>
          <span className="text-slate-400 hidden sm:inline">|</span>
          <button
            onClick={() => handleNav('/table/4')}
            className="text-slate-200 hover:text-amber-300 transition-colors flex items-center gap-1 font-medium"
          >
            <UtensilsCrossed className="w-3.5 h-3.5" /> Table 4 QR Order
          </button>
        </div>
      </div>

      {/* Admin Quick Action Strip when authenticated */}
      {currentUser && (
        <div className="bg-[#0f172a] text-slate-300 px-4 sm:px-8 py-1.5 text-xs font-medium flex items-center justify-between border-b border-white/10 overflow-x-auto">
          <div className="flex items-center gap-2">
            <Shield className="w-3.5 h-3.5 text-[#C9A96E]" />
            <span className="text-white font-semibold">Admin Panel</span>
            <span className="text-slate-400">({currentUser.role})</span>
          </div>
          <div className="flex items-center gap-4 flex-nowrap shrink-0">
            <button
              onClick={() => handleNav('/dashboard')}
              className={`hover:text-amber-300 flex items-center gap-1.5 ${currentPath === '/dashboard' ? 'text-amber-300 font-bold' : ''}`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" /> Dashboard
            </button>
            <button
              onClick={() => handleNav('/kitchen')}
              className={`hover:text-amber-300 flex items-center gap-1.5 ${currentPath === '/kitchen' ? 'text-amber-300 font-bold' : ''}`}
            >
              <Flame className="w-3.5 h-3.5 text-amber-400" /> Kitchen (KDS)
            </button>
            <button
              onClick={() => handleNav('/admin/tables')}
              className={`hover:text-amber-300 flex items-center gap-1.5 ${currentPath === '/admin/tables' ? 'text-amber-300 font-bold' : ''}`}
            >
              <Grid className="w-3.5 h-3.5" /> Floor Plan
            </button>
            <button
              onClick={() => handleNav('/admin/reservations')}
              className={`hover:text-amber-300 flex items-center gap-1.5 ${currentPath === '/admin/reservations' ? 'text-amber-300 font-bold' : ''}`}
            >
              Reservations
            </button>
            <button
              onClick={() => handleNav('/admin/orders')}
              className={`hover:text-amber-300 flex items-center gap-1.5 ${currentPath === '/admin/orders' ? 'text-amber-300 font-bold' : ''}`}
            >
              Orders
            </button>
            <button
              onClick={() => handleNav('/editor')}
              className={`hover:text-amber-300 flex items-center gap-1.5 ${currentPath === '/editor' ? 'text-amber-300 font-bold' : ''}`}
            >
              CMS Editor
            </button>
            <button
              onClick={() => {
                logout();
                handleNav('/');
              }}
              className="text-red-400 hover:text-red-300 flex items-center gap-1 ml-2"
            >
              <LogOut className="w-3.5 h-3.5" /> Logout
            </button>
          </div>
        </div>
      )}

      {/* Main Navbar */}
      <nav className="bg-white/95 backdrop-blur-md border-b border-black/5 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          {/* Brand */}
          <button
            onClick={() => handleNav('/')}
            className="flex items-center gap-2 group text-left cursor-pointer"
          >
            <span className="w-2.5 h-2.5 rounded-full bg-[#C9A96E] group-hover:scale-125 transition-transform"></span>
            <span className="font-serif text-2xl sm:text-3xl font-bold tracking-tight text-[#0B0F19]">
              {settings.name}
              <span className="text-[#C9A96E]">.</span>
            </span>
          </button>

          {/* Desktop Nav Links */}
          <div className="hidden lg:flex items-center gap-1 font-medium text-sm text-slate-700">
            <button
              onClick={() => handleNav('/')}
              className={`px-3 py-2 rounded-lg transition-colors ${currentPath === '/' ? 'text-[#0B0F19] font-semibold bg-stone-100' : 'hover:text-[#0B0F19] hover:bg-stone-50'}`}
            >
              Home
            </button>
            <button
              onClick={() => handleNav('/menu')}
              className={`px-3 py-2 rounded-lg transition-colors ${currentPath === '/menu' ? 'text-[#0B0F19] font-semibold bg-stone-100' : 'hover:text-[#0B0F19] hover:bg-stone-50'}`}
            >
              Menu
            </button>
            {settings.enableOnlineOrdering && (
              <button
                onClick={() => handleNav('/order')}
                className={`px-3 py-2 rounded-lg transition-colors ${currentPath === '/order' ? 'text-[#0B0F19] font-semibold bg-stone-100' : 'hover:text-[#0B0F19] hover:bg-stone-50'}`}
              >
                Order Online
              </button>
            )}
            {settings.enableWaitlist && (
              <button
                onClick={() => handleNav('/waitlist')}
                className={`px-3 py-2 rounded-lg transition-colors ${currentPath === '/waitlist' ? 'text-[#0B0F19] font-semibold bg-stone-100' : 'hover:text-[#0B0F19] hover:bg-stone-50'}`}
              >
                Waitlist
              </button>
            )}
            {settings.enableEvents && (
              <button
                onClick={() => handleNav('/events')}
                className={`px-3 py-2 rounded-lg transition-colors ${currentPath === '/events' ? 'text-[#0B0F19] font-semibold bg-stone-100' : 'hover:text-[#0B0F19] hover:bg-stone-50'}`}
              >
                Events
              </button>
            )}
            {settings.enableGallery && (
              <button
                onClick={() => handleNav('/gallery')}
                className={`px-3 py-2 rounded-lg transition-colors ${currentPath === '/gallery' ? 'text-[#0B0F19] font-semibold bg-stone-100' : 'hover:text-[#0B0F19] hover:bg-stone-50'}`}
              >
                Gallery
              </button>
            )}
            <button
              onClick={() => handleNav('/about')}
              className={`px-3 py-2 rounded-lg transition-colors ${currentPath === '/about' ? 'text-[#0B0F19] font-semibold bg-stone-100' : 'hover:text-[#0B0F19] hover:bg-stone-50'}`}
            >
              About
            </button>
            <button
              onClick={() => handleNav('/contact')}
              className={`px-3 py-2 rounded-lg transition-colors ${currentPath === '/contact' ? 'text-[#0B0F19] font-semibold bg-stone-100' : 'hover:text-[#0B0F19] hover:bg-stone-50'}`}
            >
              Contact
            </button>

            {/* Quick links dropdown / extra items */}
            <div className="relative group/drop">
              <button className="px-2 py-2 text-slate-500 hover:text-slate-800 text-xs font-semibold uppercase tracking-wider flex items-center gap-1">
                More ▾
              </button>
              <div className="absolute right-0 top-full hidden group-hover/drop:block bg-white border border-stone-200 shadow-xl rounded-xl py-2 w-48 z-50">
                <button
                  onClick={() => handleNav('/loyalty')}
                  className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-stone-50 hover:text-[#0B0F19] flex items-center gap-2"
                >
                  <Award className="w-4 h-4 text-amber-500" /> Rewards & Points
                </button>
                <button
                  onClick={() => handleNav('/gift-cards')}
                  className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-stone-50 hover:text-[#0B0F19]"
                >
                  🎁 Gift Cards
                </button>
                <button
                  onClick={() => handleNav('/table/4')}
                  className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-stone-50 hover:text-[#0B0F19]"
                >
                  📱 Table QR Self-Order
                </button>
                <hr className="my-1 border-stone-100" />
                <button
                  onClick={() => handleNav('/login')}
                  className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-stone-50 hover:text-[#0B0F19] flex items-center gap-2"
                >
                  <Shield className="w-4 h-4 text-slate-400" /> Staff Portal
                </button>
              </div>
            </div>
          </div>

          {/* Right Action Buttons */}
          <div className="flex items-center gap-3">
            {/* Book Table CTA */}
            {settings.enableReservations && (
              <button
                onClick={() => handleNav('/reservations')}
                className="inline-flex items-center gap-2 px-4 sm:px-5 py-2.5 rounded-full bg-gradient-to-r from-[#0B0F19] to-[#1a2332] text-white text-xs sm:text-sm font-semibold tracking-wide uppercase hover:shadow-lg hover:shadow-stone-900/20 hover:-translate-y-0.5 transition-all duration-300"
              >
                <CalendarCheck className="w-4 h-4 text-[#C9A96E]" />
                <span className="hidden sm:inline">Book Table</span>
                <span className="sm:hidden">Book</span>
              </button>
            )}

            {/* Shopping Bag Button */}
            {settings.enableOnlineOrdering && (
              <button
                onClick={() => handleNav('/cart')}
                aria-label="View shopping bag"
                className="relative p-2.5 rounded-full text-stone-700 hover:bg-stone-100 hover:text-[#0B0F19] transition-colors"
              >
                <ShoppingBag className="w-5 h-5" />
                {cartCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-[#C9A96E] text-white font-bold text-[10px] w-5 h-5 rounded-full flex items-center justify-center shadow-md animate-scale">
                    {cartCount}
                  </span>
                )}
              </button>
            )}

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-xl text-stone-700 hover:bg-stone-100 transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <MenuIcon className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Dropdown */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-white border-t border-stone-100 px-4 pt-3 pb-6 space-y-1 shadow-2xl animate-fade-in">
            <button
              onClick={() => handleNav('/')}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-base font-medium ${currentPath === '/' ? 'bg-stone-100 font-bold text-[#0B0F19]' : 'text-slate-700 hover:bg-stone-50'}`}
            >
              Home
            </button>
            <button
              onClick={() => handleNav('/menu')}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-base font-medium ${currentPath === '/menu' ? 'bg-stone-100 font-bold text-[#0B0F19]' : 'text-slate-700 hover:bg-stone-50'}`}
            >
              Menu
            </button>
            <button
              onClick={() => handleNav('/order')}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-base font-medium ${currentPath === '/order' ? 'bg-stone-100 font-bold text-[#0B0F19]' : 'text-slate-700 hover:bg-stone-50'}`}
            >
              Order Online
            </button>
            <button
              onClick={() => handleNav('/reservations')}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-base font-medium ${currentPath === '/reservations' ? 'bg-stone-100 font-bold text-[#0B0F19]' : 'text-slate-700 hover:bg-stone-50'}`}
            >
              Reservations
            </button>
            <button
              onClick={() => handleNav('/waitlist')}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-base font-medium ${currentPath === '/waitlist' ? 'bg-stone-100 font-bold text-[#0B0F19]' : 'text-slate-700 hover:bg-stone-50'}`}
            >
              Waitlist
            </button>
            <button
              onClick={() => handleNav('/loyalty')}
              className="w-full text-left px-3 py-2.5 rounded-lg text-base font-medium text-slate-700 hover:bg-stone-50 flex items-center justify-between"
            >
              <span>Rewards & Loyalty</span>
              <span className="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-semibold">50 Free Pts</span>
            </button>
            <button
              onClick={() => handleNav('/gift-cards')}
              className="w-full text-left px-3 py-2.5 rounded-lg text-base font-medium text-slate-700 hover:bg-stone-50"
            >
              Digital Gift Cards
            </button>
            <button
              onClick={() => handleNav('/events')}
              className="w-full text-left px-3 py-2.5 rounded-lg text-base font-medium text-slate-700 hover:bg-stone-50"
            >
              Events & Private Dining
            </button>
            <button
              onClick={() => handleNav('/gallery')}
              className="w-full text-left px-3 py-2.5 rounded-lg text-base font-medium text-slate-700 hover:bg-stone-50"
            >
              Photo Gallery
            </button>
            <button
              onClick={() => handleNav('/about')}
              className="w-full text-left px-3 py-2.5 rounded-lg text-base font-medium text-slate-700 hover:bg-stone-50"
            >
              About Us
            </button>
            <button
              onClick={() => handleNav('/contact')}
              className="w-full text-left px-3 py-2.5 rounded-lg text-base font-medium text-slate-700 hover:bg-stone-50"
            >
              Contact & Directions
            </button>
            <button
              onClick={() => handleNav('/login')}
              className="w-full text-left px-3 py-2.5 rounded-lg text-base font-medium text-slate-500 hover:bg-stone-50 flex items-center gap-2"
            >
              <Shield className="w-4 h-4" /> Admin & Staff Login
            </button>
          </div>
        )}
      </nav>
    </header>
  );
};
