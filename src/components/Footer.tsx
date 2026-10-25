import React from 'react';
import { useApp } from '../context/AppContext';
import { MapPin, Phone, Mail, Clock, ShieldCheck, Heart } from 'lucide-react';

interface FooterProps {
  onNavigate: (path: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  const { settings } = useApp();

  return (
    <footer className="bg-gradient-to-b from-[#0B0F19] to-[#04060a] text-slate-400 pt-16 pb-12 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
          {/* Brand info */}
          <div className="space-y-4">
            <h3 className="font-serif text-2xl font-bold text-white tracking-tight">
              {settings.name}
              <span className="text-[#C9A96E]">.</span>
            </h3>
            <p className="text-sm leading-relaxed text-slate-300">
              {settings.tagline}. Hand-rolled pasta, wood-fired hearth cooking, and authentic hospitality in the heart of San Francisco since 2019.
            </p>
            <div className="pt-2 flex items-center gap-3">
              <a
                href={`https://instagram.com/${settings.social.instagram}`}
                target="_blank"
                rel="noreferrer"
                className="w-10 h-10 rounded-full bg-white/5 hover:bg-[#C9A96E] hover:text-white transition-all flex items-center justify-center text-slate-300"
                aria-label="Instagram"
              >
                <span className="font-bold text-sm">IG</span>
              </a>
              <a
                href={`https://facebook.com/${settings.social.facebook}`}
                target="_blank"
                rel="noreferrer"
                className="w-10 h-10 rounded-full bg-white/5 hover:bg-[#C9A96E] hover:text-white transition-all flex items-center justify-center text-slate-300"
                aria-label="Facebook"
              >
                <span className="font-bold text-sm">FB</span>
              </a>
              <button
                onClick={() => onNavigate('/login')}
                className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/20 transition-all flex items-center justify-center text-slate-400 hover:text-white"
                title="Staff Portal Login"
              >
                <ShieldCheck className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Explore */}
          <div>
            <h4 className="font-sans text-xs font-bold tracking-widest uppercase text-white mb-5 border-l-2 border-[#C9A96E] pl-2.5">
              Explore
            </h4>
            <ul className="space-y-3 text-sm">
              <li>
                <button
                  onClick={() => onNavigate('/')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Home
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/menu')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Dining Menu & Wine List
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/about')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Our Tuscan Heritage
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/gallery')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Atmosphere & Gallery
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/events')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Private Dining & Events
                </button>
              </li>
            </ul>
          </div>

          {/* Dining Services */}
          <div>
            <h4 className="font-sans text-xs font-bold tracking-widest uppercase text-white mb-5 border-l-2 border-[#C9A96E] pl-2.5">
              Guest Services
            </h4>
            <ul className="space-y-3 text-sm">
              <li>
                <button
                  onClick={() => onNavigate('/order')}
                  className="hover:text-[#C9A96E] transition-colors flex items-center gap-1.5"
                >
                  <span>Online Ordering (0% Commission)</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/reservations')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Table Reservations
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/waitlist')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Live SMS Waitlist
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/loyalty')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Customer Loyalty Rewards
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/gift-cards')}
                  className="hover:text-[#C9A96E] transition-colors"
                >
                  Digital Gift Cards
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('/table/4')}
                  className="hover:text-[#C9A96E] transition-colors text-amber-300/80"
                >
                  Dine-In QR Table Ordering
                </button>
              </li>
            </ul>
          </div>

          {/* Contact & Hours */}
          <div>
            <h4 className="font-sans text-xs font-bold tracking-widest uppercase text-white mb-5 border-l-2 border-[#C9A96E] pl-2.5">
              Hours & Location
            </h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-2.5">
                <MapPin className="w-4 h-4 text-[#C9A96E] shrink-0 mt-0.5" />
                <span>{settings.address}</span>
              </div>
              <div className="flex items-center gap-2.5">
                <Phone className="w-4 h-4 text-[#C9A96E] shrink-0" />
                <a href={settings.phoneLink} className="hover:text-white transition-colors">
                  {settings.phone}
                </a>
              </div>
              <div className="flex items-center gap-2.5">
                <Mail className="w-4 h-4 text-[#C9A96E] shrink-0" />
                <a href={`mailto:${settings.email}`} className="hover:text-white transition-colors">
                  {settings.email}
                </a>
              </div>
              <div className="pt-2 border-t border-white/10 space-y-1.5">
                <div className="flex items-center gap-2 text-xs font-semibold text-white">
                  <Clock className="w-3.5 h-3.5 text-[#C9A96E]" /> Service Hours
                </div>
                {settings.hours.map((h, i) => (
                  <div key={i} className="text-xs flex justify-between text-slate-400">
                    <span>{h.days}</span>
                    <span className="text-slate-200">{h.time}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} {settings.name}. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              Handcrafted with <Heart className="w-3 h-3 text-rose-500 fill-rose-500" /> for Independent Restaurants
            </span>
            <button
              onClick={() => onNavigate('/dashboard')}
              className="text-slate-400 hover:text-amber-300 transition-colors"
            >
              CMS Backoffice
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};
