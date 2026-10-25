import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { Flame, Clock, CheckCircle2, RotateCw, Volume2, VolumeX, AlertTriangle, ArrowLeft } from 'lucide-react';
import { OrderStatus } from '../../types';

interface KitchenPageProps {
  onNavigate: (path: string) => void;
}

export const KitchenPage: React.FC<KitchenPageProps> = ({ onNavigate }) => {
  const { orders, updateOrderStatus } = useApp();
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [filter, setFilter] = useState<'active' | 'all'>('active');

  const activeOrders = orders.filter((o) =>
    filter === 'active' ? o.status !== 'completed' && o.status !== 'cancelled' : true
  );

  const getStatusBorder = (status: OrderStatus) => {
    switch (status) {
      case 'pending':
        return 'border-amber-400 bg-amber-500/10 text-amber-500';
      case 'preparing':
        return 'border-blue-500 bg-blue-500/10 text-blue-400';
      case 'ready':
        return 'border-emerald-500 bg-emerald-500/10 text-emerald-400';
      case 'completed':
        return 'border-stone-600 bg-stone-700/20 text-stone-400';
      default:
        return 'border-stone-500';
    }
  };

  const getElapsedTime = (createdIso: string) => {
    const elapsedMinutes = Math.floor((Date.now() - new Date(createdIso).getTime()) / (60 * 1000));
    return elapsedMinutes < 1 ? 'Just now' : `${elapsedMinutes}m ago`;
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-white p-4 sm:p-6 pb-24">
      {/* KDS Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-white/10 gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('/dashboard')}
            className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <Flame className="w-6 h-6 text-amber-500" />
              <h1 className="font-serif text-2xl sm:text-3xl font-bold text-white">
                Kitchen Display System (KDS)
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Live orders firing directly from online checkout and dine-in tables.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <div className="bg-white/5 p-1 rounded-xl flex items-center text-xs font-semibold">
            <button
              onClick={() => setFilter('active')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                filter === 'active' ? 'bg-amber-500 text-stone-900 font-bold' : 'text-slate-300'
              }`}
            >
              Active ({orders.filter((o) => o.status !== 'completed' && o.status !== 'cancelled').length})
            </button>
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                filter === 'all' ? 'bg-amber-500 text-stone-900 font-bold' : 'text-slate-300'
              }`}
            >
              All Orders ({orders.length})
            </button>
          </div>

          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 transition-colors flex items-center gap-1.5 text-xs font-semibold"
          >
            {soundEnabled ? <Volume2 className="w-4 h-4 text-emerald-400" /> : <VolumeX className="w-4 h-4 text-slate-500" />}
            <span className="hidden sm:inline">Chime</span>
          </button>
        </div>
      </div>

      {/* Orders Grid */}
      <div className="pt-8">
        {activeOrders.length === 0 ? (
          <div className="py-24 text-center text-slate-500 space-y-3">
            <CheckCircle2 className="w-16 h-16 mx-auto stroke-1 text-emerald-500" />
            <h3 className="font-serif text-2xl font-bold text-white">All Caught Up!</h3>
            <p className="text-xs text-slate-400">
              No active tickets currently in the queue. New orders will appear here automatically.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {activeOrders.map((order) => {
              const borderStyle = getStatusBorder(order.status);
              return (
                <div
                  key={order.id}
                  className="bg-[#121826] rounded-3xl overflow-hidden border border-white/10 shadow-xl flex flex-col justify-between"
                >
                  {/* Card Header */}
                  <div className="p-4 bg-white/5 border-b border-white/5 flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-base text-white">
                          #{order.id}
                        </span>
                        <span
                          className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full border ${borderStyle}`}
                        >
                          {order.status}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1">
                        {order.orderType === 'dine-in' ? (
                          <strong className="text-amber-300">DINE-IN (Table {order.tableNumber})</strong>
                        ) : (
                          <strong className="text-white uppercase">{order.orderType}</strong>
                        )}{' '}
                        · {order.customerName}
                      </p>
                    </div>

                    <div className="text-right">
                      <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {getElapsedTime(order.createdAt)}
                      </span>
                    </div>
                  </div>

                  {/* Card Body / Items */}
                  <div className="p-5 flex-1 space-y-3">
                    <div className="space-y-2">
                      {order.items.map((item, idx) => (
                        <div
                          key={idx}
                          className="flex items-start justify-between text-xs pb-2 border-b border-white/5"
                        >
                          <div className="flex items-start gap-2">
                            <span className="w-5 h-5 rounded-md bg-amber-500/20 text-amber-300 font-black text-center leading-5 text-[11px] shrink-0">
                              {item.quantity}×
                            </span>
                            <div>
                              <p className="font-bold text-white">{item.name}</p>
                              {item.specialInstructions && (
                                <p className="text-[10px] text-amber-300 font-medium italic mt-0.5">
                                  Note: {item.specialInstructions}
                                </p>
                              )}
                            </div>
                          </div>
                          <span className="text-slate-400 font-mono text-[11px]">
                            ${(item.price * item.quantity).toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>

                    {order.notes && (
                      <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-xs">
                        <strong>Guest note:</strong> {order.notes}
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="p-3 bg-white/5 border-t border-white/5 flex gap-2">
                    {order.status === 'pending' && (
                      <button
                        onClick={() => updateOrderStatus(order.id, 'preparing')}
                        className="flex-1 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs uppercase transition-colors"
                      >
                        Start Preparing
                      </button>
                    )}
                    {order.status === 'preparing' && (
                      <button
                        onClick={() => updateOrderStatus(order.id, 'ready')}
                        className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase transition-colors"
                      >
                        Mark Ready
                      </button>
                    )}
                    {order.status === 'ready' && (
                      <button
                        onClick={() => updateOrderStatus(order.id, 'completed')}
                        className="flex-1 py-2.5 rounded-xl bg-stone-700 hover:bg-stone-600 text-white font-bold text-xs uppercase transition-colors"
                      >
                        Complete Order
                      </button>
                    )}
                    {order.status !== 'completed' && order.status !== 'cancelled' && (
                      <button
                        onClick={() => updateOrderStatus(order.id, 'cancelled')}
                        className="px-3 py-2.5 rounded-xl bg-white/5 hover:bg-rose-900/50 text-slate-400 hover:text-rose-300 text-xs font-semibold transition-colors"
                        title="Cancel order"
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
