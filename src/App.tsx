import { useEffect } from 'react';
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useAppDispatch } from '@/hooks/useRedux';
import { getCurrentUser } from '@/store/slices/authSlice';

// Pages
import HomePage from '@/pages/HomePage';
import { LoginPage, RegisterPage } from '@/pages/auth';
import { ItemListingPage, ItemDetailPage, NewItemPage } from '@/pages/items';
import { DashboardPage } from '@/pages/dashboard';
import NotFoundPage from '@/pages/NotFoundPage';

const queryClient = new QueryClient();

const AppRoutes = () => {
  const dispatch = useAppDispatch();
  
  useEffect(() => {
    // Try to authenticate user on app startup if token exists
    if (localStorage.getItem('token')) {
      dispatch(getCurrentUser());
    } else {
      // Auto login as demo user if no token exists
      const demoLogin = async () => {
        try {
          const response = await fetch('http://localhost:8000/api/auth/demo-login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          });
          
          if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            
            const userResponse = await fetch('http://localhost:8000/api/auth/me', {
              headers: { Authorization: `Bearer ${data.access_token}` }
            });
            
            if (userResponse.ok) {
              const userData = await userResponse.json();
              dispatch({
                type: 'auth/login/fulfilled',
                payload: {
                  token: data.access_token,
                  user: userData
                }
              });
            }
          }
        } catch (error) {
          console.error('Auto demo login failed:', error);
        }
      };
      
      demoLogin();
    }
  }, [dispatch]);
  
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/items" element={<ItemListingPage />} />
      <Route path="/items/:id" element={<ItemDetailPage />} />
      
      {/* Auth required routes */}
      <Route path="/items/new" element={<NewItemPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/dashboard/items" element={<DashboardPage />} />
      <Route path="/dashboard/swaps" element={<DashboardPage />} />
      <Route path="/dashboard/profile" element={<DashboardPage />} />
      
      {/* 404 route */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
