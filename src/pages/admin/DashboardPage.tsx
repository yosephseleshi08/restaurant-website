import React from 'react';
import { useApp } from '../../context/AppContext';
import {
  Flame,
  Grid,
  CalendarCheck,
  ShoppingBag,
  Users,
  MessageSquare,
  Gift,
  Settings,
  DollarSign,
  Star,
  FileDown,
  TrendingUp
} from 'lucide-react';

interface DashboardProps {
  onNavigate: (path: string) => void;
}

export const DashboardPage: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { currentUser, orders, reservations, waitlist, loyaltyMembers, messages, exportCSV } = useApp();

  const activeOrders = orders.filter((o) => o.status !== 'completed' && o.status !== 'cancelled');
  const todayReservations = reservations.filter((r) => r.status !== 'cancelled');
  const totalRevenue = orders
    .filter((o) => o.status !== 'cancelled')
    .reduce((sum, o) => sum + o.total, 0);

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Header */}
      <div className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <span className="text-xs uppercase font-bold tracking-widest text-[#C9A96E]">
              Command Center
            </span>
            <h1 className="font-serif text-3xl font-bold text-[#0B0F19]">
              Welcome back, {currentUser?.username || 'Admin'}
            </h1>
            <p className="text-xs text-stone-500 mt-1">
              Live operational overview of kitchen orders, table capacity, and revenues.
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => onNavigate('/kitchen')}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs uppercase shadow-sm transition-colors"
            >
              <Flame className="w-4 h-4" /> Open KDS Screen
            </button>
            <button
              onClick={() => exportCSV('orders')}
              className="inline-flex items-center gap-1.5 px-3 py-2.5 rounded-xl border border-stone-200 bg-white hover:bg-stone-50 text-stone-700 text-xs font-semibold"
            >
              <FileDown className="w-4 h-4 text-stone-500" /> Export Orders
            </button>
            <button
              onClick={() => exportCSV('reservations')}
              className="inline-flex items-center gap-1.5 px-3 py-2.5 rounded-xl border border-stone-200 bg-white hover:bg-stone-50 text-stone-700 text-xs font-semibold"
            >
              <FileDown className="w-4 h-4 text-stone-500" /> Export Bookings
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        {/* KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs uppercase font-bold text-stone-600">Total Bookings</p>
              <h3 className="font-serif text-3xl font-bold text-[#0B0F19] mt-1">
                {reservations.length}
              </h3>
              <p className="text-[11px] text-emerald-600 font-semibold mt-1 flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5" /> +18% this week
              </p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-stone-100 text-[#0B0F19] flex items-center justify-center">
              <CalendarCheck className="w-6 h-6 text-[#C9A96E]" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs uppercase font-bold text-stone-600">Active Kitchen Orders</p>
              <h3 className="font-serif text-3xl font-bold text-[#0B0F19] mt-1">
                {activeOrders.length}
              </h3>
              <p className="text-[11px] text-amber-600 font-semibold mt-1">
                Ready for preparation
              </p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Flame className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs uppercase font-bold text-stone-600">Total Revenue</p>
              <h3 className="font-serif text-3xl font-bold text-[#0B0F19] mt-1">
                ${(totalRevenue / 1000).toFixed(1)}k
              </h3>
              <p className="text-[11px] text-emerald-600 font-semibold mt-1 flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5" /> 100% direct (0% cut)
              </p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <DollarSign className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs uppercase font-bold text-stone-600">Customer Rating</p>
              <h3 className="font-serif text-3xl font-bold text-[#0B0F19] mt-1 flex items-center gap-1">
                4.9 <Star className="w-5 h-5 fill-amber-400 text-amber-400" />
              </h3>
              <p className="text-[11px] text-stone-400 mt-1">Based on 650+ diners</p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-stone-100 text-[#0B0F19] flex items-center justify-center">
              <Star className="w-6 h-6 text-[#C9A96E]" />
            </div>
          </div>
        </div>

        {/* Quick Launchpad Grid */}
        <div className="space-y-4">
          <h2 className="font-serif text-2xl font-bold text-[#0B0F19]">
            Operational Tools
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <button
              onClick={() => onNavigate('/kitchen')}
              className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md hover:border-amber-400 text-left transition-all group flex flex-col justify-between"
            >
              <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Flame className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-stone-900 group-hover:text-amber-600 transition-colors">
                  Kitchen Display (KDS)
                </h4>
                <p className="text-xs text-stone-500 mt-1">
                  Live order cards, item counts, and status changes for chefs.
                </p>
              </div>
            </button>

            <button
              onClick={() => onNavigate('/admin/tables')}
              className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md hover:border-blue-400 text-left transition-all group flex flex-col justify-between"
            >
              <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Grid className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-stone-900 group-hover:text-blue-600 transition-colors">
                  Floor Plan & Tables
                </h4>
                <p className="text-xs text-stone-500 mt-1">
                  Drag-and-drop table layouts and real-time seating statuses.
                </p>
              </div>
            </button>

            <button
              onClick={() => onNavigate('/admin/reservations')}
              className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md hover:border-emerald-400 text-left transition-all group flex flex-col justify-between"
            >
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <CalendarCheck className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-stone-900 group-hover:text-emerald-600 transition-colors">
                  Reservations Admin
                </h4>
                <p className="text-xs text-stone-500 mt-1">
                  Filter upcoming bookings, seat guests, and audit capacity.
                </p>
              </div>
            </button>

            <button
              onClick={() => onNavigate('/admin/orders')}
              className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md hover:border-purple-400 text-left transition-all group flex flex-col justify-between"
            >
              <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <ShoppingBag className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-stone-900 group-hover:text-purple-600 transition-colors">
                  Orders Manager
                </h4>
                <p className="text-xs text-stone-500 mt-1">
                  Online delivery, takeout tickets, and item details.
                </p>
              </div>
            </button>

            <button
              onClick={() => onNavigate('/admin/waitlist')}
              className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md hover:border-cyan-400 text-left transition-all group flex flex-col justify-between"
            >
              <div className="w-12 h-12 rounded-2xl bg-cyan-50 text-cyan-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-stone-900 group-hover:text-cyan-600 transition-colors">
                  Smart SMS Waitlist
                </h4>
                <p className="text-xs text-stone-500 mt-1">
                  Manage walk-in queue and dispatch SMS table alerts.
                </p>
              </div>
            </button>

            <button
              onClick={() => onNavigate('/admin/customers')}
              className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md hover:border-amber-400 text-left transition-all group flex flex-col justify-between"
            >
              <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-stone-900 group-hover:text-amber-700 transition-colors">
                  Customer Database CRM
                </h4>
                <p className="text-xs text-stone-500 mt-1">
                  Loyalty point balances, favorite dishes, and spend history.
                </p>
              </div>
            </button>

            <button
              onClick={() => onNavigate('/admin/messages')}
              className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md hover:border-rose-400 text-left transition-all group flex flex-col justify-between"
            >
              <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <MessageSquare className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-stone-900 group-hover:text-rose-600 transition-colors">
                  Inquiries & Messages
                </h4>
                <p className="text-xs text-stone-500 mt-1">
                  Inbox for private events, dietary inquiries, and replies.
                </p>
              </div>
            </button>

            <button
              onClick={() => onNavigate('/editor')}
              className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md hover:border-stone-900 text-left transition-all group flex flex-col justify-between"
            >
              <div className="w-12 h-12 rounded-2xl bg-stone-100 text-stone-800 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Settings className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-stone-900 group-hover:text-[#C9A96E] transition-colors">
                  Visual CMS Editor
                </h4>
                <p className="text-xs text-stone-500 mt-1">
                  Update menu dishes, prices, theme colors, and operating hours.
                </p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
