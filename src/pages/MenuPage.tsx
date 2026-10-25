import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { ShoppingBag, Sparkles, Filter, Check } from 'lucide-react';

interface MenuPageProps {
  onNavigate: (path: string) => void;
}

export const MenuPage: React.FC<MenuPageProps> = ({ onNavigate }) => {
  const { menu, addToCart, settings } = useApp();
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [activeDietary, setActiveDietary] = useState<string>('all');
  const [addedItemName, setAddedItemName] = useState<string | null>(null);

  const categories = [
    { key: 'all', label: 'All Items' },
    { key: 'appetizers', label: 'Antipasti (Appetizers)' },
    { key: 'pasta', label: 'Primi (Handmade Pasta)' },
    { key: 'mains', label: 'Secondi (Mains & Steaks)' },
    { key: 'pizza', label: 'Pizza al Forno' },
    { key: 'desserts', label: 'Dolci (Desserts)' },
    { key: 'drinks', label: 'Vini & Cocktails' },
  ];

  const dietaryFilters = ['All', 'Vegetarian', 'Vegan', 'Gluten-Free', 'Chef Special'];

  const handleAddToCart = (item: any) => {
    addToCart(item, 1);
    setAddedItemName(item.name);
    setTimeout(() => setAddedItemName(null), 2500);
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Hero */}
      <section className="relative py-20 bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white text-center px-4 overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&h=600&fit=crop')",
          }}
        />
        <div className="relative z-10 max-w-3xl mx-auto">
          <span className="inline-block text-[#C9A96E] text-xs font-bold tracking-[0.25em] uppercase bg-[#C9A96E]/10 border border-[#C9A96E]/30 px-3 py-1 rounded-full mb-4">
            Stagionale & Tradizionale
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-white mb-4">
            Our Tuscan Culinary Menu
          </h1>
          <p className="text-slate-300 text-sm sm:text-base font-light max-w-xl mx-auto leading-relaxed">
            Every dish is cooked fresh to order using heirloom flours, single-estate olive oils, and seasonal farm ingredients.
          </p>
        </div>
      </section>

      {/* Added to cart toast */}
      {addedItemName && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#0B0F19] text-white px-5 py-3 rounded-2xl shadow-2xl flex items-center gap-3 border border-[#C9A96E]/40 animate-bounce">
          <div className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-white">
            <Check className="w-3.5 h-3.5" />
          </div>
          <div className="text-xs">
            <span className="font-bold">{addedItemName}</span> added to your order!
          </div>
          <button
            onClick={() => onNavigate('/cart')}
            className="ml-2 text-xs text-[#C9A96E] underline font-bold"
          >
            View Cart
          </button>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-10">
        <div className="flex items-center justify-center flex-wrap gap-2 pb-6 border-b border-stone-200">
          {categories.map((c) => (
            <button
              key={c.key}
              onClick={() => setActiveCategory(c.key)}
              className={`px-5 py-2.5 rounded-full text-xs sm:text-sm font-semibold transition-all duration-200 ${
                activeCategory === c.key
                  ? 'bg-[#0B0F19] text-white shadow-md'
                  : 'bg-white text-stone-700 hover:bg-stone-100 border border-stone-200/80'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>

        {/* Dietary Filters */}
        <div className="flex items-center justify-center gap-2 pt-4 pb-10 flex-wrap">
          <span className="text-xs text-stone-600 font-semibold flex items-center gap-1 mr-2">
            <Filter className="w-3.5 h-3.5 text-[#C9A96E]" /> Dietary:
          </span>
          {dietaryFilters.map((tag) => (
            <button
              key={tag}
              onClick={() => setActiveDietary(tag)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                activeDietary === tag
                  ? 'bg-[#C9A96E] text-stone-900 font-bold'
                  : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>

        {/* Menu Items Grid */}
        <div className="space-y-16">
          {Object.entries(menu)
            .filter(([cat]) => activeCategory === 'all' || activeCategory === cat)
            .map(([cat, items]) => {
              const filteredItems = items.filter((item) => {
                if (activeDietary === 'All') return true;
                return item.dietary.includes(activeDietary);
              });

              if (filteredItems.length === 0) return null;

              const categoryTitle =
                cat === 'appetizers'
                  ? 'Antipasti (Appetizers)'
                  : cat === 'pasta'
                  ? 'Primi Piatti (Pasta)'
                  : cat === 'mains'
                  ? 'Secondi Piatti (Mains)'
                  : cat === 'pizza'
                  ? 'Pizze Tradizionali'
                  : cat === 'desserts'
                  ? 'Dolci (Desserts)'
                  : 'Vini & Bevande';

              return (
                <div key={cat} className="space-y-6">
                  <div className="flex items-center gap-4 border-b-2 border-stone-200 pb-3">
                    <h2 className="font-serif text-2xl sm:text-3xl font-bold text-[#0B0F19]">
                      {categoryTitle}
                    </h2>
                    <span className="text-xs font-semibold text-stone-600 bg-stone-100 px-3 py-1 rounded-full">
                      {filteredItems.length} items
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
                    {filteredItems.map((item) => (
                      <div
                        key={item.id}
                        className="bg-white rounded-2xl p-4 sm:p-5 border border-stone-200/80 shadow-sm hover:shadow-md transition-shadow flex flex-col sm:flex-row gap-5 items-start sm:items-center justify-between"
                      >
                        <img
                          src={item.image}
                          alt={item.name}
                          className="w-full sm:w-32 h-32 rounded-xl object-cover shrink-0"
                          loading="lazy"
                        />
                        <div className="flex-1 space-y-2">
                          <div className="flex items-start justify-between gap-2">
                            <h3 className="font-serif text-lg font-bold text-[#0B0F19]">
                              {item.name}
                            </h3>
                            <span className="font-bold text-[#0B0F19] text-base shrink-0">
                              ${item.price.toFixed(2)}
                            </span>
                          </div>

                          <p className="text-xs text-stone-500 leading-relaxed">
                            {item.description}
                          </p>

                          <div className="flex items-center justify-between pt-2">
                            <div className="flex flex-wrap gap-1">
                              {item.dietary.map((d) => (
                                <span
                                  key={d}
                                  className="text-[10px] bg-stone-100 text-stone-700 px-2 py-0.5 rounded font-medium"
                                >
                                  {d}
                                </span>
                              ))}
                            </div>

                            {settings.enableOnlineOrdering && (
                              <button
                                onClick={() => handleAddToCart(item)}
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-stone-100 hover:bg-[#0B0F19] text-stone-800 hover:text-white transition-colors text-xs font-semibold"
                              >
                                <ShoppingBag className="w-3.5 h-3.5" />
                                <span>Add</span>
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
};
