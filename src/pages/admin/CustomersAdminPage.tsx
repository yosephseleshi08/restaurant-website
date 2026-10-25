import React from 'react';
import { useApp } from '../../context/AppContext';
import { Users, Award, Star, ArrowLeft, Heart, Calendar } from 'lucide-react';

interface CustomersAdminProps {
  onNavigate: (path: string) => void;
}

export const CustomersAdminPage: React.FC<CustomersAdminProps> = ({ onNavigate }) => {
  const { loyaltyMembers } = useApp();

  const totalPoints = loyaltyMembers.reduce((sum, m) => sum + m.points, 0);
  const totalSpend = loyaltyMembers.reduce((sum, m) => sum + m.lifetimeSpend, 0);

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
                Guest Intelligence
              </span>
              <h1 className="font-serif text-3xl font-bold text-[#0B0F19]">
                Customer CRM & Loyalty Database
              </h1>
              <p className="text-xs text-stone-500 mt-1">
                Recognize your regulars, audit lifetime spending, and reward repeat diners.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-3xl border border-stone-200 shadow-sm">
            <p className="text-xs font-bold text-stone-500 uppercase">Total Members</p>
            <h3 className="font-serif text-3xl font-bold text-[#0B0F19] mt-1">
              {loyaltyMembers.length}
            </h3>
            <p className="text-xs text-emerald-600 font-semibold mt-1">100% direct ownership</p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-stone-200 shadow-sm">
            <p className="text-xs font-bold text-stone-500 uppercase">Total Active Points</p>
            <h3 className="font-serif text-3xl font-bold text-amber-600 mt-1">
              {totalPoints} pts
            </h3>
            <p className="text-xs text-stone-400 mt-1">
              ${Math.floor(totalPoints / 100) * 10} in redeemable discount rewards
            </p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-stone-200 shadow-sm">
            <p className="text-xs font-bold text-stone-500 uppercase">Total Member Spend</p>
            <h3 className="font-serif text-3xl font-bold text-emerald-700 mt-1">
              ${totalSpend.toFixed(2)}
            </h3>
            <p className="text-xs text-stone-400 mt-1">
              Avg ${(totalSpend / (loyaltyMembers.length || 1)).toFixed(0)} per regular
            </p>
          </div>
        </div>

        {/* Member Table */}
        <div className="bg-white rounded-3xl border border-stone-200 shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-stone-50 border-b border-stone-200 text-stone-600 font-bold uppercase tracking-wider text-[11px]">
                <th className="py-4 px-6">Customer</th>
                <th className="py-4 px-4">Points</th>
                <th className="py-4 px-4">Lifetime Spend</th>
                <th className="py-4 px-4">Visits</th>
                <th className="py-4 px-6">Favorite Dish</th>
                <th className="py-4 px-6">Last Visit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {loyaltyMembers.map((member) => (
                <tr key={member.id} className="hover:bg-stone-50/80 transition-colors">
                  <td className="py-4 px-6">
                    <p className="font-bold text-stone-900">{member.name}</p>
                    <p className="text-stone-500">{member.email}</p>
                    <p className="text-stone-400 text-[11px]">{member.phone}</p>
                  </td>
                  <td className="py-4 px-4 font-bold text-sm text-[#C9A96E]">
                    {member.points}
                  </td>
                  <td className="py-4 px-4 font-bold text-stone-900">
                    ${member.lifetimeSpend.toFixed(2)}
                  </td>
                  <td className="py-4 px-4 font-semibold text-stone-700">
                    {member.visits} visits
                  </td>
                  <td className="py-4 px-6 text-stone-600 italic">
                    {member.favoriteDish || '—'}
                  </td>
                  <td className="py-4 px-6 text-stone-500 font-mono text-[11px]">
                    {member.lastVisit || 'First visit'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
