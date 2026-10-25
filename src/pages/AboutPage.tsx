import React from 'react';
import { useApp } from '../context/AppContext';
import { Heart, Sparkles, Award, ShieldCheck, CheckCircle2 } from 'lucide-react';

interface AboutPageProps {
  onNavigate: (path: string) => void;
}

export const AboutPage: React.FC<AboutPageProps> = ({ onNavigate }) => {
  const { settings } = useApp();

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Hero */}
      <section className="relative py-24 bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white text-center px-4 overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1920&h=800&fit=crop')",
          }}
        />
        <div className="relative z-10 max-w-3xl mx-auto space-y-4">
          <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
            Our Tuscan Roots
          </span>
          <h1 className="font-serif text-4xl sm:text-6xl font-bold tracking-tight text-white">
            The Story Behind {settings.name}
          </h1>
          <p className="text-stone-300 text-sm sm:text-base font-light leading-relaxed">
            Founded with the belief that true Italian hospitality is built on simple, uncompromised ingredients and the timeless warmth of family.
          </p>
        </div>
      </section>

      {/* Narrative Section */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 space-y-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-5">
            <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
              Handmade Every Morning
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#0B0F19] leading-tight">
              Flour, Water, Egg & Devotion
            </h2>
            <p className="text-stone-600 text-sm leading-relaxed">
              Every morning at 6:00 AM, our pasta sfoglina begins kneading stone-ground semolina flour from Umbria with fresh local organic egg yolks. The result is ribbons of tagliatelle, delicate ravioli, and wide pappardelle with that unmistakable al dente bite found only in the trattorias of Bologna and Florence.
            </p>
            <p className="text-stone-600 text-sm leading-relaxed">
              Our meats are dry-aged in-house for 35 days, then grilled over almond wood and oak embers to capture the smoky essence of Tuscan countryside feasts.
            </p>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-stone-200">
              <div>
                <p className="font-serif text-3xl font-bold text-[#C9A96E]">100%</p>
                <p className="text-xs text-stone-500 font-medium">Daily In-House Pasta</p>
              </div>
              <div>
                <p className="font-serif text-3xl font-bold text-[#C9A96E]">35-Day</p>
                <p className="text-xs text-stone-500 font-medium">Oak-Aged Steaks</p>
              </div>
            </div>
          </div>

          <div className="relative">
            <img
              src="https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=800&auto=format&fit=crop&q=80"
              alt="Making fresh pasta"
              className="rounded-3xl shadow-xl w-full object-cover h-[450px]"
            />
            <div className="absolute -bottom-6 -left-6 bg-white p-6 rounded-2xl shadow-xl border border-stone-100 hidden sm:block max-w-xs">
              <p className="font-serif italic text-xs text-stone-700">
                “Cucina povera isn't about lack — it's about elevating humble, honest ingredients with pure technique.”
              </p>
              <p className="text-[11px] font-bold text-[#0B0F19] mt-2">— Chef Mario Bellini</p>
            </div>
          </div>
        </div>

        {/* Core Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-10">
          <div className="bg-white p-8 rounded-3xl border border-stone-200/80 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-[#C9A96E] flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="font-serif text-lg font-bold text-[#0B0F19]">Farm-to-Table Producers</h3>
            <p className="text-xs text-stone-500 leading-relaxed">
              We partner directly with organic family farms in Sonoma and imported single-estate olive millers in Lucca.
            </p>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-stone-200/80 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="font-serif text-lg font-bold text-[#0B0F19]">Sustainable Dining</h3>
            <p className="text-xs text-stone-500 leading-relaxed">
              100% compostable delivery packaging, zero food waste through whole-animal butchery, and energy-efficient kitchen appliances.
            </p>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-stone-200/80 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Award className="w-6 h-6" />
            </div>
            <h3 className="font-serif text-lg font-bold text-[#0B0F19]">Accolades & Heritage</h3>
            <p className="text-xs text-stone-500 leading-relaxed">
              Awarded "Best New Italian Trattoria" by Bay Area Epicure and certified authentic Italian hospitality by Ospitalità Italiana.
            </p>
          </div>
        </div>

        {/* CTA banner */}
        <div className="bg-[#0B0F19] text-white p-10 rounded-3xl text-center space-y-4 shadow-xl">
          <h3 className="font-serif text-3xl font-bold text-white">Come Dine With Our Family</h3>
          <p className="text-stone-300 text-xs max-w-md mx-auto">
            Experience our candlelit dining room or let us prepare a takeout feast for your family tonight.
          </p>
          <div className="flex justify-center gap-4 pt-2">
            <button
              onClick={() => onNavigate('/reservations')}
              className="px-6 py-3 rounded-full bg-[#C9A96E] text-stone-900 font-bold text-xs uppercase"
            >
              Reserve a Table
            </button>
            <button
              onClick={() => onNavigate('/order')}
              className="px-6 py-3 rounded-full bg-white/10 hover:bg-white text-white hover:text-stone-900 font-semibold text-xs uppercase transition-colors"
            >
              Order Takeout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
