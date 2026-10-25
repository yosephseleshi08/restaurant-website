import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  ShoppingBag,
  Trash2,
  Plus,
  Minus,
  CheckCircle2,
  Lock,
  ArrowLeft,
  Bike,
  Store,
  Clock,
  Sparkles
} from 'lucide-react';

interface CartPageProps {
  onNavigate: (path: string) => void;
}

export const CartPage: React.FC<CartPageProps> = ({ onNavigate }) => {
  const { cart, cartSubtotal, updateCartQty, removeFromCart, clearCart, placeOrder } = useApp();

  const [orderType, setOrderType] = useState<'pickup' | 'delivery'>('pickup');
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [orderNotes, setOrderNotes] = useState('');
  const [placedOrder, setPlacedOrder] = useState<any | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const tax = Math.round(cartSubtotal * 0.0825 * 100) / 100;
  const deliveryFee = orderType === 'delivery' ? (cartSubtotal >= 60 ? 0 : 3.99) : 0;
  const grandTotal = Math.round((cartSubtotal + tax + deliveryFee) * 100) / 100;

  const handleCheckout = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName || !customerEmail || !customerPhone) return;
    if (orderType === 'delivery' && !deliveryAddress) return;

    setIsSubmitting(true);
    setTimeout(() => {
      const order = placeOrder({
        customerName,
        customerEmail,
        customerPhone,
        orderType,
        deliveryAddress: orderType === 'delivery' ? deliveryAddress : undefined,
        notes: orderNotes,
      });
      setPlacedOrder(order);
      setIsSubmitting(false);
    }, 700);
  };

  if (placedOrder) {
    return (
      <div className="min-h-screen bg-[#FAFAF9] py-16 px-4">
        <div className="max-w-xl mx-auto bg-white rounded-3xl p-8 border border-stone-200/80 shadow-2xl text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-10 h-10" />
          </div>

          <div>
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-600">
              Order Received by Kitchen
            </span>
            <h1 className="font-serif text-3xl font-bold text-[#0B0F19] mt-1">
              Order #{placedOrder.id} Confirmed!
            </h1>
            <p className="text-xs text-stone-500 mt-2">
              Thank you, {placedOrder.customerName}. Your ticket has been sent straight to the chef's display.
            </p>
          </div>

          <div className="bg-stone-50 rounded-2xl p-5 text-left space-y-3 text-xs border border-stone-200/60">
            <div className="flex justify-between font-bold text-stone-800 pb-2 border-b border-stone-200">
              <span>Fulfillment Method:</span>
              <span className="uppercase text-[#C9A96E]">
                {placedOrder.orderType}
              </span>
            </div>
            {placedOrder.deliveryAddress && (
              <div className="flex justify-between text-stone-600">
                <span>Address:</span>
                <span className="text-right font-medium">{placedOrder.deliveryAddress}</span>
              </div>
            )}
            <div className="flex justify-between text-stone-600">
              <span>Estimated Ready Time:</span>
              <span className="font-bold text-stone-900">
                {placedOrder.orderType === 'pickup' ? '~20-25 mins' : '~35-45 mins'}
              </span>
            </div>
            <div className="flex justify-between text-stone-600">
              <span>Total Paid:</span>
              <span className="font-bold text-base text-[#0B0F19]">
                ${placedOrder.total.toFixed(2)}
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <button
              onClick={() => onNavigate('/kitchen')}
              className="flex-1 py-3 rounded-xl bg-amber-50 hover:bg-amber-100 text-[#0B0F19] border border-amber-200 font-bold text-xs uppercase tracking-wider transition-colors"
            >
              🔥 Watch on Kitchen Screen
            </button>
            <button
              onClick={() => onNavigate('/order')}
              className="flex-1 py-3 rounded-xl bg-[#0B0F19] text-white font-bold text-xs uppercase tracking-wider hover:opacity-90 transition-opacity"
            >
              Back to Menu
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-[#FAFAF9] flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-3xl p-8 border border-stone-200 text-center space-y-4 shadow-sm">
          <div className="w-16 h-16 rounded-full bg-stone-100 flex items-center justify-center mx-auto text-stone-400">
            <ShoppingBag className="w-8 h-8" />
          </div>
          <h2 className="font-serif text-2xl font-bold text-stone-800">
            Your Cart is Empty
          </h2>
          <p className="text-xs text-stone-500">
            You haven't added any delicious dishes yet. Explore our freshly made pasta and wood-fired mains!
          </p>
          <button
            onClick={() => onNavigate('/order')}
            className="w-full py-3.5 rounded-full bg-[#0B0F19] text-white font-bold text-xs uppercase tracking-wider hover:bg-[#1e293b] transition-colors"
          >
            Explore Menu & Order
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9] py-12 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <button
          onClick={() => onNavigate('/order')}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-stone-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" /> Continue Ordering
        </button>

        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-[#0B0F19] mb-8">
          Checkout & Order Confirmation
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Cart items list (Col 7) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="bg-white rounded-3xl p-6 border border-stone-200/80 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-stone-100">
                <h2 className="font-serif text-lg font-bold text-[#0B0F19]">
                  Order Items ({cart.length})
                </h2>
                <button
                  onClick={clearCart}
                  className="text-xs text-rose-600 hover:text-rose-700 font-semibold"
                >
                  Clear All
                </button>
              </div>

              <div className="space-y-4">
                {cart.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between gap-4 py-3 border-b border-stone-100 last:border-b-0"
                  >
                    <img
                      src={item.image}
                      alt={item.name}
                      className="w-16 h-16 rounded-xl object-cover shrink-0"
                    />

                    <div className="flex-1">
                      <h4 className="font-serif text-sm font-bold text-stone-900">
                        {item.name}
                      </h4>
                      <p className="text-xs text-stone-500">
                        ${item.price.toFixed(2)} each
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => updateCartQty(item.id, item.quantity - 1)}
                        className="w-7 h-7 rounded-lg bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-700"
                      >
                        <Minus className="w-3.5 h-3.5" />
                      </button>
                      <span className="text-xs font-bold w-5 text-center">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => updateCartQty(item.id, item.quantity + 1)}
                        className="w-7 h-7 rounded-lg bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-700"
                      >
                        <Plus className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => removeFromCart(item.id)}
                        className="text-stone-400 hover:text-rose-500 p-1 ml-1"
                        title="Remove item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <span className="font-bold text-xs text-[#0B0F19] shrink-0 w-16 text-right">
                      ${(item.price * item.quantity).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Loyalty bonus alert */}
            <div className="bg-amber-50/80 border border-amber-200/80 rounded-2xl p-4 text-xs text-amber-900 flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-amber-600 shrink-0" />
              <div>
                <strong>Loyalty Member Reward:</strong> You will earn{' '}
                <span className="font-bold">{Math.floor(cartSubtotal)} points</span> with this
                order!
              </div>
            </div>
          </div>

          {/* Checkout Form (Col 5) */}
          <div className="lg:col-span-5 space-y-6">
            <form
              onSubmit={handleCheckout}
              className="bg-white rounded-3xl p-6 sm:p-8 border border-stone-200/80 shadow-lg space-y-5"
            >
              {/* Pickup vs Delivery Toggle */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-2">
                  Order Type
                </label>
                <div className="grid grid-cols-2 gap-2 bg-stone-100 p-1.5 rounded-2xl">
                  <button
                    type="button"
                    onClick={() => setOrderType('pickup')}
                    className={`py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                      orderType === 'pickup'
                        ? 'bg-white text-stone-900 shadow-sm'
                        : 'text-stone-500 hover:text-stone-900'
                    }`}
                  >
                    <Store className="w-4 h-4" /> Pickup (~20m)
                  </button>
                  <button
                    type="button"
                    onClick={() => setOrderType('delivery')}
                    className={`py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                      orderType === 'delivery'
                        ? 'bg-white text-stone-900 shadow-sm'
                        : 'text-stone-500 hover:text-stone-900'
                    }`}
                  >
                    <Bike className="w-4 h-4" /> Delivery (~35m)
                  </button>
                </div>
              </div>

              {/* Customer Info */}
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Your Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Giulia De Luca"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      required
                      placeholder="giulia@example.com"
                      value={customerEmail}
                      onChange={(e) => setCustomerEmail(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      required
                      placeholder="(555) 000-0000"
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                </div>

                {orderType === 'delivery' && (
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Delivery Address *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="Street address, Apt, Suite, San Francisco, CA"
                      value={deliveryAddress}
                      onChange={(e) => setDeliveryAddress(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Kitchen Notes / Dietary Requests
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Utensils, gate code #1234, dressing on side"
                    value={orderNotes}
                    onChange={(e) => setOrderNotes(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>
              </div>

              {/* Cost Summary Breakdown */}
              <div className="pt-4 border-t border-stone-200 space-y-2 text-xs text-stone-600">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="font-semibold text-stone-900">${cartSubtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Sales Tax (8.25%)</span>
                  <span className="font-semibold text-stone-900">${tax.toFixed(2)}</span>
                </div>
                {orderType === 'delivery' && (
                  <div className="flex justify-between">
                    <span>Delivery Fee</span>
                    <span className="font-semibold text-stone-900">
                      {deliveryFee === 0 ? (
                        <span className="text-emerald-600 font-bold">FREE (Over $60)</span>
                      ) : (
                        `$${deliveryFee.toFixed(2)}`
                      )}
                    </span>
                  </div>
                )}
                <div className="flex justify-between pt-3 border-t border-stone-200 text-sm font-bold text-stone-900">
                  <span>Total Amount</span>
                  <span className="text-lg text-[#0B0F19]">${grandTotal.toFixed(2)}</span>
                </div>
              </div>

              {/* Submit CTA */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity flex items-center justify-center gap-2 shadow-lg"
              >
                {isSubmitting ? (
                  <span className="animate-spin">⏳ Placing Order...</span>
                ) : (
                  <>
                    <Lock className="w-4 h-4 text-[#C9A96E]" /> Place Order (${grandTotal.toFixed(2)})
                  </>
                )}
              </button>

              <p className="text-[11px] text-stone-400 text-center flex items-center justify-center gap-1">
                <Lock className="w-3 h-3" /> Direct 256-bit encrypted checkout. No third-party cuts.
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
