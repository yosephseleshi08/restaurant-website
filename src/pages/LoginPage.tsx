import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Shield, Lock, ChefHat, UserCheck, ArrowRight } from 'lucide-react';

interface LoginPageProps {
  onNavigate: (path: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onNavigate }) => {
  const { login } = useApp();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(username, 'admin');
    onNavigate('/dashboard');
  };

  const handleQuickRole = (user: string, role: 'admin' | 'manager' | 'staff', targetPath: string) => {
    login(user, role);
    onNavigate(targetPath);
  };

  return (
    <div className="min-h-[85vh] bg-[#FAFAF9] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl p-8 border border-stone-200/80 shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-[#0B0F19] text-[#C9A96E] flex items-center justify-center mx-auto shadow-md">
            <Shield className="w-7 h-7" />
          </div>
          <h2 className="font-serif text-2xl sm:text-3xl font-bold text-[#0B0F19]">
            Staff & Admin Portal
          </h2>
          <p className="text-xs text-stone-500">
            Sign in to manage kitchen orders, table floor plans, and restaurant settings.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-stone-700 mb-1">
              Username
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-700 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full text-xs p-3 rounded-xl border border-stone-300 focus:outline-none focus:border-[#C9A96E]"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#0B0F19] to-[#1e293b] text-white font-bold text-xs uppercase tracking-wider hover:opacity-95 shadow-md flex items-center justify-center gap-2"
          >
            <Lock className="w-4 h-4 text-[#C9A96E]" /> Sign In to Backoffice
          </button>
        </form>

        {/* Quick Demo Role Switcher */}
        <div className="pt-4 border-t border-stone-100 space-y-3">
          <span className="text-[11px] font-bold text-stone-400 uppercase tracking-wider block text-center">
            One-Click Demo Roles
          </span>
          <div className="grid grid-cols-1 gap-2">
            <button
              type="button"
              onClick={() => handleQuickRole('admin', 'admin', '/dashboard')}
              className="w-full p-2.5 rounded-xl border border-stone-200 hover:border-stone-900 bg-stone-50 text-left flex items-center justify-between text-xs transition-colors"
            >
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-600" />
                <span>
                  <strong>Admin Account</strong> (Full backoffice & settings)
                </span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-stone-400" />
            </button>

            <button
              type="button"
              onClick={() => handleQuickRole('chef_mario', 'manager', '/kitchen')}
              className="w-full p-2.5 rounded-xl border border-stone-200 hover:border-stone-900 bg-stone-50 text-left flex items-center justify-between text-xs transition-colors"
            >
              <div className="flex items-center gap-2">
                <ChefHat className="w-4 h-4 text-amber-600" />
                <span>
                  <strong>Kitchen Display (KDS)</strong> (Mario Bellini)
                </span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-stone-400" />
            </button>

            <button
              type="button"
              onClick={() => handleQuickRole('front_desk', 'staff', '/admin/tables')}
              className="w-full p-2.5 rounded-xl border border-stone-200 hover:border-stone-900 bg-stone-50 text-left flex items-center justify-between text-xs transition-colors"
            >
              <div className="flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-blue-600" />
                <span>
                  <strong>Host / Front Desk</strong> (Floor plan & waitlist)
                </span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-stone-400" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
