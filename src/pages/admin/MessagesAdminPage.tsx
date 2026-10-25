import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { MessageSquare, ArrowLeft, Send, Archive, FileDown } from 'lucide-react';

interface MessagesAdminProps {
  onNavigate: (path: string) => void;
}

export const MessagesAdminPage: React.FC<MessagesAdminProps> = ({ onNavigate }) => {
  const { messages, replyMessage, archiveMessage, exportCSV } = useApp();
  const [filter, setFilter] = useState<'all' | 'new' | 'replied' | 'archived'>('all');
  const [replyTextMap, setReplyTextMap] = useState<Record<number, string>>({});

  const filtered = messages.filter((m) => filter === 'all' || m.status === filter);

  const handleSendReply = (id: number) => {
    const text = replyTextMap[id];
    if (!text) return;
    replyMessage(id, text);
    setReplyTextMap((prev) => ({ ...prev, [id]: '' }));
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Header */}
      <div className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate('/dashboard')}
              className="p-2.5 rounded-xl border border-stone-200 hover:bg-stone-50 text-stone-600 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <span className="text-xs uppercase font-bold tracking-widest text-[#C9A96E]">
                Communications
              </span>
              <h1 className="font-serif text-3xl font-bold text-[#0B0F19]">
                Customer Message Inbox
              </h1>
              <p className="text-xs text-stone-500 mt-1">
                Respond to inquiries, private dining quotes, and feedback.
              </p>
            </div>
          </div>

          <button
            onClick={() => exportCSV('messages')}
            className="px-4 py-2.5 rounded-xl bg-stone-900 text-white hover:bg-stone-800 font-bold text-xs uppercase flex items-center gap-2"
          >
            <FileDown className="w-4 h-4 text-[#C9A96E]" /> Export Messages CSV
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-6">
        {/* Filters */}
        <div className="flex items-center gap-2">
          {(['all', 'new', 'replied', 'archived'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition-colors ${
                filter === st
                  ? 'bg-[#0B0F19] text-white'
                  : 'bg-white hover:bg-stone-100 text-stone-700 border border-stone-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        {/* Message Cards */}
        <div className="space-y-4">
          {filtered.length === 0 ? (
            <div className="bg-white rounded-3xl p-12 text-center text-stone-400 space-y-2 border border-stone-200">
              <MessageSquare className="w-12 h-12 mx-auto stroke-1" />
              <p className="font-serif text-lg font-bold text-stone-700">Inbox is Clear</p>
              <p className="text-xs text-stone-500">No messages in this view.</p>
            </div>
          ) : (
            filtered.map((msg) => (
              <div
                key={msg.id}
                className="bg-white rounded-3xl p-6 border border-stone-200 shadow-sm space-y-4"
              >
                <div className="flex justify-between items-start gap-4 pb-3 border-b border-stone-100">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-serif text-base font-bold text-stone-900">
                        {msg.subject.toUpperCase()} — {msg.senderName}
                      </h4>
                      <span
                        className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                          msg.status === 'new'
                            ? 'bg-rose-100 text-rose-800'
                            : msg.status === 'replied'
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-stone-100 text-stone-600'
                        }`}
                      >
                        {msg.status}
                      </span>
                    </div>
                    <p className="text-xs text-stone-500 mt-0.5">
                      {msg.senderEmail} · {new Date(msg.createdAt).toLocaleDateString()}
                    </p>
                  </div>

                  <button
                    onClick={() => archiveMessage(msg.id)}
                    className="p-2 rounded-xl text-stone-400 hover:text-stone-700 hover:bg-stone-100"
                    title="Archive message"
                  >
                    <Archive className="w-4 h-4" />
                  </button>
                </div>

                <p className="text-xs text-stone-700 leading-relaxed bg-stone-50 p-4 rounded-2xl">
                  {msg.messageBody}
                </p>

                {msg.reply && (
                  <div className="p-4 rounded-2xl bg-emerald-50 text-emerald-950 text-xs space-y-1 border border-emerald-100">
                    <p className="font-bold text-emerald-800 flex items-center gap-1">
                      <Send className="w-3.5 h-3.5" /> Your Sent Reply:
                    </p>
                    <p>{msg.reply}</p>
                  </div>
                )}

                {/* Reply Box */}
                <div className="flex gap-2 pt-2">
                  <input
                    type="text"
                    placeholder="Type an instant reply to the customer..."
                    value={replyTextMap[msg.id] || ''}
                    onChange={(e) =>
                      setReplyTextMap((prev) => ({ ...prev, [msg.id]: e.target.value }))
                    }
                    className="flex-1 text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
                  />
                  <button
                    onClick={() => handleSendReply(msg.id)}
                    className="px-5 py-2.5 bg-[#0B0F19] text-white rounded-xl text-xs font-bold uppercase hover:bg-stone-800 flex items-center gap-1.5"
                  >
                    <Send className="w-3.5 h-3.5 text-[#C9A96E]" /> Reply
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
