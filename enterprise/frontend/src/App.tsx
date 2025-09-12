import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ConfigProvider, theme } from 'antd';
import { Toaster } from 'react-hot-toast';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import relativeTime from 'dayjs/plugin/relativeTime';

import { store } from './store';
import { useAuth } from './hooks/useAuth';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import CostAnalysis from './pages/CostAnalysis/CostAnalysis';
import BusinessIntelligence from './pages/BusinessIntelligence/BusinessIntelligence';
import CloudAccounts from './pages/CloudAccounts/CloudAccounts';
import Organizations from './pages/Organizations/Organizations';
import Teams from './pages/Teams/Teams';
import Users from './pages/Users/Users';
import Settings from './pages/Settings/Settings';
import Login from './pages/Auth/Login';
import LoadingScreen from './components/Common/LoadingScreen';

import './App.css';

// Configure dayjs
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(relativeTime);

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Main App Component
const App: React.FC = () => {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider
          theme={{
            algorithm: theme.defaultAlgorithm,
            token: {
              colorPrimary: '#1890ff',
              borderRadius: 6,
              fontFamily: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
            },
          }}
        >
          <Router>
            <div className="App">
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                
                {/* Protected Routes */}
                <Route
                  path="/*"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <Routes>
                          <Route path="/" element={<Navigate to="/dashboard" replace />} />
                          <Route path="/dashboard" element={<Dashboard />} />
                          <Route path="/cost-analysis" element={<CostAnalysis />} />
                          <Route path="/business-intelligence" element={<BusinessIntelligence />} />
                          <Route path="/cloud-accounts" element={<CloudAccounts />} />
                          <Route path="/organizations" element={<Organizations />} />
                          <Route path="/teams" element={<Teams />} />
                          <Route path="/users" element={<Users />} />
                          <Route path="/settings" element={<Settings />} />
                        </Routes>
                      </Layout>
                    </ProtectedRoute>
                  }
                />
              </Routes>
              
              {/* Global Toast Notifications */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                  success: {
                    style: {
                      background: '#10b981',
                    },
                  },
                  error: {
                    style: {
                      background: '#ef4444',
                    },
                  },
                }}
              />
            </div>
          </Router>
        </ConfigProvider>
      </QueryClientProvider>
    </Provider>
  );
};

export default App;