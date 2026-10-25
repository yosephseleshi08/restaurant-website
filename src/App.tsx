import React, { useState, useEffect } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

// Public pages
import { Home } from './pages/Home';
import { MenuPage } from './pages/MenuPage';
import { OrderPage } from './pages/OrderPage';
import { CartPage } from './pages/CartPage';
import { ReservationsPage } from './pages/ReservationsPage';
import { WaitlistPage } from './pages/WaitlistPage';
import { TableOrderPage } from './pages/TableOrderPage';
import { EventsPage } from './pages/EventsPage';
import { GalleryPage } from './pages/GalleryPage';
import { AboutPage } from './pages/AboutPage';
import { ContactPage } from './pages/ContactPage';
import { GiftCardsPage } from './pages/GiftCardsPage';
import { LoyaltyPage } from './pages/LoyaltyPage';
import { LoginPage } from './pages/LoginPage';

// Admin pages
import { DashboardPage } from './pages/admin/DashboardPage';
import { KitchenPage } from './pages/admin/KitchenPage';
import { TablesAdminPage } from './pages/admin/TablesAdminPage';
import { ReservationsAdminPage } from './pages/admin/ReservationsAdminPage';
import { OrdersAdminPage } from './pages/admin/OrdersAdminPage';
import { WaitlistAdminPage } from './pages/admin/WaitlistAdminPage';
import { CustomersAdminPage } from './pages/admin/CustomersAdminPage';
import { MessagesAdminPage } from './pages/admin/MessagesAdminPage';
import { EditorAdminPage } from './pages/admin/EditorAdminPage';

const AppContent: React.FC = () => {
  const [currentPath, setCurrentPath] = useState<string>(() => {
    return window.location.pathname || '/';
  });

  const navigate = (path: string) => {
    setCurrentPath(path);
    window.history.pushState({}, '', path);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname || '/');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const renderPage = () => {
    if (currentPath === '/' || currentPath === '') {
      return <Home onNavigate={navigate} />;
    }
    if (currentPath === '/menu') {
      return <MenuPage onNavigate={navigate} />;
    }
    if (currentPath === '/order' || currentPath === '/order/menu') {
      return <OrderPage onNavigate={navigate} />;
    }
    if (currentPath === '/cart' || currentPath === '/checkout') {
      return <CartPage onNavigate={navigate} />;
    }
    if (currentPath === '/reservations') {
      return <ReservationsPage onNavigate={navigate} />;
    }
    if (currentPath === '/waitlist') {
      return <WaitlistPage onNavigate={navigate} />;
    }
    if (currentPath.startsWith('/table/')) {
      const tableNum = currentPath.split('/table/')[1] || '1';
      return <TableOrderPage tableNumber={tableNum} onNavigate={navigate} />;
    }
    if (currentPath === '/events') {
      return <EventsPage onNavigate={navigate} />;
    }
    if (currentPath === '/gallery') {
      return <GalleryPage />;
    }
    if (currentPath === '/about') {
      return <AboutPage onNavigate={navigate} />;
    }
    if (currentPath === '/contact') {
      return <ContactPage onNavigate={navigate} />;
    }
    if (currentPath === '/gift-cards') {
      return <GiftCardsPage />;
    }
    if (currentPath === '/loyalty') {
      return <LoyaltyPage />;
    }
    if (currentPath === '/login') {
      return <LoginPage onNavigate={navigate} />;
    }

    // Admin & Backoffice routes
    if (currentPath === '/dashboard') {
      return <DashboardPage onNavigate={navigate} />;
    }
    if (currentPath === '/kitchen') {
      return <KitchenPage onNavigate={navigate} />;
    }
    if (currentPath === '/admin/tables') {
      return <TablesAdminPage onNavigate={navigate} />;
    }
    if (currentPath === '/admin/reservations') {
      return <ReservationsAdminPage onNavigate={navigate} />;
    }
    if (currentPath === '/admin/orders') {
      return <OrdersAdminPage onNavigate={navigate} />;
    }
    if (currentPath === '/admin/waitlist') {
      return <WaitlistAdminPage onNavigate={navigate} />;
    }
    if (currentPath === '/admin/customers') {
      return <CustomersAdminPage onNavigate={navigate} />;
    }
    if (currentPath === '/admin/messages') {
      return <MessagesAdminPage onNavigate={navigate} />;
    }
    if (currentPath === '/editor' || currentPath === '/admin/settings') {
      return <EditorAdminPage onNavigate={navigate} />;
    }

    // Default fallback
    return <Home onNavigate={navigate} />;
  };

  const isKitchen = currentPath === '/kitchen';

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar currentPath={currentPath} onNavigate={navigate} />
      <main className="flex-1">{renderPage()}</main>
      {!isKitchen && <Footer onNavigate={navigate} />}
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

export default App;
