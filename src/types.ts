export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  image: string;
  popular?: boolean;
  dietary: string[]; // e.g. ['Vegetarian', 'Gluten-Free', 'Chef Special']
  calories?: number;
}

export interface CartItem {
  id: string;
  name: string;
  price: number;
  category: string;
  image: string;
  quantity: number;
  specialInstructions?: string;
}

export type OrderStatus = 'pending' | 'confirmed' | 'preparing' | 'ready' | 'completed' | 'cancelled';

export interface Order {
  id: number;
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  orderType: 'pickup' | 'delivery' | 'dine-in';
  tableNumber?: string | number;
  deliveryAddress?: string;
  items: CartItem[];
  subtotal: number;
  tax: number;
  deliveryFee: number;
  discount: number;
  total: number;
  status: OrderStatus;
  notes?: string;
  createdAt: string;
}

export type ReservationStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'no-show';

export interface Reservation {
  id: number;
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  partySize: number;
  date: string;
  time: string;
  status: ReservationStatus;
  specialRequests?: string;
  tableAssigned?: number;
  createdAt: string;
}

export type TableStatus = 'available' | 'occupied' | 'reserved' | 'cleaning';

export interface TableNode {
  number: number;
  capacity: number;
  currentGuests: number;
  status: TableStatus;
  xPos: number;
  yPos: number;
  orderId?: number;
}

export interface WaitlistEntry {
  id: number;
  name: string;
  phone: string;
  guests: number;
  createdAt: string;
  notified: boolean;
  status: 'waiting' | 'notified' | 'seated' | 'cancelled';
}

export interface LoyaltyMember {
  id: number;
  name: string;
  email: string;
  phone: string;
  birthday?: string;
  points: number;
  lifetimeSpend: number;
  visits: number;
  lastVisit?: string;
  joinedAt: string;
  favoriteDish?: string;
}

export interface GiftCard {
  id: number;
  code: string;
  amount: number;
  balance: number;
  recipientName: string;
  recipientEmail: string;
  purchaserName: string;
  purchaserEmail: string;
  message?: string;
  status: 'active' | 'redeemed' | 'expired';
  createdAt: string;
}

export interface ContactMessage {
  id: number;
  senderName: string;
  senderEmail: string;
  subject: string;
  messageBody: string;
  isResolved: boolean;
  status: 'new' | 'read' | 'replied' | 'archived';
  reply?: string;
  createdAt: string;
}

export interface RestaurantSettings {
  name: string;
  tagline: string;
  phone: string;
  phoneLink: string;
  email: string;
  address: string;
  hours: {
    days: string;
    time: string;
  }[];
  social: {
    instagram: string;
    facebook: string;
  };
  theme: {
    primaryColor: string;
    secondaryColor: string;
    accentColor: string;
    darkMode: boolean;
  };
  enableOnlineOrdering: boolean;
  enableReservations: boolean;
  enableWaitlist: boolean;
  enableLoyalty: boolean;
  enableGiftCards: boolean;
  enableEvents: boolean;
  enableGallery: boolean;
  maxCapacityPerSlot: number;
}

export interface StaffUser {
  id: number;
  username: string;
  role: 'admin' | 'manager' | 'staff';
  createdAt: string;
}
