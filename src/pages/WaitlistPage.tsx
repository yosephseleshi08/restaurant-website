import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Bell, Users, Clock, CheckCircle2, Phone, MessageSquare } from 'lucide-react';

interface WaitlistPageProps {
  onNavigate: (path: string) => void;
}

export const WaitlistPage: React.FC<WaitlistPageProps> = ({ onNavigate }) => {
  const { waitlist, joinWaitlist, settings } = useApp();

  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [guests, setGuests] = useState(2);
  const [joinedEntry, setJoinedEntry] = useState<any | null>(null);

  const activeWaiting = waitlist.filter((w) => w.status === 'waiting' || w.status === 'notified');
  const estimatedWait = Math.max(10, activeWaiting.length * 8 + 5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !phone) return;
    const entry = joinWaitlist(name, phone, Number(guests));
    setJoinedEntry(entry);
    setName('');
    setPhone('');
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Header */}
      <section className="bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white py-16 px-4 text-center">
        <div className="max-w-2xl mx-auto space-y-3">
          <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
            Live Host Stand
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-white">
            Join the Smart Waitlist
          </h1>
          <p className="text-stone-300 text-sm font-light">
            No pager or app required. We will send an SMS to your phone as soon as your table is ready.
          </p>
        </div>
      </section>

      <div className="max-w-xl mx-auto px-4 pt-10">
        {/* Current Wait Time Banner */}
        <div className="bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white rounded-3xl p-6 sm:p-8 text-center shadow-xl mb-8 border border-white/10">
          <p className="text-xs font-bold uppercase tracking-widest text-[#C9A96E]">
            Current Estimated Wait Time
          </p>
          <div className="flex items-center justify-center gap-2 my-2">
            <Clock className="w-8 h-8 text-[#C9A96E]" />
            <span className="font-serif text-5xl font-extrabold text-white">
              ~{estimatedWait} min
            </span>
          </div>
          <p className="text-xs text-stone-300">
            {activeWaiting.length} {activeWaiting.length === 1 ? 'party' : 'parties'} currently in the queue
          </p>
        </div>

        {joinedEntry ? (
          <div className="bg-white rounded-3xl p-8 border border-stone-200 shadow-xl text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="font-serif text-2xl font-bold text-stone-900">
              You're on the list, {joinedEntry.name}!
            </h2>
            <p className="text-xs text-stone-600 leading-relaxed">
              We've registered your party of <strong>{joinedEntry.guests}</strong>. You'll receive a text message at <strong>{joinedEntry.phone}</strong> when your host is preparing your table.
            </p>
            <div className="bg-stone-50 p-4 rounded-2xl text-xs text-stone-500 flex items-center justify-center gap-2">
              <MessageSquare className="w-4 h-4 text-[#C9A96E]" />
              <span>Feel free to grab a drink at our lounge while you wait.</span>
            </div>
            <button
              onClick={() => setJoinedEntry(null)}
              className="py-3 px-6 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-800 text-xs font-bold uppercase"
            >
              Add Another Party
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-stone-200/80 shadow-md">
            <h3 className="font-serif text-xl font-bold text-[#0B0F19] mb-1">
              Add Your Name
            </h3>
            <p className="text-xs text-stone-500 mb-6">
              Enter your mobile number to get automatic table notifications.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Mobile Phone *
                  </label>
                  <input
                    type="tel"
                    required
                    placeholder="(555) 123-4567"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Party Size *
                  </label>
                  <select
                    value={guests}
                    onChange={(e) => setGuests(Number(e.target.value))}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                      <option key={n} value={n}>
                        {n} {n === 1 ? 'Guest' : 'Guests'}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity flex items-center justify-center gap-2 shadow-lg"
              >
                <Bell className="w-4 h-4 text-[#C9A96E]" /> Join Live Waitlist
              </button>

              <p className="text-[11px] text-stone-400 text-center">
                Standard messaging rates apply. You can reply STOP at any time.
              </p>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};
