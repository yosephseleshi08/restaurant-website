import React from 'react';
import { useApp } from '../../context/AppContext';
import { Users, Bell, CheckCircle2, ArrowLeft, Clock } from 'lucide-react';

interface WaitlistAdminProps {
  onNavigate: (path: string) => void;
}

export const WaitlistAdminPage: React.FC<WaitlistAdminProps> = ({ onNavigate }) => {
  const { waitlist, notifyWaitlist, seatWaitlist } = useApp();

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Header */}
      <div className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate('/dashboard')}
              className="p-2.5 rounded-xl border border-stone-200 hover:bg-stone-50 text-stone-600 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <span className="text-xs uppercase font-bold tracking-widest text-[#C9A96E]">
                Host Stand Queue
              </span>
              <h1 className="font-serif text-3xl font-bold text-[#0B0F19]">
                Live Walk-in Waitlist
              </h1>
              <p className="text-xs text-stone-500 mt-1">
                Dispatch SMS alerts to guests when their table is ready or mark as seated.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <div className="bg-white rounded-3xl border border-stone-200 shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-stone-50 border-b border-stone-200 text-stone-600 font-bold uppercase tracking-wider text-[11px]">
                <th className="py-4 px-6">Queue #</th>
                <th className="py-4 px-6">Guest Name</th>
                <th className="py-4 px-6">Phone Number</th>
                <th className="py-4 px-4">Party Size</th>
                <th className="py-4 px-4">Wait Time</th>
                <th className="py-4 px-4">Status</th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {waitlist.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-stone-400">
                    No guests currently waiting.
                  </td>
                </tr>
              ) : (
                waitlist.map((entry, idx) => {
                  const elapsedMinutes = Math.floor(
                    (Date.now() - new Date(entry.createdAt).getTime()) / (60 * 1000)
                  );
                  return (
                    <tr key={entry.id} className="hover:bg-stone-50/80 transition-colors">
                      <td className="py-4 px-6 font-bold text-stone-500">#{idx + 1}</td>
                      <td className="py-4 px-6 font-bold text-stone-900">{entry.name}</td>
                      <td className="py-4 px-6 text-stone-600 font-mono">{entry.phone}</td>
                      <td className="py-4 px-4">
                        <span className="px-2 py-0.5 rounded-full bg-stone-100 font-bold">
                          {entry.guests} Guests
                        </span>
                      </td>
                      <td className="py-4 px-4 text-stone-600">
                        {Math.max(1, elapsedMinutes)} min
                      </td>
                      <td className="py-4 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            entry.status === 'seated'
                              ? 'bg-stone-100 text-stone-600'
                              : entry.notified
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {entry.status}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-right space-x-2">
                        {!entry.notified && entry.status === 'waiting' && (
                          <button
                            onClick={() => notifyWaitlist(entry.id)}
                            className="px-3 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs uppercase inline-flex items-center gap-1"
                          >
                            <Bell className="w-3.5 h-3.5" /> Text Guest (SMS)
                          </button>
                        )}
                        {entry.status !== 'seated' && (
                          <button
                            onClick={() => seatWaitlist(entry.id)}
                            className="px-3 py-1.5 rounded-xl bg-stone-900 hover:bg-stone-800 text-white font-bold text-xs uppercase inline-flex items-center gap-1"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" /> Seat Party
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
