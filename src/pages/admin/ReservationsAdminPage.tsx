import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { CalendarCheck, FileDown, ArrowLeft, Search, Filter } from 'lucide-react';
import { ReservationStatus } from '../../types';

interface ReservationsAdminProps {
  onNavigate: (path: string) => void;
}

export const ReservationsAdminPage: React.FC<ReservationsAdminProps> = ({ onNavigate }) => {
  const { reservations, updateReservationStatus, exportCSV } = useApp();
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [search, setSearch] = useState('');

  const filtered = reservations.filter((r) => {
    const matchStatus = filterStatus === 'all' || r.status === filterStatus;
    const matchSearch =
      r.customerName.toLowerCase().includes(search.toLowerCase()) ||
      r.customerEmail.toLowerCase().includes(search.toLowerCase()) ||
      r.customerPhone.includes(search);
    return matchStatus && matchSearch;
  });

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Header */}
      <div className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate('/dashboard')}
              className="p-2.5 rounded-xl border border-stone-200 hover:bg-stone-50 text-stone-600 transition-colors"
              title="Back to Dashboard"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <span className="text-xs uppercase font-bold tracking-widest text-[#C9A96E]">
                Booking Ledger
              </span>
              <h1 className="font-serif text-3xl font-bold text-[#0B0F19]">
                Reservations Management
              </h1>
              <p className="text-xs text-stone-500 mt-1">
                View upcoming bookings, update guest arrival statuses, or export to CSV.
              </p>
            </div>
          </div>

          <button
            onClick={() => exportCSV('reservations')}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-stone-900 text-white hover:bg-stone-800 text-xs font-bold uppercase transition-colors"
          >
            <FileDown className="w-4 h-4 text-[#C9A96E]" /> Export Reservations CSV
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-6">
        {/* Filters and search */}
        <div className="bg-white p-4 rounded-2xl border border-stone-200 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
            {(['all', 'pending', 'confirmed', 'completed', 'cancelled'] as const).map((st) => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition-colors ${
                  filterStatus === st
                    ? 'bg-[#0B0F19] text-white'
                    : 'bg-stone-100 hover:bg-stone-200 text-stone-700'
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-stone-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by name, email, phone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full text-xs pl-9 pr-3 py-2 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
            />
          </div>
        </div>

        {/* Table list */}
        <div className="bg-white rounded-3xl border border-stone-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-stone-600 font-bold uppercase tracking-wider text-[11px]">
                  <th className="py-4 px-6">Guest Info</th>
                  <th className="py-4 px-4">Date & Time</th>
                  <th className="py-4 px-4">Party Size</th>
                  <th className="py-4 px-4">Current Status</th>
                  <th className="py-4 px-6">Special Notes</th>
                  <th className="py-4 px-6 text-right">Update Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {filtered.map((res) => (
                  <tr key={res.id} className="hover:bg-stone-50/80 transition-colors">
                    <td className="py-4 px-6">
                      <p className="font-bold text-stone-900">{res.customerName}</p>
                      <p className="text-stone-500">{res.customerPhone}</p>
                      <p className="text-stone-400 text-[11px]">{res.customerEmail}</p>
                    </td>

                    <td className="py-4 px-4">
                      <p className="font-bold text-stone-900">{res.date}</p>
                      <p className="text-stone-500">{res.time}</p>
                    </td>

                    <td className="py-4 px-4">
                      <span className="inline-block px-2.5 py-1 rounded-full bg-stone-100 font-bold text-stone-800">
                        {res.partySize} Guests
                      </span>
                    </td>

                    <td className="py-4 px-4">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                          res.status === 'confirmed'
                            ? 'bg-emerald-100 text-emerald-800'
                            : res.status === 'pending'
                            ? 'bg-amber-100 text-amber-800'
                            : res.status === 'completed'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {res.status}
                      </span>
                    </td>

                    <td className="py-4 px-6 max-w-xs text-stone-500 italic">
                      {res.specialRequests || '—'}
                    </td>

                    <td className="py-4 px-6 text-right">
                      <select
                        value={res.status}
                        onChange={(e) => updateReservationStatus(res.id, e.target.value as ReservationStatus)}
                        className="text-xs p-1.5 rounded-lg border border-stone-300 bg-white font-semibold text-stone-700"
                      >
                        <option value="pending">Pending</option>
                        <option value="confirmed">Confirmed</option>
                        <option value="completed">Completed / Seated</option>
                        <option value="cancelled">Cancelled</option>
                        <option value="no-show">No-Show</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
