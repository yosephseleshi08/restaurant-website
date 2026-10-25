import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  MenuItem,
  CartItem,
  Order,
  OrderStatus,
  Reservation,
  ReservationStatus,
  TableNode,
  TableStatus,
  WaitlistEntry,
  LoyaltyMember,
  GiftCard,
  ContactMessage,
  RestaurantSettings,
  StaffUser,
} from '../types';
import {
  INITIAL_SETTINGS,
  INITIAL_MENU,
  INITIAL_ORDERS,
  INITIAL_RESERVATIONS,
  INITIAL_TABLES,
  INITIAL_WAITLIST,
  INITIAL_LOYALTY,
  INITIAL_GIFT_CARDS,
  INITIAL_MESSAGES,
  INITIAL_STAFF,
} from '../data/initialData';

interface AppContextType {
  settings: RestaurantSettings;
  updateSettings: (newSettings: Partial<RestaurantSettings>) => void;
  updateTheme: (theme: Partial<RestaurantSettings['theme']>) => void;
  menu: Record<string, MenuItem[]>;
  addMenuItem: (category: string, item: Omit<MenuItem, 'id'>) => void;
  updateMenuItem: (category: string, itemId: string, item: Partial<MenuItem>) => void;
  deleteMenuItem: (category: string, itemId: string) => void;
  cart: CartItem[];
  cartCount: number;
  cartSubtotal: number;
  addToCart: (item: MenuItem, qty?: number, specialInstructions?: string) => void;
  removeFromCart: (itemId: string) => void;
  updateCartQty: (itemId: string, quantity: number) => void;
  clearCart: () => void;
  orders: Order[];
  placeOrder: (orderData: {
    customerName: string;
    customerEmail: string;
    customerPhone: string;
    orderType: 'pickup' | 'delivery' | 'dine-in';
    tableNumber?: string | number;
    deliveryAddress?: string;
    notes?: string;
  }) => Order;
  updateOrderStatus: (orderId: number, status: OrderStatus) => void;
  reservations: Reservation[];
  addReservation: (resData: {
    customerName: string;
    customerEmail: string;
    customerPhone: string;
    partySize: number;
    date: string;
    time: string;
    specialRequests?: string;
  }) => { success: boolean; message: string; reservation?: Reservation };
  updateReservationStatus: (resId: number, status: ReservationStatus) => void;
  tables: TableNode[];
  updateTableStatus: (tableNumber: number, status: TableStatus, currentGuests?: number) => void;
  updateTablePosition: (tableNumber: number, xPos: number, yPos: number) => void;
  waitlist: WaitlistEntry[];
  joinWaitlist: (name: string, phone: string, guests: number) => WaitlistEntry;
  notifyWaitlist: (id: number) => void;
  seatWaitlist: (id: number) => void;
  loyaltyMembers: LoyaltyMember[];
  enrollLoyalty: (name: string, email: string, phone: string, birthday?: string) => LoyaltyMember;
  checkLoyalty: (email: string) => LoyaltyMember | undefined;
  giftCards: GiftCard[];
  purchaseGiftCard: (data: {
    amount: number;
    recipientName: string;
    recipientEmail: string;
    purchaserName: string;
    purchaserEmail: string;
    message?: string;
  }) => GiftCard;
  checkGiftCard: (code: string) => GiftCard | undefined;
  messages: ContactMessage[];
  sendMessage: (name: string, email: string, subject: string, message: string) => void;
  replyMessage: (id: number, replyText: string) => void;
  archiveMessage: (id: number) => void;
  staff: StaffUser[];
  addStaff: (username: string, role: 'admin' | 'manager' | 'staff') => void;
  deleteStaff: (id: number) => void;
  currentUser: StaffUser | null;
  login: (username: string, role?: 'admin' | 'manager' | 'staff') => boolean;
  logout: () => void;
  exportCSV: (type: 'reservations' | 'orders' | 'messages') => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

function loadFromStorage<T>(key: string, fallback: T): T {
  try {
    const item = localStorage.getItem(`rbc_${key}`);
    return item ? JSON.parse(item) : fallback;
  } catch (e) {
    return fallback;
  }
}

function saveToStorage<T>(key: string, data: T) {
  try {
    localStorage.setItem(`rbc_${key}`, JSON.stringify(data));
  } catch (e) {
    console.error(`Failed to save ${key} to storage`, e);
  }
}

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<RestaurantSettings>(() => loadFromStorage('settings', INITIAL_SETTINGS));
  const [menu, setMenu] = useState<Record<string, MenuItem[]>>(() => loadFromStorage('menu', INITIAL_MENU));
  const [cart, setCart] = useState<CartItem[]>(() => loadFromStorage('cart', []));
  const [orders, setOrders] = useState<Order[]>(() => loadFromStorage('orders', INITIAL_ORDERS));
  const [reservations, setReservations] = useState<Reservation[]>(() => loadFromStorage('reservations', INITIAL_RESERVATIONS));
  const [tables, setTables] = useState<TableNode[]>(() => loadFromStorage('tables', INITIAL_TABLES));
  const [waitlist, setWaitlist] = useState<WaitlistEntry[]>(() => loadFromStorage('waitlist', INITIAL_WAITLIST));
  const [loyaltyMembers, setLoyaltyMembers] = useState<LoyaltyMember[]>(() => loadFromStorage('loyalty', INITIAL_LOYALTY));
  const [giftCards, setGiftCards] = useState<GiftCard[]>(() => loadFromStorage('giftcards', INITIAL_GIFT_CARDS));
  const [messages, setMessages] = useState<ContactMessage[]>(() => loadFromStorage('messages', INITIAL_MESSAGES));
  const [staff, setStaff] = useState<StaffUser[]>(() => loadFromStorage('staff', INITIAL_STAFF));
  const [currentUser, setCurrentUser] = useState<StaffUser | null>(() => loadFromStorage('user', null));

