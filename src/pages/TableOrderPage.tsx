import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Utensils, Plus, Check, ShoppingBag, ArrowRight } from 'lucide-react';

interface TableOrderPageProps {
  tableNumber: string | number;
  onNavigate: (path: string) => void;
}

export const TableOrderPage: React.FC<TableOrderPageProps> = ({ tableNumber, onNavigate }) => {
  const { menu, addToCart, cart, cartCount, cartSubtotal, placeOrder } = useApp();
  const [toastItem, setToastItem] = useState<string | null>(null);
  const [orderSent, setOrderSent] = useState(false);

  const handleAdd = (item: any) => {
    addToCart(item, 1, `Dine-in Table ${tableNumber}`);
    setToastItem(item.name);
    setTimeout(() => setToastItem(null), 2500);
  };

  const handleSendToKitchen = () => {
    if (cart.length === 0) return;
    placeOrder({
      customerName: `Table ${tableNumber} Guest`,
      customerEmail: `table${tableNumber}@dining.local`,
      customerPhone: '555-000-0000',
      orderType: 'dine-in',
      tableNumber: tableNumber,
      notes: `Direct QR order from Table ${tableNumber}`,
    });
    setOrderSent(true);
  };

  if (orderSent) {
    return (
      <div className="min-h-screen bg-[#FAFAF9] py-16 px-4">
        <div className="max-w-md mx-auto bg-white rounded-3xl p-8 border border-stone-200 text-center space-y-5 shadow-xl">
          <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto text-2xl font-bold">
            ✓
          </div>
          <h2 className="font-serif text-3xl font-bold text-stone-900">
            Order Sent to Kitchen!
          </h2>
          <p className="text-xs text-stone-600 leading-relaxed">
            Your dishes are now firing for <strong>Table {tableNumber}</strong>. Your server will deliver each item as it is plated fresh.
          </p>
          <div className="pt-2 flex flex-col gap-2">
            <button
              onClick={() => onNavigate('/kitchen')}
              className="py-3 rounded-xl bg-amber-50 hover:bg-amber-100 text-[#0B0F19] border border-amber-200 text-xs font-bold uppercase"
            >
              🔥 View on Kitchen Screen (Staff View)
            </button>
            <button
              onClick={() => setOrderSent(false)}
              className="py-3 rounded-xl bg-[#0B0F19] text-white text-xs font-bold uppercase"
            >
              Order More Drinks or Desserts
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-32">
      {/* Table Banner */}
      <section className="bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white py-10 px-4 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#C9A96E]/20 text-[#C9A96E] text-xs font-bold uppercase tracking-wider mb-2">
          <Utensils className="w-3.5 h-3.5" /> Table Self-Service
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-white">
          Table {tableNumber} Dine-In Menu
        </h1>
        <p className="text-stone-300 text-xs mt-1">
          Add items to your order ticket. Tap "Send to Kitchen" when you're ready!
        </p>
      </section>

      {/* Added Toast */}
      {toastItem && (
        <div className="fixed top-24 right-6 z-50 bg-[#0B0F19] text-white px-5 py-3 rounded-2xl shadow-2xl flex items-center gap-2 border border-[#C9A96E]">
          <Check className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold">{toastItem} added to Table {tableNumber}!</span>
        </div>
      )}

      {/* Menu Categories */}
      <div className="max-w-4xl mx-auto px-4 pt-8 space-y-10">
        {Object.entries(menu).map(([category, items]) => (
          <div key={category} className="space-y-4">
            <h2 className="font-serif text-2xl font-bold text-[#0B0F19] capitalize border-b border-stone-200 pb-2">
              {category}
            </h2>
            <div className="space-y-3">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="bg-white p-4 rounded-2xl border border-stone-200/80 shadow-sm flex items-center justify-between gap-4"
                >
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-16 h-16 rounded-xl object-cover shrink-0"
                  />
                  <div className="flex-1">
                    <h3 className="font-serif text-base font-bold text-[#0B0F19]">
                      {item.name}
                    </h3>
                    <p className="text-xs text-stone-500 line-clamp-1">{item.description}</p>
                    <span className="font-bold text-xs text-[#0B0F19] mt-1 inline-block">
                      ${item.price.toFixed(2)}
                    </span>
                  </div>
                  <button
                    onClick={() => handleAdd(item)}
                    className="px-4 py-2 rounded-xl bg-stone-100 hover:bg-[#0B0F19] text-stone-800 hover:text-white transition-colors text-xs font-bold flex items-center gap-1 shrink-0"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Sticky Bottom Bar */}
      {cartCount > 0 && (
        <div className="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-stone-200 p-4 shadow-2xl">
          <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
            <div>
              <p className="text-xs text-stone-500">Table {tableNumber} Ticket</p>
              <p className="font-bold text-base text-[#0B0F19]">
                {cartCount} {cartCount === 1 ? 'item' : 'items'} · ${cartSubtotal.toFixed(2)}
              </p>
            </div>
            <button
              onClick={handleSendToKitchen}
              className="px-6 py-3.5 rounded-full bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 shadow-lg flex items-center gap-2"
            >
              <span>Send Directly to Kitchen</span>
              <ArrowRight className="w-4 h-4 text-[#C9A96E]" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
