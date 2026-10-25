import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Settings,
  Palette,
  Utensils,
  Bell,
  Users,
  CheckCircle2,
  ArrowLeft,
  Plus,
  Trash2,
  Save,
  Shield
} from 'lucide-react';
import { MenuItem } from '../../types';

interface EditorAdminProps {
  onNavigate: (path: string) => void;
}

export const EditorAdminPage: React.FC<EditorAdminProps> = ({ onNavigate }) => {
  const {
    settings,
    updateSettings,
    updateTheme,
    menu,
    addMenuItem,
    deleteMenuItem,
    staff,
    addStaff,
    deleteStaff,
  } = useApp();

  const [activeTab, setActiveTab] = useState<'details' | 'theme' | 'features' | 'menu' | 'staff'>('details');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Form states for settings
  const [name, setName] = useState(settings.name);
  const [tagline, setTagline] = useState(settings.tagline);
  const [phone, setPhone] = useState(settings.phone);
  const [email, setEmail] = useState(settings.email);
  const [address, setAddress] = useState(settings.address);
  const [maxCapacity, setMaxCapacity] = useState(settings.maxCapacityPerSlot || 28);

  // Theme states
  const [primaryColor, setPrimaryColor] = useState(settings.theme.primaryColor);
  const [secondaryColor, setSecondaryColor] = useState(settings.theme.secondaryColor);
  const [accentColor, setAccentColor] = useState(settings.theme.accentColor);

  // New menu item state
  const [newItemCategory, setNewItemCategory] = useState('appetizers');
  const [newItemName, setNewItemName] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');
  const [newItemPrice, setNewItemPrice] = useState('18.00');
  const [newItemImage, setNewItemImage] = useState('https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80');

  // New staff state
  const [newStaffUser, setNewStaffUser] = useState('');
  const [newStaffRole, setNewStaffRole] = useState<'admin' | 'manager' | 'staff'>('staff');

  const handleSaveDetails = (e: React.FormEvent) => {
    e.preventDefault();
    updateSettings({
      name,
      tagline,
      phone,
      email,
      address,
      maxCapacityPerSlot: Number(maxCapacity),
    });
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  const handleSaveTheme = (e: React.FormEvent) => {
    e.preventDefault();
    updateTheme({
      primaryColor,
      secondaryColor,
      accentColor,
    });
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  const handleAddDish = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemName || !newItemPrice) return;
    addMenuItem(newItemCategory, {
      name: newItemName,
      description: newItemDesc,
      price: parseFloat(newItemPrice) || 15.0,
      category: newItemCategory,
      image: newItemImage,
      dietary: ['Chef Special'],
    });
    setNewItemName('');
    setNewItemDesc('');
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  const handleAddStaffSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newStaffUser) return;
    addStaff(newStaffUser, newStaffRole);
    setNewStaffUser('');
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
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
                Backoffice CMS
              </span>
              <h1 className="font-serif text-3xl font-bold text-[#0B0F19]">
                Visual Restaurant CMS Editor
              </h1>
              <p className="text-xs text-stone-500 mt-1">
                Customize restaurant brand, menu catalog, feature modules, and team credentials.
              </p>
            </div>
          </div>

          {saveSuccess && (
            <div className="p-3 bg-emerald-50 text-emerald-800 rounded-2xl border border-emerald-200 text-xs font-bold flex items-center gap-2 animate-bounce">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Changes Saved Successfully!
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-6">
        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-stone-200 pb-2 overflow-x-auto">
          {[
            { key: 'details', label: 'Restaurant Info', icon: Settings },
            { key: 'theme', label: 'Branding & Colors', icon: Palette },
            { key: 'features', label: 'Module Toggles', icon: Bell },
            { key: 'menu', label: 'Menu Catalog', icon: Utensils },
            { key: 'staff', label: 'Team & Staff', icon: Users },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-4 py-2.5 rounded-2xl text-xs font-bold flex items-center gap-2 transition-all whitespace-nowrap ${
                  activeTab === tab.key
                    ? 'bg-[#0B0F19] text-white shadow-md'
                    : 'bg-white hover:bg-stone-100 text-stone-700 border border-stone-200'
                }`}
              >
                <Icon className="w-4 h-4 text-[#C9A96E]" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab 1: Restaurant Details */}
        {activeTab === 'details' && (
          <form onSubmit={handleSaveDetails} className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-6 max-w-3xl">
            <h3 className="font-serif text-xl font-bold text-[#0B0F19]">
              General Restaurant Information
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">Restaurant Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-stone-300"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">Tagline</label>
                <input
                  type="text"
                  required
                  value={tagline}
                  onChange={(e) => setTagline(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-stone-300"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">Phone Number</label>
                <input
                  type="text"
                  required
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-stone-300"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">Public Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-stone-300"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-stone-700 mb-1">Physical Address</label>
              <input
                type="text"
                required
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full text-xs p-3 rounded-xl border border-stone-300"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-stone-700 mb-1">
                Max Capacity Per Reservation Slot (Anti-Overbooking Guard)
              </label>
              <input
                type="number"
                min={5}
                max={150}
                value={maxCapacity}
                onChange={(e) => setMaxCapacity(Number(e.target.value))}
                className="w-full text-xs p-3 rounded-xl border border-stone-300"
              />
            </div>

            <button
              type="submit"
              className="px-6 py-3 rounded-xl bg-[#0B0F19] hover:bg-stone-800 text-white font-bold text-xs uppercase flex items-center gap-2"
            >
              <Save className="w-4 h-4 text-[#C9A96E]" /> Save Restaurant Details
            </button>
          </form>
        )}

        {/* Tab 2: Theme & Colors */}
        {activeTab === 'theme' && (
          <form onSubmit={handleSaveTheme} className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-6 max-w-3xl">
            <h3 className="font-serif text-xl font-bold text-[#0B0F19]">
              Visual Brand Colors
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-stone-700">Primary Color (Navy / Charcoal)</label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={primaryColor}
                    onChange={(e) => setPrimaryColor(e.target.value)}
                    className="w-12 h-12 rounded-xl cursor-pointer border border-stone-300 p-1"
                  />
                  <span className="font-mono text-xs">{primaryColor}</span>
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-semibold text-stone-700">Secondary Accent (Gold / Brass)</label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={secondaryColor}
                    onChange={(e) => setSecondaryColor(e.target.value)}
                    className="w-12 h-12 rounded-xl cursor-pointer border border-stone-300 p-1"
                  />
                  <span className="font-mono text-xs">{secondaryColor}</span>
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-semibold text-stone-700">Success Accent (Forest Olive)</label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={accentColor}
                    onChange={(e) => setAccentColor(e.target.value)}
                    className="w-12 h-12 rounded-xl cursor-pointer border border-stone-300 p-1"
                  />
                  <span className="font-mono text-xs">{accentColor}</span>
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="px-6 py-3 rounded-xl bg-[#0B0F19] hover:bg-stone-800 text-white font-bold text-xs uppercase flex items-center gap-2"
            >
              <Save className="w-4 h-4 text-[#C9A96E]" /> Apply Theme Palette
            </button>
          </form>
        )}

        {/* Tab 3: Module Toggles */}
        {activeTab === 'features' && (
          <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-4 max-w-3xl">
            <h3 className="font-serif text-xl font-bold text-[#0B0F19]">
              Enable or Disable Restaurant Features
            </h3>
            <p className="text-xs text-stone-500 mb-4">
              Toggle customer-facing capabilities on your live website.
            </p>

            <div className="divide-y divide-stone-100">
              {[
                { key: 'enableOnlineOrdering', label: 'Direct Online Ordering & Cart' },
                { key: 'enableReservations', label: 'Online Table Reservations' },
                { key: 'enableWaitlist', label: 'Live SMS Waitlist Queue' },
                { key: 'enableLoyalty', label: 'Loyalty Rewards Program' },
                { key: 'enableGiftCards', label: 'Digital Gift Cards' },
                { key: 'enableEvents', label: 'Private Dining & Events' },
                { key: 'enableGallery', label: 'Atmosphere Photo Gallery' },
              ].map((feat) => {
                const isEnabled = (settings as any)[feat.key];
                return (
                  <div key={feat.key} className="py-3.5 flex items-center justify-between">
                    <span className="text-xs font-bold text-stone-800">{feat.label}</span>
                    <button
                      type="button"
                      onClick={() => updateSettings({ [feat.key]: !isEnabled })}
                      className={`w-12 h-6 rounded-full transition-colors relative p-1 ${
                        isEnabled ? 'bg-emerald-600' : 'bg-stone-300'
                      }`}
                    >
                      <div
                        className={`w-4 h-4 rounded-full bg-white transition-transform ${
                          isEnabled ? 'translate-x-6' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tab 4: Menu Items Catalog */}
        {activeTab === 'menu' && (
          <div className="space-y-8">
            {/* Add Item Card */}
            <form onSubmit={handleAddDish} className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-4 max-w-3xl">
              <h3 className="font-serif text-xl font-bold text-[#0B0F19]">
                Add New Menu Dish
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">Category</label>
                  <select
                    value={newItemCategory}
                    onChange={(e) => setNewItemCategory(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-xl border border-stone-300"
                  >
                    <option value="appetizers">Appetizers (Antipasti)</option>
                    <option value="pasta">Handmade Pasta (Primi)</option>
                    <option value="mains">Mains & Steaks (Secondi)</option>
                    <option value="pizza">Pizza al Forno</option>
                    <option value="desserts">Desserts (Dolci)</option>
                    <option value="drinks">Wine & Cocktails</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-stone-700 mb-1">Dish Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Risotto ai Funghi Porcini"
                    value={newItemName}
                    onChange={(e) => setNewItemName(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-xl border border-stone-300"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">Price ($) *</label>
                  <input
                    type="number"
                    step="0.5"
                    required
                    value={newItemPrice}
                    onChange={(e) => setNewItemPrice(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-xl border border-stone-300"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">Image URL</label>
                  <input
                    type="url"
                    value={newItemImage}
                    onChange={(e) => setNewItemImage(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-xl border border-stone-300"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">Description</label>
                <input
                  type="text"
                  placeholder="Ingredients, preparation notes, provenance..."
                  value={newItemDesc}
                  onChange={(e) => setNewItemDesc(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-xl border border-stone-300"
                />
              </div>

              <button
                type="submit"
                className="px-5 py-2.5 bg-[#0B0F19] text-white rounded-xl text-xs font-bold uppercase flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4 text-[#C9A96E]" /> Add to Menu Catalog
              </button>
            </form>

            {/* Existing Menu Items */}
            <div className="space-y-6">
              <h3 className="font-serif text-2xl font-bold text-[#0B0F19]">
                Existing Menu Dishes
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(menu).flatMap(([cat, items]) =>
                  items.map((item) => (
                    <div
                      key={item.id}
                      className="bg-white p-4 rounded-2xl border border-stone-200 flex items-center justify-between gap-4"
                    >
                      <img src={item.image} alt={item.name} className="w-14 h-14 rounded-xl object-cover" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="font-bold text-xs text-stone-900">{item.name}</p>
                          <span className="font-mono font-bold text-xs text-[#0B0F19]">
                            ${item.price.toFixed(2)}
                          </span>
                        </div>
                        <p className="text-[11px] text-stone-500 capitalize">{cat}</p>
                      </div>
                      <button
                        onClick={() => deleteMenuItem(cat, item.id)}
                        className="text-stone-400 hover:text-rose-600 p-2"
                        title="Delete item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 5: Staff User Roles */}
        {activeTab === 'staff' && (
          <div className="space-y-6 max-w-3xl">
            {/* Add Staff */}
            <form onSubmit={handleAddStaffSubmit} className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-4">
              <h3 className="font-serif text-xl font-bold text-[#0B0F19] flex items-center gap-2">
                <Shield className="w-5 h-5 text-[#C9A96E]" /> Add Staff Member
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">Username *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. server_elena"
                    value={newStaffUser}
                    onChange={(e) => setNewStaffUser(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-stone-700 mb-1">Role</label>
                  <select
                    value={newStaffRole}
                    onChange={(e) => setNewStaffRole(e.target.value as any)}
                    className="w-full text-xs p-3 rounded-xl border border-stone-300"
                  >
                    <option value="staff">Staff (Floor & Waitlist view)</option>
                    <option value="manager">Manager (Kitchen & Menu editing)</option>
                    <option value="admin">Admin (Full settings access)</option>
                  </select>
                </div>
              </div>
              <button
                type="submit"
                className="px-5 py-2.5 bg-[#0B0F19] text-white rounded-xl text-xs font-bold uppercase flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4 text-[#C9A96E]" /> Add Staff Member
              </button>
            </form>

            {/* Staff list */}
            <div className="bg-white rounded-3xl border border-stone-200 shadow-sm overflow-hidden">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-stone-50 border-b border-stone-200 text-stone-600 font-bold uppercase tracking-wider text-[11px]">
                    <th className="py-4 px-6">Username</th>
                    <th className="py-4 px-4">Role</th>
                    <th className="py-4 px-4">Created Date</th>
                    <th className="py-4 px-6 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {staff.map((u) => (
                    <tr key={u.id} className="hover:bg-stone-50/80">
                      <td className="py-4 px-6 font-bold text-stone-900">{u.username}</td>
                      <td className="py-4 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-stone-100 text-stone-800">
                          {u.role}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-stone-500">{u.createdAt}</td>
                      <td className="py-4 px-6 text-right">
                        {u.username !== 'admin' && (
                          <button
                            onClick={() => deleteStaff(u.id)}
                            className="text-stone-400 hover:text-rose-600 p-1"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