  useEffect(() => saveToStorage('settings', settings), [settings]);
  useEffect(() => saveToStorage('menu', menu), [menu]);
  useEffect(() => saveToStorage('cart', cart), [cart]);
  useEffect(() => saveToStorage('orders', orders), [orders]);
  useEffect(() => saveToStorage('reservations', reservations), [reservations]);
  useEffect(() => saveToStorage('tables', tables), [tables]);
  useEffect(() => saveToStorage('waitlist', waitlist), [waitlist]);
  useEffect(() => saveToStorage('loyalty', loyaltyMembers), [loyaltyMembers]);
  useEffect(() => saveToStorage('giftcards', giftCards), [giftCards]);
  useEffect(() => saveToStorage('messages', messages), [messages]);
  useEffect(() => saveToStorage('staff', staff), [staff]);
  useEffect(() => saveToStorage('user', currentUser), [currentUser]);

  const updateSettings = (newSettings: Partial<RestaurantSettings>) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  };

  const updateTheme = (newTheme: Partial<RestaurantSettings['theme']>) => {
    setSettings((prev) => ({
      ...prev,
      theme: { ...prev.theme, ...newTheme },
    }));
  };

  const addMenuItem = (category: string, item: Omit<MenuItem, 'id'>) => {
    const newItem: MenuItem = {
      ...item,
      id: `item-${Date.now()}`,
    };
    setMenu((prev) => ({
      ...prev,
      [category]: [...(prev[category] || []), newItem],
    }));
  };

  const updateMenuItem = (category: string, itemId: string, itemUpdates: Partial<MenuItem>) => {
    setMenu((prev) => ({
      ...prev,
      [category]: (prev[category] || []).map((item) => (item.id === itemId ? { ...item, ...itemUpdates } : item)),
    }));
  };

  const deleteMenuItem = (category: string, itemId: string) => {
    setMenu((prev) => ({
      ...prev,
      [category]: (prev[category] || []).filter((item) => item.id !== itemId),
    }));
  };

  const addToCart = (item: MenuItem, qty = 1, specialInstructions?: string) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.id === item.id);
      if (existing) {
        return prev.map((i) =>
          i.id === item.id ? { ...i, quantity: i.quantity + qty, specialInstructions: specialInstructions || i.specialInstructions } : i
        );
      }
      return [
        ...prev,
        {
          id: item.id,
          name: item.name,
          price: item.price,
          category: item.category,
          image: item.image,
          quantity: qty,
          specialInstructions,
        },
      ];
    });
  };

  const removeFromCart = (itemId: string) => {
    setCart((prev) => prev.filter((i) => i.id !== itemId));
  };

  const updateCartQty = (itemId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(itemId);
      return;
    }
    setCart((prev) => prev.map((i) => (i.id === itemId ? { ...i, quantity } : i)));
  };

  const clearCart = () => setCart([]);

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
  const cartSubtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const placeOrder = (orderData: {
    customerName: string;
    customerEmail: string;
    customerPhone: string;
    orderType: 'pickup' | 'delivery' | 'dine-in';
    tableNumber?: string | number;
    deliveryAddress?: string;
    notes?: string;
  }) => {
    const subtotal = cartSubtotal;
    const tax = Math.round(subtotal * 0.0825 * 100) / 100;
    const deliveryFee = orderData.orderType === 'delivery' ? (subtotal > 60 ? 0 : 3.99) : 0;
    const total = Math.round((subtotal + tax + deliveryFee) * 100) / 100;

    const newOrder: Order = {
      id: orders.length > 0 ? Math.max(...orders.map((o) => o.id)) + 1 : 1001,
      customerName: orderData.customerName,
      customerEmail: orderData.customerEmail,
      customerPhone: orderData.customerPhone,
      orderType: orderData.orderType,
      tableNumber: orderData.tableNumber,
      deliveryAddress: orderData.deliveryAddress,
      items: [...cart],
      subtotal,
      tax,
      deliveryFee,
      discount: 0,
      total,
      status: 'pending',
      notes: orderData.notes,
      createdAt: new Date().toISOString(),
    };

    setOrders((prev) => [newOrder, ...prev]);
    clearCart();

    // If loyalty member, add points
    setLoyaltyMembers((prev) =>
      prev.map((m) => {
        if (m.email.toLowerCase() === orderData.customerEmail.toLowerCase()) {
          return {
            ...m,
            points: m.points + Math.floor(subtotal),
            lifetimeSpend: m.lifetimeSpend + total,
            visits: m.visits + 1,
            lastVisit: new Date().toISOString().split('T')[0],
          };
        }
        return m;
      })
    );

    return newOrder;
  };

  const updateOrderStatus = (orderId: number, status: OrderStatus) => {
    setOrders((prev) =>
      prev.map((order) => (order.id === orderId ? { ...order, status } : order))
    );
  };

  const addReservation = (resData: {
    customerName: string;
    customerEmail: string;
    customerPhone: string;
    partySize: number;
    date: string;
    time: string;
    specialRequests?: string;
  }) => {
    // Capacity limit verification check
    const existingInSlot = reservations
      .filter((r) => r.date === resData.date && r.time === resData.time && r.status !== 'cancelled')
      .reduce((sum, r) => sum + r.partySize, 0);

    const maxCap = settings.maxCapacityPerSlot || 28;
    const remaining = maxCap - existingInSlot;

    if (existingInSlot + resData.partySize > maxCap) {
      return {
        success: false,
        message: `Sorry, there are only ${Math.max(0, remaining)} seats remaining for ${resData.time}. Please select another time or reduce party size.`,
      };
    }

    const newRes: Reservation = {
      id: reservations.length > 0 ? Math.max(...reservations.map((r) => r.id)) + 1 : 101,
      customerName: resData.customerName,
      customerEmail: resData.customerEmail,
      customerPhone: resData.customerPhone,
      partySize: resData.partySize,
      date: resData.date,
      time: resData.time,
      status: 'confirmed',
      specialRequests: resData.specialRequests,
      createdAt: new Date().toISOString(),
    };

    setReservations((prev) => [newRes, ...prev]);

    return {
      success: true,
      message: 'Reservation confirmed! We look forward to welcoming you.',
      reservation: newRes,
    };
  };

  const updateReservationStatus = (resId: number, status: ReservationStatus) => {
    setReservations((prev) =>
      prev.map((r) => (r.id === resId ? { ...r, status } : r))
    );
  };

  const updateTableStatus = (tableNumber: number, status: TableStatus, currentGuests = 0) => {
    setTables((prev) =>
      prev.map((t) =>
        t.number === tableNumber
          ? { ...t, status, currentGuests: status === 'available' || status === 'cleaning' ? 0 : currentGuests || t.capacity }
          : t
      )
    );
  };

  const updateTablePosition = (tableNumber: number, xPos: number, yPos: number) => {
    setTables((prev) =>
      prev.map((t) => (t.number === tableNumber ? { ...t, xPos, yPos } : t))
    );
  };

  const joinWaitlist = (name: string, phone: string, guests: number) => {
    const entry: WaitlistEntry = {
      id: Date.now(),
      name,
      phone,
      guests,
      createdAt: new Date().toISOString(),
      notified: false,
      status: 'waiting',
    };
    setWaitlist((prev) => [...prev, entry]);
    return entry;
  };

  const notifyWaitlist = (id: number) => {
    setWaitlist((prev) =>
      prev.map((w) => (w.id === id ? { ...w, notified: true, status: 'notified' } : w))
    );
  };

  const seatWaitlist = (id: number) => {
    setWaitlist((prev) =>
      prev.map((w) => (w.id === id ? { ...w, status: 'seated' } : w))
    );
  };

  const enrollLoyalty = (name: string, email: string, phone: string, birthday?: string) => {
    const existing = loyaltyMembers.find((m) => m.email.toLowerCase() === email.toLowerCase());
    if (existing) return existing;

    const newMember: LoyaltyMember = {
      id: Date.now(),
      name,
      email,
      phone,
      birthday,
      points: 50, // 50 Welcome bonus points!
      lifetimeSpend: 0,
      visits: 0,
      joinedAt: new Date().toISOString().split('T')[0],
    };
    setLoyaltyMembers((prev) => [...prev, newMember]);
    return newMember;
  };

  const checkLoyalty = (email: string) => {
    return loyaltyMembers.find((m) => m.email.toLowerCase() === email.trim().toLowerCase());
  };

  const purchaseGiftCard = (data: {
    amount: number;
    recipientName: string;
    recipientEmail: string;
    purchaserName: string;
    purchaserEmail: string;
    message?: string;
  }) => {
    const randCode = `BELLA-${Math.random().toString(36).substring(2, 6).toUpperCase()}-${Math.floor(1000 + Math.random() * 9000)}`;
    const newCard: GiftCard = {
      id: Date.now(),
      code: randCode,
      amount: data.amount,
      balance: data.amount,
      recipientName: data.recipientName,
      recipientEmail: data.recipientEmail,
      purchaserName: data.purchaserName,
      purchaserEmail: data.purchaserEmail,
      message: data.message,
      status: 'active',
      createdAt: new Date().toISOString(),
    };
    setGiftCards((prev) => [newCard, ...prev]);
    return newCard;
  };

  const checkGiftCard = (code: string) => {
    return giftCards.find((c) => c.code.toUpperCase() === code.trim().toUpperCase());
  };

  const sendMessage = (senderName: string, senderEmail: string, subject: string, messageBody: string) => {
    const newMsg: ContactMessage = {
      id: Date.now(),
      senderName,
      senderEmail,
      subject,
      messageBody,
      isResolved: false,
      status: 'new',
      createdAt: new Date().toISOString(),
    };
    setMessages((prev) => [newMsg, ...prev]);
  };

  const replyMessage = (id: number, replyText: string) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? { ...m, reply: replyText, status: 'replied', isResolved: true } : m))
    );
  };

  const archiveMessage = (id: number) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? { ...m, status: 'archived', isResolved: true } : m))
    );
  };

  const addStaff = (username: string, role: 'admin' | 'manager' | 'staff') => {
    const newUser: StaffUser = {
      id: Date.now(),
      username,
      role,
      createdAt: new Date().toISOString().split('T')[0],
    };
    setStaff((prev) => [...prev, newUser]);
  };

  const deleteStaff = (id: number) => {
    setStaff((prev) => prev.filter((u) => u.id !== id));
  };

  const login = (username: string, preferredRole?: 'admin' | 'manager' | 'staff') => {
    const matched = staff.find((s) => s.username.toLowerCase() === username.toLowerCase());
    if (matched) {
      setCurrentUser(matched);
      return true;
    }
    // Demo auto-login for testing convenience
    const demoUser: StaffUser = {
      id: 999,
      username: username || 'admin',
      role: preferredRole || 'admin',
      createdAt: new Date().toISOString().split('T')[0],
    };
    setCurrentUser(demoUser);
    return true;
  };

  const logout = () => {
    setCurrentUser(null);
  };

  const exportCSV = (type: 'reservations' | 'orders' | 'messages') => {
    let csvContent = '';
    let filename = '';

    if (type === 'reservations') {
      filename = `reservations_export_${new Date().toISOString().split('T')[0]}.csv`;
      csvContent = 'ID,Customer Name,Email,Phone,Date,Time,Party Size,Status,Special Requests\n';
      reservations.forEach((r) => {
        csvContent += `"${r.id}","${r.customerName}","${r.customerEmail}","${r.customerPhone}","${r.date}","${r.time}","${r.partySize}","${r.status}","${(r.specialRequests || '').replace(/"/g, '""')}"\n`;
      });
    } else if (type === 'orders') {
      filename = `orders_export_${new Date().toISOString().split('T')[0]}.csv`;
      csvContent = 'Order ID,Customer,Email,Type,Total,Status,Date,Items\n';
      orders.forEach((o) => {
        const itemsStr = o.items.map((i) => `${i.quantity}x ${i.name}`).join('; ');
        csvContent += `"${o.id}","${o.customerName}","${o.customerEmail}","${o.orderType}","$${o.total.toFixed(2)}","${o.status}","${o.createdAt}","${itemsStr}"\n`;
      });
    } else if (type === 'messages') {
      filename = `messages_export_${new Date().toISOString().split('T')[0]}.csv`;
      csvContent = 'ID,Sender,Email,Subject,Status,Date,Message,Reply\n';
      messages.forEach((m) => {
        csvContent += `"${m.id}","${m.senderName}","${m.senderEmail}","${m.subject}","${m.status}","${m.createdAt}","${(m.messageBody || '').replace(/"/g, '""')}","${(m.reply || '').replace(/"/g, '""')}"\n`;
      });
    }

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <AppContext.Provider
      value={{
        settings,
        updateSettings,
        updateTheme,
        menu,
        addMenuItem,
        updateMenuItem,
        deleteMenuItem,
        cart,
        cartCount,
        cartSubtotal,
        addToCart,
        removeFromCart,
        updateCartQty,
        clearCart,
        orders,
        placeOrder,
        updateOrderStatus,
        reservations,
        addReservation,
        updateReservationStatus,
        tables,
        updateTableStatus,
        updateTablePosition,
        waitlist,
        joinWaitlist,
        notifyWaitlist,
        seatWaitlist,
        loyaltyMembers,
        enrollLoyalty,
        checkLoyalty,
        giftCards,
        purchaseGiftCard,
        checkGiftCard,
        messages,
        sendMessage,
        replyMessage,
        archiveMessage,
        staff,
        addStaff,
        deleteStaff,
        currentUser,
        login,
        logout,
        exportCSV,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within an AppProvider');
  return context;
};
