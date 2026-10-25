import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { ShoppingBag, FileDown, ArrowLeft, Search, Check, Clock } from 'lucide-react';
import { OrderStatus } from '../../types';

interface OrdersAdminProps {
  onNavigate: (path: string) => void;
}

export const OrdersAdminPage: React.FC<OrdersAdminProps> = ({ onNavigate }) => {
  const { orders, updateOrderStatus, exportCSV } = useApp();
  const [filter, setFilter] = useState<string>('all');
  const [search, setSearch] = useState('');

  const filtered = orders.filter((o) => {
    const matchStatus = filter === 'all' || o.status === filter;
    const matchSearch =
      o.customerName.toLowerCase().includes(search.toLowerCase()) ||
      o.customerEmail.toLowerCase().includes(search.toLowerCase()) ||
      o.id.toString().includes(search);
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
                Kitchen & Delivery
              </span>
              <h1 className="font-serif text-3xl font-bold text-[#0B0F19]">
                Online Orders Ledger
              </h1>
              <p className="text-xs text-stone-500 mt-1">
                Track takeout, delivery, and QR table dine-in orders with status transitions.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate('/kitchen')}
              className="px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs uppercase"
            >
              🔥 Switch to KDS Screen
            </button>
            <button
              onClick={() => exportCSV('orders')}
              className="px-4 py-2.5 rounded-xl bg-stone-900 text-white hover:bg-stone-800 font-bold text-xs uppercase flex items-center gap-2"
            >
              <FileDown className="w-4 h-4 text-[#C9A96E]" /> Export Orders CSV
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-6">
        {/* Filters */}
        <div className="bg-white p-4 rounded-2xl border border-stone-200 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
            {(['all', 'pending', 'preparing', 'ready', 'completed', 'cancelled'] as const).map((st) => (
              <button
                key={st}
                onClick={() => setFilter(st)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition-colors ${
                  filter === st
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
              placeholder="Search orders..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full text-xs pl-9 pr-3 py-2 rounded-xl border border-stone-300"
            />
          </div>
        </div>

        {/* Orders List Cards */}
        <div className="space-y-4">
          {filtered.map((order) => (
            <div
              key={order.id}
              className="bg-white rounded-3xl p-6 border border-stone-200 shadow-sm space-y-4"
            >
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-3 border-b border-stone-100">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-serif text-lg font-bold text-[#0B0F19]">
                      Order #{order.id} — {order.customerName}
                    </h3>
                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-stone-100 text-stone-700">
                      {order.orderType}
                    </span>
                  </div>
                  <p className="text-xs text-stone-500">
                    {order.customerEmail} · {order.customerPhone} · {new Date(order.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>

                <div className="text-right">
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase ${
                      order.status === 'completed'
                        ? 'bg-emerald-100 text-emerald-800'
                        : order.status === 'ready'
                        ? 'bg-blue-100 text-blue-800'
                        : order.status === 'preparing'
                        ? 'bg-amber-100 text-amber-800'
                        : order.status === 'cancelled'
                        ? 'bg-rose-100 text-rose-800'
                        : 'bg-stone-100 text-stone-800'
                    }`}
                  >
                    {order.status}
                  </span>
                  <p className="font-bold text-lg text-[#0B0F19] mt-1">
                    ${order.total.toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Items Breakdown */}
              <div className="bg-stone-50 p-4 rounded-2xl text-xs space-y-1.5 border border-stone-100">
                {order.items.map((item, idx) => (
                  <div key={idx} className="flex justify-between">
                    <span>
                      <strong className="text-stone-900">{item.quantity}×</strong> {item.name}
                      {item.specialInstructions && (
                        <span className="text-stone-500 italic ml-1">({item.specialInstructions})</span>
                      )}
                    </span>
                    <span className="font-mono">${(item.price * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
                {order.deliveryAddress && (
                  <p className="pt-2 text-[11px] text-stone-500 border-t border-stone-200">
                    📍 Delivery Address: <strong>{order.deliveryAddress}</strong>
                  </p>
                )}
                {order.notes && (
                  <p className="text-[11px] text-amber-800 font-medium">
                    Note: {order.notes}
                  </p>
                )}
              </div>

              {/* Status Action Buttons */}
              <div className="flex gap-2 flex-wrap pt-2">
                {order.status === 'pending' && (
                  <button
                    onClick={() => updateOrderStatus(order.id, 'preparing')}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold uppercase transition-colors"
                  >
                    Mark Preparing
                  </button>
                )}
                {order.status === 'preparing' && (
                  <button
                    onClick={() => updateOrderStatus(order.id, 'ready')}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold uppercase transition-colors"
                  >
                    Mark Ready
                  </button>
                )}
                {order.status === 'ready' && (
                  <button
                    onClick={() => updateOrderStatus(order.id, 'completed')}
                    className="px-4 py-2 bg-stone-800 hover:bg-stone-700 text-white rounded-xl text-xs font-bold uppercase transition-colors"
                  >
                    Complete Order
                  </button>
                )}
                {order.status !== 'completed' && order.status !== 'cancelled' && (
                  <button
                    onClick={() => updateOrderStatus(order.id, 'cancelled')}
                    className="px-4 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-xl text-xs font-bold uppercase transition-colors"
                  >
                    Cancel Order
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
