import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Award, Star, Search, Sparkles, CheckCircle2, Gift, Utensils } from 'lucide-react';

export const LoyaltyPage: React.FC = () => {
  const { enrollLoyalty, checkLoyalty } = useApp();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [birthday, setBirthday] = useState('');
  const [enrolledMember, setEnrolledMember] = useState<any | null>(null);

  // Check points state
  const [lookupEmail, setLookupEmail] = useState('');
  const [lookupResult, setLookupResult] = useState<any | null>(null);
  const [lookupError, setLookupError] = useState<string | null>(null);

  const handleEnroll = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email) return;
    const member = enrollLoyalty(name, email, phone, birthday);
    setEnrolledMember(member);
  };

  const handleLookup = (e: React.FormEvent) => {
    e.preventDefault();
    setLookupError(null);
    setLookupResult(null);

    const mem = checkLoyalty(lookupEmail);
    if (mem) {
      setLookupResult(mem);
    } else {
      setLookupError('No loyalty membership found for that email address. You can join above for free and get 50 bonus points!');
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Hero */}
      <section className="bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white py-16 px-4 text-center">
        <div className="max-w-2xl mx-auto space-y-3">
          <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs flex items-center justify-center gap-1">
            <Star className="w-3.5 h-3.5 fill-[#C9A96E]" /> Guest Privileges
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-white">
            La Bella Rewards Club
          </h1>
          <p className="text-stone-300 text-sm font-light">
            Earn 1 point per $1 spent on every order. Every 100 points converts directly to $10 off your meal.
          </p>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 pt-12 space-y-12">
        {/* Value Prop Banner */}
        <div className="bg-gradient-to-r from-amber-500 to-amber-600 rounded-3xl p-8 text-white shadow-xl flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-center sm:text-left">
            <h3 className="font-serif text-2xl font-bold">
              🌟 Join Today & Receive 50 Bonus Points
            </h3>
            <p className="text-xs text-amber-100 max-w-lg leading-relaxed">
              No cards to carry. Your phone number or email instantly earns points on both takeout and dine-in tables.
            </p>
          </div>
          <div className="shrink-0 bg-white/20 backdrop-blur-md px-5 py-3 rounded-2xl text-center">
            <span className="text-xs uppercase tracking-wider block font-bold text-amber-100">Welcome Gift</span>
            <span className="font-serif text-2xl font-black">50 Points</span>
          </div>
        </div>

        {/* 2-Column: Enroll + Check Points */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          {/* Enroll Card */}
          <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200/80 shadow-md">
            <h3 className="font-serif text-xl font-bold text-[#0B0F19] mb-1 flex items-center gap-2">
              <Award className="w-5 h-5 text-[#C9A96E]" /> Enroll in Rewards
            </h3>
            <p className="text-xs text-stone-500 mb-6">
              Takes 30 seconds. Instant 50 points credited.
            </p>

            {enrolledMember ? (
              <div className="bg-emerald-50 text-emerald-900 p-6 rounded-2xl text-center space-y-3 border border-emerald-200">
                <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
                <h4 className="font-serif text-lg font-bold">Welcome, {enrolledMember.name}!</h4>
                <p className="text-xs">
                  Your account is activated with <strong className="text-sm font-bold">{enrolledMember.points} points</strong>.
                </p>
                <p className="text-[11px] text-emerald-700">
                  Provide your email ({enrolledMember.email}) at checkout to earn on every order.
                </p>
                <button
                  onClick={() => setEnrolledMember(null)}
                  className="mt-2 px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold uppercase"
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleEnroll} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Maria Rossi"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
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
                    placeholder="maria@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    placeholder="(555) 000-0000"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Birthday (for complimentary dessert!)
                  </label>
                  <input
                    type="date"
                    value={birthday}
                    onChange={(e) => setBirthday(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity flex items-center justify-center gap-2 shadow-lg"
                >
                  <Sparkles className="w-4 h-4 text-[#C9A96E]" /> Join & Claim 50 Points
                </button>
              </form>
            )}
          </div>

          {/* Check Points Card */}
          <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200/80 shadow-md space-y-4">
            <h3 className="font-serif text-xl font-bold text-[#0B0F19] mb-1 flex items-center gap-2">
              <Search className="w-5 h-5 text-[#C9A96E]" /> Check Points Balance
            </h3>
            <p className="text-xs text-stone-500 mb-4">
              Enter your email to view your current points and rewards. Try demo: <code className="bg-stone-100 px-1 py-0.5 rounded text-stone-800">sophia.lorenzi@example.com</code>
            </p>

            <form onSubmit={handleLookup} className="space-y-3">
              <input
                type="email"
                required
                placeholder="Enter your registered email"
                value={lookupEmail}
                onChange={(e) => setLookupEmail(e.target.value)}
                className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
              />
              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-800 font-bold text-xs uppercase"
              >
                Look Up My Points
              </button>
            </form>

            {lookupResult && (
              <div className="bg-stone-50 p-5 rounded-2xl border border-stone-200 text-xs space-y-3 mt-4">
                <div className="flex justify-between items-center pb-2 border-b border-stone-200">
                  <span className="font-bold text-stone-900">{lookupResult.name}</span>
                  <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded-full">
                    VIP Member
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-500">Available Points:</span>
                  <span className="font-bold text-lg text-[#C9A96E]">{lookupResult.points} pts</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-500">Redeemable Value:</span>
                  <span className="font-bold text-stone-900">
                    ${Math.floor(lookupResult.points / 100) * 10} OFF
                  </span>
                </div>
                <div className="flex justify-between text-[11px] text-stone-400">
                  <span>Total Visits: {lookupResult.visits}</span>
                  <span>Lifetime Spend: ${lookupResult.lifetimeSpend.toFixed(2)}</span>
                </div>
              </div>
            )}

            {lookupError && (
              <div className="bg-stone-50 text-stone-600 p-4 rounded-xl text-xs mt-3">
                {lookupError}
              </div>
            )}
          </div>
        </div>

        {/* How It Works 3-steps */}
        <div className="bg-white rounded-3xl p-8 border border-stone-200/80 shadow-sm text-center">
          <h3 className="font-serif text-2xl font-bold text-[#0B0F19] mb-8">
            How La Bella Rewards Works
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-full bg-stone-100 text-[#C9A96E] flex items-center justify-center mx-auto">
                <Utensils className="w-6 h-6" />
              </div>
              <h4 className="font-serif text-base font-bold text-stone-900">1. Dine or Order</h4>
              <p className="text-xs text-stone-500 leading-relaxed">
                Order takeout online or dine at any table. Every dollar spent counts.
              </p>
            </div>
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-full bg-stone-100 text-[#C9A96E] flex items-center justify-center mx-auto">
                <Star className="w-6 h-6" />
              </div>
              <h4 className="font-serif text-base font-bold text-stone-900">2. Collect Points</h4>
              <p className="text-xs text-stone-500 leading-relaxed">
                1 point per $1. Track points easily anytime using your email address.
              </p>
            </div>
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-full bg-stone-100 text-[#C9A96E] flex items-center justify-center mx-auto">
                <Gift className="w-6 h-6" />
              </div>
              <h4 className="font-serif text-base font-bold text-stone-900">3. Enjoy Free Dining</h4>
              <p className="text-xs text-stone-500 leading-relaxed">
                100 points = $10 discount directly on your bill. Points never expire.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
