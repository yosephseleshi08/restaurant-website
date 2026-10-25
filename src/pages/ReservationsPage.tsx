import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { CalendarCheck, Clock, Users, PhoneCall, CheckCircle2, AlertCircle, Info } from 'lucide-react';

interface ReservationsPageProps {
  onNavigate: (path: string) => void;
}

export const ReservationsPage: React.FC<ReservationsPageProps> = ({ onNavigate }) => {
  const { settings, addReservation, reservations } = useApp();

  const [date, setDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });
  const [time, setTime] = useState('19:00');
  const [partySize, setPartySize] = useState(2);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [specialRequests, setSpecialRequests] = useState('');

  const [bookingResult, setBookingResult] = useState<{
    success: boolean;
    message: string;
    reservation?: any;
  } | null>(null);

  const timeSlots = [
    '17:00',
    '17:30',
    '18:00',
    '18:30',
    '19:00',
    '19:30',
    '20:00',
    '20:30',
    '21:00',
  ];

  // Calculate booked seats in selected slot
  const currentSlotBooked = reservations
    .filter((r) => r.date === date && r.time === time && r.status !== 'cancelled')
    .reduce((sum, r) => sum + r.partySize, 0);

  const maxCapacity = settings.maxCapacityPerSlot || 28;
  const remainingSeats = Math.max(0, maxCapacity - currentSlotBooked);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !phone) return;

    const res = addReservation({
      customerName: name,
      customerEmail: email,
      customerPhone: phone,
      partySize: Number(partySize),
      date,
      time,
      specialRequests,
    });

    setBookingResult(res);
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Header */}
      <section className="bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white py-16 px-4 text-center">
        <div className="max-w-2xl mx-auto space-y-3">
          <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
            Reserve a Table
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-white">
            Book Your Table Experience
          </h1>
          <p className="text-stone-300 text-sm font-light">
            Indulge in artisanal Tuscan cooking, curated wines, and authentic hospitality.
          </p>
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-12">
        {bookingResult?.success ? (
          <div className="max-w-xl mx-auto bg-white rounded-3xl p-8 border border-stone-200/80 shadow-xl text-center space-y-5">
            <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="font-serif text-3xl font-bold text-stone-900">
              Reservation Confirmed!
            </h2>
            <p className="text-xs text-stone-500">
              We look forward to serving you, {bookingResult.reservation?.customerName}.
            </p>

            <div className="bg-stone-50 rounded-2xl p-6 text-left space-y-2 text-xs border border-stone-200">
              <div className="flex justify-between">
                <span className="text-stone-500">Booking Ref:</span>
                <span className="font-bold text-stone-900">
                  #RES-{bookingResult.reservation?.id}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-stone-500">Date & Time:</span>
                <span className="font-bold text-stone-900">
                  {bookingResult.reservation?.date} at {bookingResult.reservation?.time}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-stone-500">Party Size:</span>
                <span className="font-bold text-stone-900">
                  {bookingResult.reservation?.partySize} Guests
                </span>
              </div>
              {bookingResult.reservation?.specialRequests && (
                <div className="flex justify-between pt-2 border-t border-stone-200">
                  <span className="text-stone-500">Special Notes:</span>
                  <span className="text-right font-medium text-stone-800">
                    {bookingResult.reservation?.specialRequests}
                  </span>
                </div>
              )}
            </div>

            <div className="pt-2 flex gap-3">
              <button
                onClick={() => setBookingResult(null)}
                className="flex-1 py-3 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-800 font-bold text-xs uppercase"
              >
                Make Another Booking
              </button>
              <button
                onClick={() => onNavigate('/menu')}
                className="flex-1 py-3 rounded-xl bg-[#0B0F19] hover:bg-stone-800 text-white font-bold text-xs uppercase"
              >
                View Menu
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Info Column (Col 4) */}
            <div className="lg:col-span-4 bg-[#0B0F19] text-white p-8 rounded-3xl space-y-6 shadow-xl">
              <div>
                <span className="text-[#C9A96E] text-xs font-bold uppercase tracking-wider">
                  Important Info
                </span>
                <h3 className="font-serif text-2xl font-bold mt-1 text-white">
                  Reservation Policies
                </h3>
              </div>

              <div className="space-y-4 text-xs text-stone-300">
                <div className="flex items-start gap-3">
                  <Clock className="w-4 h-4 text-[#C9A96E] shrink-0 mt-0.5" />
                  <p>
                    Tables are held for up to <strong>15 minutes</strong> past your scheduled reservation time before releasing to walk-ins.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <Users className="w-4 h-4 text-[#C9A96E] shrink-0 mt-0.5" />
                  <p>
                    Parties of 8 or more require a credit card authorization and have a 24-hour cancellation window.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <PhoneCall className="w-4 h-4 text-[#C9A96E] shrink-0 mt-0.5" />
                  <p>
                    Need assistance or private dining? Call us directly at{' '}
                    <a href={settings.phoneLink} className="underline text-amber-300">
                      {settings.phone}
                    </a>
                    .
                  </p>
                </div>
              </div>

              <div className="pt-6 border-t border-white/10">
                <p className="text-xs font-semibold text-white mb-2">Dress Code</p>
                <p className="text-[11px] text-stone-400">
                  Smart casual attire requested. No athletic wear or beachwear.
                </p>
              </div>
            </div>

            {/* Right Form Card (Col 8) */}
            <div className="lg:col-span-8 bg-white p-6 sm:p-10 rounded-3xl border border-stone-200/80 shadow-md space-y-6">
              <div>
                <h3 className="font-serif text-2xl font-bold text-[#0B0F19]">
                  Select Date & Time
                </h3>
                <p className="text-xs text-stone-500">
                  All reservations are confirmed instantly with capacity safeguards.
                </p>
              </div>

              {bookingResult && !bookingResult.success && (
                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{bookingResult.message}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Leonardo Donati"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      required
                      placeholder="leonardo@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      required
                      placeholder="(555) 000-0000"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Date *
                    </label>
                    <input
                      type="date"
                      required
                      value={date}
                      onChange={(e) => setDate(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Party Size *
                    </label>
                    <select
                      value={partySize}
                      onChange={(e) => setPartySize(Number(e.target.value))}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    >
                      {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                        <option key={n} value={n}>
                          {n} {n === 1 ? 'Guest' : 'Guests'}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-semibold text-stone-700">
                      Available Time Slots for {date}
                    </label>
                    <span className="text-[11px] text-stone-500 flex items-center gap-1">
                      <Info className="w-3 h-3 text-[#C9A96E]" /> {remainingSeats} seats left for {time}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
                    {timeSlots.map((slot) => {
                      const booked = reservations
                        .filter((r) => r.date === date && r.time === slot && r.status !== 'cancelled')
                        .reduce((sum, r) => sum + r.partySize, 0);
                      const isFull = booked >= maxCapacity;
                      return (
                        <button
                          type="button"
                          key={slot}
                          disabled={isFull}
                          onClick={() => setTime(slot)}
                          className={`py-2.5 px-2 rounded-xl text-xs font-bold transition-all ${
                            time === slot
                              ? 'bg-[#0B0F19] text-white shadow-md'
                              : isFull
                              ? 'bg-stone-100 text-stone-400 cursor-not-allowed line-through'
                              : 'bg-stone-50 hover:bg-stone-100 text-stone-800 border border-stone-200'
                          }`}
                        >
                          {slot}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Special Requests or Dietary Requirements
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Allergies, anniversary celebration, high chair needed, or booth seating preference..."
                    value={specialRequests}
                    onChange={(e) => setSpecialRequests(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-4 rounded-2xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity flex items-center justify-center gap-2 shadow-lg"
                >
                  <CalendarCheck className="w-4 h-4 text-[#C9A96E]" /> Confirm Table Reservation
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
