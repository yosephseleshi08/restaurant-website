import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { MapPin, Phone, Mail, Clock, Send, CheckCircle2 } from 'lucide-react';

interface ContactPageProps {
  onNavigate: (path: string) => void;
}

export const ContactPage: React.FC<ContactPageProps> = ({ onNavigate }) => {
  const { settings, sendMessage } = useApp();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('general');
  const [message, setMessage] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !message) return;
    sendMessage(name, email, subject, message);
    setSubmitted(true);
    setName('');
    setEmail('');
    setMessage('');
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Hero */}
      <section className="bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white py-16 px-4 text-center">
        <div className="max-w-2xl mx-auto space-y-3">
          <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
            We'd Love to Hear From You
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-white">
            Get in Touch with Our Team
          </h1>
          <p className="text-stone-300 text-sm font-light">
            Questions regarding private dining, allergies, or wine acquisitions? Reach out anytime.
          </p>
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Info Card (Col 5) */}
          <div className="lg:col-span-5 bg-[#0B0F19] text-white p-8 rounded-3xl space-y-6 shadow-xl">
            <div>
              <span className="text-[#C9A96E] text-xs font-bold uppercase tracking-wider">
                Direct Contact
              </span>
              <h3 className="font-serif text-2xl font-bold mt-1 text-white">
                Location & Information
              </h3>
            </div>

            <div className="space-y-4 text-xs text-stone-300">
              <div className="flex items-start gap-3">
                <MapPin className="w-4 h-4 text-[#C9A96E] shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-white">Restaurant Address</p>
                  <p>{settings.address}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Phone className="w-4 h-4 text-[#C9A96E] shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-white">Phone Inquiries</p>
                  <a href={settings.phoneLink} className="hover:text-amber-300">
                    {settings.phone}
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Mail className="w-4 h-4 text-[#C9A96E] shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-white">Email</p>
                  <a href={`mailto:${settings.email}`} className="hover:text-amber-300">
                    {settings.email}
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-3 pt-2 border-t border-white/10">
                <Clock className="w-4 h-4 text-[#C9A96E] shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-white mb-1">Service Hours</p>
                  {settings.hours.map((h, i) => (
                    <div key={i} className="flex justify-between gap-4 text-[11px] text-stone-400">
                      <span>{h.days}:</span>
                      <span className="text-stone-200">{h.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-white/10">
              <button
                onClick={() => onNavigate('/reservations')}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-[#C9A96E] to-[#b38e55] text-stone-900 font-bold text-xs uppercase tracking-wider"
              >
                Find Us & Book Table
              </button>
            </div>
          </div>

          {/* Form Card (Col 7) */}
          <div className="lg:col-span-7 bg-white p-6 sm:p-8 rounded-3xl border border-stone-200/80 shadow-md">
            <h3 className="font-serif text-2xl font-bold text-[#0B0F19] mb-1">
              Send us a Message
            </h3>
            <p className="text-xs text-stone-500 mb-6">
              Our front desk manager will respond to your message directly.
            </p>

            {submitted ? (
              <div className="bg-emerald-50 text-emerald-800 p-6 rounded-2xl text-center space-y-2 border border-emerald-200">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
                <p className="font-bold text-sm">Message Sent Successfully!</p>
                <p className="text-xs">
                  We've received your note and will get back to your email shortly.
                </p>
                <button
                  onClick={() => setSubmitted(false)}
                  className="mt-3 px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold uppercase"
                >
                  Send Another
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-stone-700 mb-1">
                      Your Name *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. John Doe"
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
                      placeholder="john@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Inquiry Subject *
                  </label>
                  <select
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  >
                    <option value="general">General Dining Inquiry</option>
                    <option value="reservation">Reservation Question</option>
                    <option value="private-event">Private Event & Catering</option>
                    <option value="wine">Wine List & Cellar Inquiries</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">
                    Message *
                  </label>
                  <textarea
                    rows={4}
                    required
                    placeholder="How can we make your visit memorable?..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 transition-opacity flex items-center justify-center gap-2 shadow-lg"
                >
                  <Send className="w-4 h-4 text-[#C9A96E]" /> Send Message
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
