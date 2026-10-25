import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Grid, Users, CheckCircle, RefreshCw, AlertCircle, ArrowLeft } from 'lucide-react';
import { TableStatus } from '../../types';

interface TablesAdminPageProps {
  onNavigate: (path: string) => void;
}

export const TablesAdminPage: React.FC<TablesAdminPageProps> = ({ onNavigate }) => {
  const { tables, updateTableStatus, updateTablePosition } = useApp();
  const [selectedTable, setSelectedTable] = useState<number | null>(null);
  const [draggedTable, setDraggedTable] = useState<number | null>(null);

  const activeTableObj = tables.find((t) => t.number === selectedTable);

  const handleDragStart = (e: React.DragEvent, tableNum: number) => {
    setDraggedTable(tableNum);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (draggedTable === null) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.max(20, Math.min(rect.width - 90, e.clientX - rect.left - 40));
    const y = Math.max(20, Math.min(rect.height - 90, e.clientY - rect.top - 40));
    updateTablePosition(draggedTable, Math.round(x), Math.round(y));
    setDraggedTable(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const getStatusColor = (status: TableStatus) => {
    switch (status) {
      case 'available':
        return 'bg-emerald-100 border-emerald-500 text-emerald-900 shadow-emerald-500/20';
      case 'occupied':
        return 'bg-rose-100 border-rose-500 text-rose-900 shadow-rose-500/20';
      case 'reserved':
        return 'bg-amber-100 border-amber-500 text-amber-900 shadow-amber-500/20';
      case 'cleaning':
        return 'bg-stone-200 border-stone-400 text-stone-700 shadow-stone-400/20';
      default:
        return 'bg-white border-stone-300';
    }
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
              title="Back to Dashboard"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <span className="text-xs uppercase font-bold tracking-widest text-[#C9A96E]">
                Host Stand
              </span>
              <h1 className="font-serif text-3xl font-bold text-[#0B0F19]">
                Table Floor Plan Management
              </h1>
              <p className="text-xs text-stone-500 mt-1">
                Drag tables to rearrange your dining room layout. Click any table to adjust seating status.
              </p>
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center gap-3 flex-wrap text-xs font-semibold bg-stone-50 p-2 rounded-2xl border border-stone-200">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span> Available
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-rose-500 inline-block"></span> Occupied
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-amber-500 inline-block"></span> Reserved
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-stone-400 inline-block"></span> Cleaning
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Floor Canvas (Col 8/9) */}
        <div className="lg:col-span-8 bg-white rounded-3xl p-6 border border-stone-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-stone-100 text-xs text-stone-500">
            <span>Main Dining Room & Terrace Canvas</span>
            <span>Drag table circles to reposition</span>
          </div>

          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="relative w-full h-[520px] bg-stone-50 rounded-2xl border-2 border-dashed border-stone-300 overflow-hidden"
          >
            {/* Kitchen & Bar Reference Labels */}
            <div className="absolute top-3 left-4 bg-stone-200 text-stone-600 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">
              🍳 Open Kitchen & Wood-Fired Hearth
            </div>
            <div className="absolute bottom-3 right-4 bg-stone-200 text-stone-600 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">
              🍷 Tuscan Wine Bar & Host Stand
            </div>

            {tables.map((table) => {
              const colorStyle = getStatusColor(table.status);
              const isSelected = selectedTable === table.number;
              return (
                <div
                  key={table.number}
                  draggable
                  onDragStart={(e) => handleDragStart(e, table.number)}
                  onClick={() => setSelectedTable(table.number)}
                  style={{ left: `${table.xPos}px`, top: `${table.yPos}px` }}
                  className={`absolute w-20 h-20 rounded-full border-3 flex flex-col items-center justify-center cursor-grab active:cursor-grabbing select-none transition-all duration-200 hover:scale-110 shadow-lg ${colorStyle} ${
                    isSelected ? 'ring-4 ring-[#0B0F19]' : ''
                  }`}
                >
                  <span className="font-serif text-lg font-bold leading-none">
                    T{table.number}
                  </span>
                  <span className="text-[10px] opacity-80 mt-0.5">
                    {table.capacity} seats
                  </span>
                  {table.currentGuests > 0 && (
                    <span className="text-[9px] font-bold mt-0.5">
                      {table.currentGuests} guests
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Table Inspector (Col 4) */}
        <div className="lg:col-span-4 bg-white rounded-3xl p-6 sm:p-8 border border-stone-200 shadow-lg space-y-6">
          {activeTableObj ? (
            <div className="space-y-6">
              <div>
                <span className="text-xs font-bold uppercase text-[#C9A96E] tracking-widest">
                  Selected Table
                </span>
                <h3 className="font-serif text-3xl font-bold text-[#0B0F19] mt-1">
                  Table {activeTableObj.number}
                </h3>
                <p className="text-xs text-stone-500">
                  Capacity: {activeTableObj.capacity} seats · Currently{' '}
                  <strong className="uppercase">{activeTableObj.status}</strong>
                </p>
              </div>

              {/* Status Change Buttons */}
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-stone-700">
                  Update Seating Status
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => updateTableStatus(activeTableObj.number, 'available')}
                    className={`p-2.5 rounded-xl text-xs font-bold transition-all ${
                      activeTableObj.status === 'available'
                        ? 'bg-emerald-600 text-white shadow-md'
                        : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200'
                    }`}
                  >
                    Available
                  </button>
                  <button
                    onClick={() => updateTableStatus(activeTableObj.number, 'occupied', activeTableObj.capacity)}
                    className={`p-2.5 rounded-xl text-xs font-bold transition-all ${
                      activeTableObj.status === 'occupied'
                        ? 'bg-rose-600 text-white shadow-md'
                        : 'bg-rose-50 text-rose-800 hover:bg-rose-100 border border-rose-200'
                    }`}
                  >
                    Occupied
                  </button>
                  <button
                    onClick={() => updateTableStatus(activeTableObj.number, 'reserved')}
                    className={`p-2.5 rounded-xl text-xs font-bold transition-all ${
                      activeTableObj.status === 'reserved'
                        ? 'bg-amber-600 text-white shadow-md'
                        : 'bg-amber-50 text-amber-800 hover:bg-amber-100 border border-amber-200'
                    }`}
                  >
                    Reserved
                  </button>
                  <button
                    onClick={() => updateTableStatus(activeTableObj.number, 'cleaning')}
                    className={`p-2.5 rounded-xl text-xs font-bold transition-all ${
                      activeTableObj.status === 'cleaning'
                        ? 'bg-stone-600 text-white shadow-md'
                        : 'bg-stone-100 text-stone-800 hover:bg-stone-200 border border-stone-300'
                    }`}
                  >
                    Cleaning
                  </button>
                </div>
              </div>

              {/* Guest Count Slider if occupied */}
              {activeTableObj.status === 'occupied' && (
                <div className="space-y-2 pt-2 border-t border-stone-100">
                  <label className="block text-xs font-semibold text-stone-700">
                    Seated Guests: {activeTableObj.currentGuests}
                  </label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 6, 8]
                      .filter((n) => n <= activeTableObj.capacity + 2)
                      .map((n) => (
                        <button
                          key={n}
                          onClick={() => updateTableStatus(activeTableObj.number, 'occupied', n)}
                          className={`w-8 h-8 rounded-lg text-xs font-bold transition-colors ${
                            activeTableObj.currentGuests === n
                              ? 'bg-[#0B0F19] text-white'
                              : 'bg-stone-100 hover:bg-stone-200 text-stone-700'
                          }`}
                        >
                          {n}
                        </button>
                      ))}
                  </div>
                </div>
              )}

              {/* QR Code Table Order link */}
              <div className="pt-4 border-t border-stone-100">
                <button
                  onClick={() => onNavigate(`/table/${activeTableObj.number}`)}
                  className="w-full py-3 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-800 text-xs font-bold uppercase transition-colors"
                >
                  📱 Test Table {activeTableObj.number} QR Order
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 text-stone-400 space-y-3">
              <Grid className="w-12 h-12 mx-auto stroke-1" />
              <h4 className="font-serif text-lg font-bold text-stone-700">
                Select Any Table
              </h4>
              <p className="text-xs text-stone-500">
                Click a table on the floor plan canvas to view seats, adjust live availability, or launch its self-ordering QR screen.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
