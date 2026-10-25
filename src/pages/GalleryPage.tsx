import React, { useState } from 'react';
import { GALLERY_ITEMS } from '../data/initialData';
import { X, ZoomIn } from 'lucide-react';

export const GalleryPage: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState<'all' | 'food' | 'interior' | 'drinks'>('all');
  const [selectedImage, setSelectedImage] = useState<{ url: string; caption: string } | null>(null);

  const filtered = GALLERY_ITEMS.filter((item) => activeFilter === 'all' || item.category === activeFilter);

  return (
    <div className="min-h-screen bg-[#FAFAF9] pb-24">
      {/* Lightbox Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in"
          onClick={() => setSelectedImage(null)}
        >
          <button
            onClick={() => setSelectedImage(null)}
            className="absolute top-6 right-6 text-white/80 hover:text-white p-2 rounded-full bg-white/10"
          >
            <X className="w-6 h-6" />
          </button>
          <div className="max-w-4xl max-h-[85vh] text-center space-y-3" onClick={(e) => e.stopPropagation()}>
            <img
              src={selectedImage.url}
              alt={selectedImage.caption}
              className="max-h-[75vh] max-w-full rounded-2xl mx-auto shadow-2xl object-contain"
            />
            <p className="text-stone-300 text-sm font-medium">{selectedImage.caption}</p>
          </div>
        </div>
      )}

      {/* Header */}
      <section className="bg-gradient-to-br from-[#0B0F19] to-[#1a2332] text-white py-16 px-4 text-center">
        <div className="max-w-2xl mx-auto space-y-3">
          <span className="text-[#C9A96E] font-bold uppercase tracking-widest text-xs">
            Atmosphere & Gastronomy
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-white">
            Photo Gallery
          </h1>
          <p className="text-stone-300 text-sm font-light">
            A glimpse inside our warm dining rooms, open fire hearth, and handcrafted culinary art.
          </p>
        </div>
      </section>

      {/* Filter Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-10">
        <div className="flex items-center justify-center gap-2 mb-10 flex-wrap">
          {(['all', 'food', 'interior', 'drinks'] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveFilter(cat)}
              className={`px-6 py-2.5 rounded-full text-xs sm:text-sm font-semibold capitalize transition-all ${
                activeFilter === cat
                  ? 'bg-[#0B0F19] text-white shadow-md'
                  : 'bg-white text-stone-700 hover:bg-stone-100 border border-stone-200'
              }`}
            >
              {cat === 'all' ? 'All Photos' : cat}
            </button>
          ))}
        </div>

        {/* Masonry / Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((item, idx) => (
            <div
              key={idx}
              onClick={() => setSelectedImage(item)}
              className="group relative rounded-3xl overflow-hidden shadow-sm hover:shadow-2xl transition-all duration-300 cursor-pointer aspect-4/3 bg-stone-100"
            >
              <img
                src={item.url}
                alt={item.caption}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 p-6 flex flex-col justify-end text-white">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-medium text-stone-200 line-clamp-2">{item.caption}</p>
                  <ZoomIn className="w-5 h-5 text-[#C9A96E] shrink-0 ml-2" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
