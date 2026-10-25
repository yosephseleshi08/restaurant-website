import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  CalendarCheck,
  ShoppingBag,
  Clock,
  Sparkles,
  Award,
  ChevronRight,
  Star,
  CheckCircle2,
  Utensils,
  MapPin,
  TrendingDown,
  ShieldCheck,
  Users
} from 'lucide-react';

interface HomeProps {
  onNavigate: (path: string) => void;
}

export const Home: React.FC<HomeProps> = ({ onNavigate }) => {
  const { settings, menu, addToCart, addReservation } = useApp();

  // Quick reservation form state
  const [resDate, setResDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });
  const [resTime, setResTime] = useState('19:00');
  const [resGuests, setResGuests] = useState(2);
  const [resName, setResName] = useState('');
  const [resEmail, setResEmail] = useState('');
  const [resPhone, setResPhone] = useState('');
  const [resMessage, setResMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleQuickBook = (e: React.FormEvent) => {
    e.preventDefault();
    if (!resName || !resEmail || !resPhone) {
      setResMessage({ type: 'error', text: 'Please complete all required fields.' });
      return;
    }
    const result = addReservation({
      customerName: resName,
      customerEmail: resEmail,
      customerPhone: resPhone,
      partySize: Number(resGuests),
      date: resDate,
      time: resTime,
    });
    if (result.success) {
      setResMessage({ type: 'success', text: result.message });
      setResName('');
      setResEmail('');
      setResPhone('');
    } else {
      setResMessage({ type: 'error', text: result.message });
    }
  };

  // Featured items: 1 from appetizers, 1 from pasta, 1 from mains, 1 from pizza
  const featured = [
    ...(menu.appetizers || []).filter((i) => i.popular).slice(0, 1),
    ...(menu.pasta || []).filter((i) => i.popular).slice(0, 1),
    ...(menu.mains || []).filter((i) => i.popular).slice(0, 1),
    ...(menu.desserts || []).filter((i) => i.popular).slice(0, 1),
  ];

  return (
    <div className="min-h-screen bg-[#FAFAF9]">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center text-center text-white overflow-hidden bg-gradient-to-br from-[#0B0F19] via-[#1a2332] to-[#0B0F19]">
        {/* Background image with gentle overlay */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30 mix-blend-overlay"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1920&h=1080&fit=crop')",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0B0F19]/80 via-[#0B0F19]/60 to-[#0B0F19]/95" />

        <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 py-20 flex flex-col items-center">
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-[0.25em] text-[#C9A96E] bg-[#C9A96E]/10 border border-[#C9A96E]/30 mb-6 backdrop-blur-sm">
            <Sparkles className="w-3.5 h-3.5" /> Modern Tuscan Gastronomy
          </span>

          <h1 className="font-serif text-4xl sm:text-6xl md:text-7xl font-bold tracking-tight text-white mb-6 leading-[1.08]">
            Authentic Flavor,{' '}
            <span className="italic font-normal text-[#C9A96E] block sm:inline">
              Crafted by Fire.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 font-light max-w-2xl mb-10 leading-relaxed">
            Welcome to {settings.name}. Hand-extruded pasta, heritage Tuscan truffles, and prime wood-fired steaks served with timeless warmth.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 mb-14">
            <button
              onClick={() => onNavigate('/reservations')}
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-gradient-to-r from-[#C9A96E] to-[#b38e55] text-stone-900 font-bold text-sm tracking-wider uppercase hover:shadow-xl hover:shadow-amber-500/20 hover:-translate-y-0.5 transition-all duration-300"
            >
              <CalendarCheck className="w-4 h-4 text-stone-900" /> Reserve a Table
            </button>
            <button
              onClick={() => onNavigate('/order')}
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white/10 hover:bg-white text-white hover:text-stone-900 font-semibold text-sm tracking-wider uppercase border border-white/30 hover:border-white transition-all duration-300"
            >
              <ShoppingBag className="w-4 h-4" /> Order Directly (0% Fee)
            </button>
          </div>

          {/* Quick value badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-8 pt-8 border-t border-white/10 text-xs text-slate-300">
            <div className="flex items-center gap-2 justify-center">
              <CheckCircle2 className="w-4 h-4 text-[#C9A96E]" />
              <span>Fresh Daily Pasta</span>
            </div>
            <div className="flex items-center gap-2 justify-center">
              <CheckCircle2 className="w-4 h-4 text-[#C9A96E]" />
              <span>Wood-Fired Hearth</span>
            </div>
            <div className="flex items-center gap-2 justify-center">
              <CheckCircle2 className="w-4 h-4 text-[#C9A96E]" />
              <span>Direct Kitchen Order</span>
            </div>
            <div className="flex items-center gap-2 justify-center">
              <CheckCircle2 className="w-4 h-4 text-[#C9A96E]" />
              <span>Organic Wine Selection</span>
            </div>
          </div>
        </div>
      </section>

      {/* Value Proposition Section (from original restaurant_website_pro) */}
      <section className="bg-emerald-950/20 border-y border-emerald-900/10 py-12 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-10">
            <span className="text-emerald-700 text-xs font-bold uppercase tracking-widest bg-emerald-100 px-3 py-1 rounded-full">
              Why Order Direct?
            </span>
            <h2 className="font-serif text-2xl sm:text-3xl font-bold text-stone-900 mt-3 mb-2">
              Skip The Third-Party Delivery Apps
            </h2>
            <p className="text-stone-600 text-sm">
              Third-party delivery corporations take 30% commission from local family restaurants. Ordering directly supports our staff and gives you exclusive rewards!
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 flex items-start gap-4">
              <div className="p-3 bg-emerald-50 rounded-xl text-emerald-600 shrink-0">
                <TrendingDown className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-serif text-lg font-bold text-stone-900 mb-1">0% App Commission</h3>
                <p className="text-xs text-stone-600 leading-relaxed">
                  Every single dollar stays with our culinary team and local purveyors, keeping our menu prices honest and affordable.
                </p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 flex items-start gap-4">
              <div className="p-3 bg-amber-50 rounded-xl text-[#C9A96E] shrink-0">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-serif text-lg font-bold text-stone-900 mb-1">Loyalty Points Earned</h3>
                <p className="text-xs text-stone-600 leading-relaxed">
                  Earn 1 point per $1 spent on every takeout or dine-in order. 100 points converts immediately to $10 off your next feast!
                </p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 flex items-start gap-4">
              <div className="p-3 bg-blue-50 rounded-xl text-blue-600 shrink-0">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-serif text-lg font-bold text-stone-900 mb-1">Kitchen-Fresh Timing</h3>
                <p className="text-xs text-stone-600 leading-relaxed">
                  Orders route directly to our live kitchen display screen (KDS) without delays or confusing third-party courier dispatchers.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Chef Specials */}
      <section className="py-20 px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row items-center justify-between mb-12 gap-4">
          <div>
            <span className="text-[#C9A96E] text-xs font-bold uppercase tracking-widest">
              Signature Dishes
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#0B0F19] mt-1">
              Chef’s Featured Recommendations
            </h2>
          </div>
          <button
            onClick={() => onNavigate('/menu')}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#0B0F19] hover:text-[#C9A96E] transition-colors"
          >
            Explore Complete Menu <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featured.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-stone-200/60 flex flex-col group"
            >
              <div className="relative h-48 overflow-hidden">
                <img
                  src={item.image}
                  alt={item.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  loading="lazy"
                />
                <div className="absolute top-3 right-3 bg-stone-900/80 backdrop-blur-md text-amber-300 font-bold px-3 py-1 rounded-full text-xs">
                  ${item.price.toFixed(2)}
                </div>
                {item.popular && (
                  <span className="absolute top-3 left-3 bg-[#C9A96E] text-stone-900 text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded-full">
                    Guest Favorite
                  </span>
                )}
              </div>

              <div className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-serif text-lg font-bold text-[#0B0F19] mb-2 leading-snug">
                    {item.name}
                  </h3>
                  <p className="text-stone-500 text-xs line-clamp-2 leading-relaxed mb-4">
                    {item.description}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-stone-100">
                  <div className="flex flex-wrap gap-1">
                    {item.dietary.map((tag) => (
                      <span
                        key={tag}
                        className="text-[10px] bg-stone-100 text-stone-600 px-2 py-0.5 rounded font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={() => addToCart(item, 1)}
                    className="p-2 rounded-xl bg-stone-100 hover:bg-[#0B0F19] text-stone-800 hover:text-white transition-colors"
                    title="Add to order"
                  >
                    <ShoppingBag className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Reservation Quick-Booking Widget Section */}
      <section className="py-20 bg-stone-900 text-white relative overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-10"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1544025162-d76694265947?w=1920&h=800&fit=crop')",
          }}
        />
        <div className="relative max-w-5xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left text */}
            <div className="lg:col-span-5 space-y-5">
              <span className="text-[#C9A96E] text-xs font-bold uppercase tracking-widest">
                Seamless Reservations
              </span>
              <h2 className="font-serif text-3xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
                Secure Your Evening at {settings.name}
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed">
                Experience our open hearth kitchen and candlelit dining room. We hold reserved tables for 15 minutes past booking time.
              </p>

              <div className="space-y-3 pt-2 text-xs text-slate-300">
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-[#C9A96E]">
                    <Clock className="w-3.5 h-3.5" />
                  </div>
                  <span>Instant confirmation with SMS & Email alert</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-[#C9A96E]">
                    <Users className="w-3.5 h-3.5" />
                  </div>
                  <span>Parties of 8+ welcome with dedicated sommelier</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-[#C9A96E]">
                    <Award className="w-3.5 h-3.5" />
                  </div>
                  <span>Dedicated capacity guard ensures no overcrowding</span>
                </div>
              </div>
            </div>

            {/* Right form card */}
            <div className="lg:col-span-7 bg-white text-stone-900 p-6 sm:p-8 rounded-3xl shadow-2xl">
              <h3 className="font-serif text-xl font-bold text-[#0B0F19] mb-1">
                Book a Table
              </h3>
              <p className="text-xs text-stone-500 mb-6">
                Choose your party size, date and preferred seating time.
              </p>

              {resMessage && (
                <div
                  className={`p-4 rounded-xl text-xs mb-4 flex items-center gap-2 ${
                    resMessage.type === 'success'
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-rose-50 text-rose-800 border border-rose-200'
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{resMessage.text}</span>
                </div>
              )}

              <form onSubmit={handleQuickBook} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Date *
                    </label>
                    <input
                      type="date"
                      required
                      value={resDate}
                      onChange={(e) => setResDate(e.target.value)}
                      className="w-full text-xs p-2.5 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Time Slot *
                    </label>
                    <select
                      value={resTime}
                      onChange={(e) => setResTime(e.target.value)}
                      className="w-full text-xs p-2.5 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    >
                      <option value="17:00">5:00 PM</option>
                      <option value="17:30">5:30 PM</option>
                      <option value="18:00">6:00 PM</option>
                      <option value="18:30">6:30 PM</option>
                      <option value="19:00">7:00 PM (Peak)</option>
                      <option value="19:30">7:30 PM (Peak)</option>
                      <option value="20:00">8:00 PM</option>
                      <option value="20:30">8:30 PM</option>
                      <option value="21:00">9:00 PM</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Guests *
                    </label>
                    <select
                      value={resGuests}
                      onChange={(e) => setResGuests(Number(e.target.value))}
                      className="w-full text-xs p-2.5 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    >
                      {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                        <option key={n} value={n}>
                          {n} {n === 1 ? 'Guest' : 'Guests'}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Your Name *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. John Doe"
                      value={resName}
                      onChange={(e) => setResName(e.target.value)}
                      className="w-full text-xs p-2.5 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      required
                      placeholder="john@example.com"
                      value={resEmail}
                      onChange={(e) => setResEmail(e.target.value)}
                      className="w-full text-xs p-2.5 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      required
                      placeholder="(555) 000-0000"
                      value={resPhone}
                      onChange={(e) => setResPhone(e.target.value)}
                      className="w-full text-xs p-2.5 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity flex items-center justify-center gap-2"
                >
                  <CalendarCheck className="w-4 h-4 text-[#C9A96E]" /> Confirm Table Reservation
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Guest Reviews */}
      <section className="py-20 px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-[#C9A96E] text-xs font-bold uppercase tracking-widest">
            Guest Testimonials
          </span>
          <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#0B0F19] mt-2 mb-3">
            Loved by Epicures & Locals Alike
          </h2>
          <div className="flex items-center justify-center gap-1 text-amber-400">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="w-4 h-4 fill-amber-400" />
            ))}
            <span className="text-stone-700 text-xs font-bold ml-2">4.9 / 5.0 (650+ Verified Reviews)</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-8 rounded-2xl border border-stone-200/80 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex gap-1 text-amber-400 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-3.5 h-3.5 fill-amber-400" />
                ))}
              </div>
              <p className="font-serif italic text-sm text-stone-700 leading-relaxed mb-6">
                “The Tagliatelle al Tartufo is extraordinary. The dining room feels like you were transported to an intimate trattoria in Florence.”
              </p>
            </div>
            <div className="flex items-center gap-3 pt-4 border-t border-stone-100">
              <div className="w-9 h-9 rounded-full bg-stone-200 flex items-center justify-center font-bold text-xs text-stone-700">
                SC
              </div>
              <div>
                <p className="text-xs font-bold text-[#0B0F19]">Sarah Campbell</p>
                <p className="text-[11px] text-stone-400">San Francisco Chronicle Food Enthusiast</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-stone-200/80 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex gap-1 text-amber-400 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-3.5 h-3.5 fill-amber-400" />
                ))}
              </div>
              <p className="font-serif italic text-sm text-stone-700 leading-relaxed mb-6">
                “We order online directly every Friday night. Food always arrives hot, packaging is eco-friendly, and the loyalty points program is a great bonus!”
              </p>
            </div>
            <div className="flex items-center gap-3 pt-4 border-t border-stone-100">
              <div className="w-9 h-9 rounded-full bg-stone-200 flex items-center justify-center font-bold text-xs text-stone-700">
                MR
              </div>
              <div>
                <p className="text-xs font-bold text-[#0B0F19]">Marco Ricci</p>
                <p className="text-[11px] text-stone-400">Regular Takeout Member</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-stone-200/80 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex gap-1 text-amber-400 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-3.5 h-3.5 fill-amber-400" />
                ))}
              </div>
              <p className="font-serif italic text-sm text-stone-700 leading-relaxed mb-6">
                “Hosted our private executive dinner in their cellar room. Unmatched service, world-class Barolo pairing, and genuine warmth.”
              </p>
            </div>
            <div className="flex items-center gap-3 pt-4 border-t border-stone-100">
              <div className="w-9 h-9 rounded-full bg-stone-200 flex items-center justify-center font-bold text-xs text-stone-700">
                JL
              </div>
              <div>
                <p className="text-xs font-bold text-[#0B0F19]">Jonathan Lee</p>
                <p className="text-[11px] text-stone-400">Corporate Host</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
