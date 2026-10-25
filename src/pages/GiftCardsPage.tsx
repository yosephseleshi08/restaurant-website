import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Gift, CreditCard, CheckCircle2, Sparkles, Search, AlertCircle } from 'lucide-react';

export const GiftCardsPage: React.FC = () => {
  const { settings, purchaseGiftCard, checkGiftCard } = useApp();

  const [amount, setAmount] = useState<number>(100);
  const [customAmount, setCustomAmount] = useState<string>('');
  const [recipientName, setRecipientName] = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [purchaserName, setPurchaserName] = useState('');
  const [purchaserEmail, setPurchaserEmail] = useState('');
  const [message, setMessage] = useState('');
  const [createdCard, setCreatedCard] = useState<any | null>(null);

  // Balance checker state
  const [checkCode, setCheckCode] = useState('');
  const [foundCard, setFoundCard] = useState<any | null>(null);
  const [checkError, setCheckError] = useState<string | null>(null);

  const selectedAmount = customAmount ? parseFloat(customAmount) || 0 : amount;

  const handlePurchase = (e: React.FormEvent) => {
    e.preventDefault();
    if (!recipientName || !recipientEmail || !purchaserName || !purchaserEmail) return;

    const newCard = purchaseGiftCard({
      amount: selectedAmount,
      recipientName,
      recipientEmail,
      purchaserName,
      purchaserEmail,
      message,
    });
    setCreatedCard(newCard);
  };

  const handleCheckBalance = (e: React.FormEvent) => {
    e.preventDefault();
    setCheckError(null);
    setFoundCard(null);

    const card = checkGiftCard(checkCode);
    if (card) {
      setFoundCard(card);
    } else {
      setCheckError('No active gift card found matching that code. Please verify your code and try again.');
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Hero */}
      <section className="bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white py-16 px-4 text-center">
        <div className="max-w-2xl mx-auto space-y-3">
          <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
            Timeless Gifts
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-white">
            Digital Gift Cards
          </h1>
          <p className="text-stone-300 text-sm font-light">
            Give the gift of Tuscan dining. Delivered instantly via email with no expiration date.
          </p>
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-12 space-y-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Card Preview & Balance Check (Col 5) */}
          <div className="lg:col-span-5 space-y-6">
            {/* Live Gift Card Preview Graphic */}
            <div className="bg-gradient-to-br from-[#0B0F19] via-[#1a2332] to-[#04060a] p-6 sm:p-8 rounded-3xl text-white shadow-2xl border border-white/10 relative overflow-hidden flex flex-col justify-between min-h-[240px]">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#C9A96E]/10 rounded-full blur-2xl" />

              <div className="flex justify-between items-start relative z-10">
                <div>
                  <h4 className="font-serif text-xl font-bold tracking-tight text-white">
                    {settings.name}
                  </h4>
                  <p className="text-[10px] text-amber-300/80 uppercase tracking-widest">
                    Digital Dining Card
                  </p>
                </div>
                <Sparkles className="w-6 h-6 text-[#C9A96E]" />
              </div>

              <div className="my-6 relative z-10">
                <span className="text-xs text-stone-400">Card Value</span>
                <p className="font-serif text-4xl font-extrabold text-[#C9A96E]">
                  ${selectedAmount.toFixed(2)}
                </p>
              </div>

              <div className="flex justify-between items-end text-xs text-stone-300 relative z-10">
                <div>
                  <p className="text-[10px] text-stone-400">Recipient</p>
                  <p className="font-semibold">{recipientName || 'Your Recipient'}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-stone-400">Code</p>
                  <p className="font-mono text-xs text-amber-300">
                    {createdCard ? createdCard.code : 'BELLA-••••-••••'}
                  </p>
                </div>
              </div>
            </div>

            {/* Check Card Balance Tool */}
            <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm space-y-4">
              <h4 className="font-serif text-lg font-bold text-[#0B0F19] flex items-center gap-2">
                <Search className="w-4 h-4 text-[#C9A96E]" /> Check Gift Card Balance
              </h4>
              <p className="text-xs text-stone-500">
                Try demo code: <code className="bg-stone-100 text-stone-800 px-1 py-0.5 rounded font-mono">BELLA-GOLD-9482</code>
              </p>

              <form onSubmit={handleCheckBalance} className="flex gap-2">
                <input
                  type="text"
                  required
                  placeholder="e.g. BELLA-GOLD-9482"
                  value={checkCode}
                  onChange={(e) => setCheckCode(e.target.value)}
                  className="flex-1 text-xs p-2.5 rounded-xl border border-stone-300 uppercase font-mono"
                />
                <button
                  type="submit"
                  className="px-4 py-2.5 bg-[#0B0F19] text-white rounded-xl text-xs font-semibold hover:bg-stone-800"
                >
                  Check
                </button>
              </form>

              {foundCard && (
                <div className="bg-emerald-50 text-emerald-900 p-4 rounded-2xl text-xs border border-emerald-200 space-y-1">
                  <p className="font-bold">Card Found: {foundCard.code}</p>
                  <p>Remaining Balance: <strong className="text-sm font-bold">${foundCard.balance.toFixed(2)}</strong> (Original: ${foundCard.amount.toFixed(2)})</p>
                  <p className="text-[11px] text-emerald-700">Recipient: {foundCard.recipientName}</p>
                </div>
              )}

              {checkError && (
                <div className="bg-rose-50 text-rose-800 p-3 rounded-xl text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{checkError}</span>
                </div>
              )}
            </div>
          </div>

          {/* Purchase Form (Col 7) */}
          <div className="lg:col-span-7 bg-white p-6 sm:p-8 rounded-3xl border border-stone-200/80 shadow-md">
            {createdCard ? (
              <div className="text-center space-y-5 py-4">
                <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-10 h-10" />
                </div>
                <h3 className="font-serif text-2xl font-bold text-stone-900">
                  Gift Card Issued!
                </h3>
                <p className="text-xs text-stone-500">
                  A digital gift card has been generated for {createdCard.recipientName}.
                </p>
                <div className="bg-stone-50 p-6 rounded-2xl border border-stone-200 text-left space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-stone-500">Redemption Code:</span>
                    <span className="font-mono font-bold text-stone-900 text-sm">
                      {createdCard.code}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-stone-500">Amount:</span>
                    <span className="font-bold text-stone-900">
                      ${createdCard.amount.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-stone-500">Sent To:</span>
                    <span className="font-medium text-stone-800">
                      {createdCard.recipientEmail}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setCreatedCard(null);
                    setRecipientName('');
                    setRecipientEmail('');
                  }}
                  className="py-3 px-6 rounded-xl bg-[#0B0F19] text-white text-xs font-bold uppercase"
                >
                  Buy Another Gift Card
                </button>
              </div>
            ) : (
              <form onSubmit={handlePurchase} className="space-y-6">
                <div>
                  <h3 className="font-serif text-2xl font-bold text-[#0B0F19] mb-1">
                    Select Card Value
                  </h3>
                  <p className="text-xs text-stone-500 mb-4">
                    Choose a preset or enter a custom amount.
                  </p>

                  <div className="grid grid-cols-4 gap-2 mb-3">
                    {[50, 100, 150, 250].map((val) => (
                      <button
                        type="button"
                        key={val}
                        onClick={() => {
                          setAmount(val);
                          setCustomAmount('');
                        }}
                        className={`py-3 rounded-xl text-xs font-bold transition-all ${
                          amount === val && !customAmount
                            ? 'bg-[#0B0F19] text-white shadow-md'
                            : 'bg-stone-100 hover:bg-stone-200 text-stone-800'
                        }`}
                      >
                        ${val}
                      </button>
                    ))}
                  </div>

                  <input
                    type="number"
                    placeholder="Or enter custom amount ($)"
                    value={customAmount}
                    onChange={(e) => setCustomAmount(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>

                <div className="space-y-4 pt-2 border-t border-stone-100">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-stone-700">
                    Recipient Details
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-stone-700 mb-1">
                        Recipient Name *
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Maria Rossi"
                        value={recipientName}
                        onChange={(e) => setRecipientName(e.target.value)}
                        className="w-full text-xs p-3 rounded-xl border border-stone-300"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-stone-700 mb-1">
                        Recipient Email *
                      </label>
                      <input
                        type="email"
                        required
                        placeholder="maria@example.com"
                        value={recipientEmail}
                        onChange={(e) => setRecipientEmail(e.target.value)}
                        className="w-full text-xs p-3 rounded-xl border border-stone-300"
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-4 pt-2 border-t border-stone-100">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-stone-700">
                    Your Information
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-stone-700 mb-1">
                        Your Name *
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Marco Bellini"
                        value={purchaserName}
                        onChange={(e) => setPurchaserName(e.target.value)}
                        className="w-full text-xs p-3 rounded-xl border border-stone-300"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-stone-700 mb-1">
                        Your Email *
                      </label>
                      <input
                        type="email"
                        required
                        placeholder="marco@example.com"
                        value={purchaserEmail}
                        onChange={(e) => setPurchaserEmail(e.target.value)}
                        className="w-full text-xs p-3 rounded-xl border border-stone-300"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Personal Message
                    </label>
                    <textarea
                      rows={3}
                      placeholder="Buon compleanno! Hope you enjoy an amazing dinner..."
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-4 rounded-2xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity flex items-center justify-center gap-2 shadow-lg"
                >
                  <Gift className="w-4 h-4 text-[#C9A96E]" /> Purchase Gift Card (${selectedAmount.toFixed(2)})
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
