import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { UPCOMING_EVENTS } from '../data/initialData';
import { Wine, Utensils, Sparkles, Calendar, Mail, CheckCircle2 } from 'lucide-react';

interface EventsPageProps {
  onNavigate: (path: string) => void;
}

export const EventsPage: React.FC<EventsPageProps> = ({ onNavigate }) => {
  const [inquiryName, setInquiryName] = useState('');
  const [inquiryEmail, setInquiryEmail] = useState('');
  const [inquiryDate, setInquiryDate] = useState('');
  const [inquiryGuests, setInquiryGuests] = useState('20');
  const [inquirySubmitted, setInquirySubmitted] = useState(false);

  const services = [
    {
      icon: Utensils,
      title: 'Corporate Executive Dinners',
      desc: 'Discreet, high-touch private boardroom banquets with bespoke 4-course menus and audio-visual capability.',
    },
    {
      icon: Wine,
      title: 'Sommelier Wine Tastings',
      desc: 'Guided vintage pairings exploring Barolo, Brunello, and Super Tuscans with artisan cured salumi & cheeses.',
    },
    {
      icon: Sparkles,
      title: 'Weddings & Celebrations',
      desc: 'Exclusive full-buyouts or terrace cocktail parties holding up to 80 guests with personalized floral and pastry service.',
    },
  ];

  const handleInquiry = (e: React.FormEvent) => {
    e.preventDefault();
    setInquirySubmitted(true);
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Hero */}
      <section className="relative py-20 bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white text-center px-4 overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-25"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=1920&h=800&fit=crop')",
          }}
        />
        <div className="relative z-10 max-w-3xl mx-auto space-y-3">
          <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
            Private Gastronomy
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-white">
            Events & Private Dining
          </h1>
          <p className="text-stone-300 text-sm font-light leading-relaxed">
            From intimate anniversaries to unforgettable corporate galas, host your event with authentic Tuscan warmth.
          </p>
        </div>
      </section>

      {/* Services Grid */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="font-serif text-3xl font-bold text-[#0B0F19]">
            Private Dining Formats
          </h2>
          <p className="text-stone-500 text-xs mt-1">
            Customizable formats with dedicated service staff and custom menus.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
          {services.map((s, idx) => {
            const Icon = s.icon;
            return (
              <div
                key={idx}
                className="bg-white p-8 rounded-3xl border border-stone-200/80 shadow-sm text-center space-y-4"
              >
                <div className="w-14 h-14 rounded-2xl bg-stone-100 text-[#C9A96E] flex items-center justify-center mx-auto">
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="font-serif text-xl font-bold text-[#0B0F19]">{s.title}</h3>
                <p className="text-xs text-stone-500 leading-relaxed">{s.desc}</p>
              </div>
            );
          })}
        </div>

        {/* Upcoming Public Events */}
        <div className="space-y-8 mb-20">
          <div className="text-center">
            <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
              Calendar of Culinary Evenings
            </span>
            <h2 className="font-serif text-3xl font-bold text-[#0B0F19] mt-1">
              Upcoming Special Events
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {UPCOMING_EVENTS.map((ev) => (
              <div
                key={ev.id}
                className="bg-white rounded-3xl overflow-hidden border border-stone-200/80 shadow-sm flex flex-col group"
              >
                <div className="h-48 overflow-hidden relative">
                  <img
                    src={ev.image}
                    alt={ev.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 right-3 bg-stone-900/90 text-amber-300 font-bold px-3 py-1 rounded-full text-xs">
                    {ev.price}
                  </div>
                </div>
                <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex items-center gap-2 text-xs font-semibold text-[#C9A96E] mb-2">
                      <Calendar className="w-4 h-4" /> {ev.date}
                    </div>
                    <h3 className="font-serif text-lg font-bold text-[#0B0F19] mb-2">
                      {ev.title}
                    </h3>
                    <p className="text-xs text-stone-500 leading-relaxed">{ev.description}</p>
                  </div>
                  <button
                    onClick={() => onNavigate('/reservations')}
                    className="w-full py-2.5 rounded-xl bg-stone-100 hover:bg-[#0B0F19] text-stone-800 hover:text-white text-xs font-bold uppercase transition-colors"
                  >
                    Reserve Seats
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Private Dining Inquiry Form */}
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-3xl border border-stone-200/80 shadow-lg">
          <h3 className="font-serif text-2xl font-bold text-[#0B0F19] mb-1 text-center">
            Inquire About Private Dining
          </h3>
          <p className="text-xs text-stone-500 text-center mb-6">
            Our private event director will respond within 24 hours with floor layouts and pricing.
          </p>

          {inquirySubmitted ? (
            <div className="bg-emerald-50 text-emerald-800 p-6 rounded-2xl text-center space-y-2 border border-emerald-200">
              <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
              <p className="font-bold text-sm">Thank you, {inquiryName}!</p>
              <p className="text-xs">
                Your private event inquiry has been logged. Our banquet director will be in touch shortly.
              </p>
            </div>
          ) : (
            <form onSubmit={handleInquiry} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Your Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="John Doe"
                    value={inquiryName}
                    onChange={(e) => setInquiryName(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
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
                    value={inquiryEmail}
                    onChange={(e) => setInquiryEmail(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Estimated Date
                  </label>
                  <input
                    type="date"
                    required
                    value={inquiryDate}
                    onChange={(e) => setInquiryDate(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Estimated Guest Count
                  </label>
                  <select
                    value={inquiryGuests}
                    onChange={(e) => setInquiryGuests(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  >
                    <option value="10-20">10 – 20 Guests</option>
                    <option value="20-40">20 – 40 Guests</option>
                    <option value="40-80">40 – 80 Guests (Full Buyout)</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity"
              >
                Submit Event Inquiry
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
