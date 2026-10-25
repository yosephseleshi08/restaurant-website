import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { ShoppingBag, Plus, Minus, ArrowRight, ShieldCheck, Check } from 'lucide-react';

interface OrderPageProps {
  onNavigate: (path: string) => void;
}

export const OrderPage: React.FC<OrderPageProps> = ({ onNavigate }) => {
  const { menu, addToCart, cart, cartCount, cartSubtotal } = useApp();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (name: string) => {
    setToastMessage(`${name} added to cart!`);
    setTimeout(() => setToastMessage(null), 2500);
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-28">
      {/* Hero */}
      <section className="bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white py-14 px-4 text-center">
        <div className="max-w-4xl mx-auto space-y-3">
          <span className="text-amber-300 font-bold uppercase tracking-widest text-xs">
            0% Commission Direct Kitchen Order
          </span>
          <h1 className="font-serif text-3xl sm:text-5xl font-bold tracking-tight text-white">
            Order Online from La Bella Cucina
          </h1>
          <p className="text-stone-300 text-sm max-w-xl mx-auto">
            Skip the delivery app markups. Freshly made pasta and wood-fired mains prepared by our culinary team.
          </p>
        </div>
      </section>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-24 right-6 z-50 bg-[#0B0F19] text-white px-5 py-3 rounded-2xl shadow-2xl flex items-center gap-3 border border-[#C9A96E]/50 animate-bounce">
          <Check className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold">{toastMessage}</span>
        </div>
      )}

      {/* Main Content Layout */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Menu Items List (Col 8) */}
          <div className="lg:col-span-8 space-y-8">
            {/* Category Pills */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition-colors ${
                  selectedCategory === 'all'
                    ? 'bg-[#0B0F19] text-white'
                    : 'bg-white text-stone-700 border border-stone-200 hover:bg-stone-100'
                }`}
              >
                All Categories
              </button>
              {Object.keys(menu).map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-full text-xs font-semibold capitalize whitespace-nowrap transition-colors ${
                    selectedCategory === cat
                      ? 'bg-[#0B0F19] text-white'
                      : 'bg-white text-stone-700 border border-stone-200 hover:bg-stone-100'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Render categories */}
            {Object.entries(menu)
              .filter(([cat]) => selectedCategory === 'all' || selectedCategory === cat)
              .map(([cat, items]) => (
                <div key={cat} className="space-y-4">
                  <h2 className="font-serif text-2xl font-bold text-[#0B0F19] capitalize border-b border-stone-200 pb-2">
                    {cat}
                  </h2>
                  <div className="space-y-4">
                    {items.map((item) => {
                      const inCart = cart.find((c) => c.id === item.id);
                      return (
                        <div
                          key={item.id}
                          className="bg-white p-4 sm:p-5 rounded-2xl border border-stone-200/80 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                        >
                          <div className="flex gap-4 items-center flex-1">
                            <img
                              src={item.image}
                              alt={item.name}
                              className="w-20 h-20 rounded-xl object-cover shrink-0"
                              loading="lazy"
                            />
                            <div className="space-y-1">
                              <div className="flex items-center gap-2 flex-wrap">
                                <h3 className="font-serif text-base sm:text-lg font-bold text-[#0B0F19]">
                                  {item.name}
                                </h3>
                                {item.popular && (
                                  <span className="text-[10px] font-bold bg-[#C9A96E]/20 text-stone-900 px-2 py-0.5 rounded-full">
                                    Popular
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-stone-500 line-clamp-2">
                                {item.description}
                              </p>
                              <div className="flex items-center gap-2 pt-1">
                                <span className="font-bold text-sm text-[#0B0F19]">
                                  ${item.price.toFixed(2)}
                                </span>
                                {item.dietary.map((d) => (
                                  <span
                                    key={d}
                                    className="text-[10px] bg-stone-100 text-stone-600 px-2 py-0.5 rounded"
                                  >
                                    {d}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>

                          <div className="shrink-0 w-full sm:w-auto flex sm:flex-col items-center justify-end">
                            <button
                              onClick={() => {
                                addToCart(item, 1);
                                showToast(item.name);
                              }}
                              className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-[#0B0F19] hover:bg-[#1e293b] text-white text-xs font-semibold flex items-center justify-center gap-1.5 shadow-sm transition-colors"
                            >
                              <Plus className="w-3.5 h-3.5" />
                              <span>{inCart ? `Add More (${inCart.quantity})` : 'Add to Cart'}</span>
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
          </div>

          {/* Cart Sidebar Summary (Col 4) */}
          <div className="lg:col-span-4 sticky top-28 space-y-4">
            <div className="bg-white rounded-3xl p-6 border border-stone-200/80 shadow-lg">
              <div className="flex items-center justify-between pb-4 border-b border-stone-100">
                <h3 className="font-serif text-lg font-bold text-[#0B0F19] flex items-center gap-2">
                  <ShoppingBag className="w-5 h-5 text-[#C9A96E]" /> Your Order Summary
                </h3>
                <span className="text-xs font-bold bg-stone-100 px-2.5 py-1 rounded-full text-stone-700">
                  {cartCount} items
                </span>
              </div>

              {cart.length === 0 ? (
                <div className="py-12 text-center text-stone-400 space-y-3">
                  <ShoppingBag className="w-12 h-12 mx-auto stroke-1" />
                  <p className="text-xs font-medium">Your shopping bag is currently empty.</p>
                  <p className="text-[11px] text-stone-400">
                    Select your favorite items from the menu to build your feast.
                  </p>
                </div>
              ) : (
                <div className="space-y-4 pt-4">
                  <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                    {cart.map((item) => (
                      <div key={item.id} className="flex items-center justify-between text-xs py-1 border-b border-stone-50">
                        <div className="flex-1 pr-2">
                          <p className="font-bold text-stone-900">{item.name}</p>
                          <p className="text-stone-400">
                            {item.quantity} × ${item.price.toFixed(2)}
                          </p>
                        </div>
                        <span className="font-bold text-stone-900">
                          ${(item.price * item.quantity).toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="pt-3 border-t border-stone-200 space-y-1.5 text-xs text-stone-600">
                    <div className="flex justify-between">
                      <span>Subtotal</span>
                      <span className="font-semibold text-stone-900">${cartSubtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Estimated Tax (8.25%)</span>
                      <span className="font-semibold text-stone-900">
                        ${(cartSubtotal * 0.0825).toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-stone-100 text-sm font-bold text-stone-900">
                      <span>Estimated Total</span>
                      <span className="text-base text-[#0B0F19]">
                        ${(cartSubtotal * 1.0825).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => onNavigate('/cart')}
                    className="w-full mt-4 py-3.5 rounded-2xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity flex items-center justify-center gap-2 shadow-md"
                  >
                    <span>Proceed to Checkout</span>
                    <ArrowRight className="w-4 h-4 text-[#C9A96E]" />
                  </button>
                </div>
              )}
            </div>

            <div className="bg-emerald-50 rounded-2xl p-4 border border-emerald-200/80 text-emerald-800 text-xs flex items-center gap-3">
              <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>
                Earn 1 loyalty point per $1 spent! Free delivery on orders over $60.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
