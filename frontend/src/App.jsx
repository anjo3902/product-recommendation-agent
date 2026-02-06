import React, { useState, Suspense, lazy } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './contexts/AuthContext';
import './App.css';

// Lazy load heavy components for faster initial load
const Login = lazy(() => import('./components/Login'));
const Signup = lazy(() => import('./components/Signup'));
const UserProfile = lazy(() => import('./components/UserProfile'));
const Wishlist = lazy(() => import('./components/Wishlist'));
const SearchHistory = lazy(() => import('./components/SearchHistory'));
const Recommendations = lazy(() => import('./components/Recommendations'));
const ConversationAgent = lazy(() => import('./components/ConversationAgent'));

// Loading fallback component
const LoadingFallback = () => (
  <div className="app-loading">
    <div className="spinner-large"></div>
    <p>Loading...</p>
  </div>
);

/**
 * Main App Component with Authentication
 */
function AppContent() {
  const { user, isAuthenticated, loading } = useAuth();
  const [showSignup, setShowSignup] = useState(false);
  const [currentPage, setCurrentPage] = useState('recommendations'); // 'recommendations', 'agent', 'wishlist', 'history', 'profile'

  // OPTIMIZATION: Show login immediately if not authenticated
  // Only show loading for authenticated users
  if (loading && isAuthenticated !== false) {
    // Still checking auth - but this should be fast (max 1s)
    return null; // The initial loader in index.html will handle this
  }

  // Not authenticated - show login/signup
  if (!isAuthenticated) {
    return (
      <div className="app">
        <Suspense fallback={<LoadingFallback />}>
          {showSignup ? (
            <Signup
              onSwitchToLogin={() => setShowSignup(false)}
              onSignupSuccess={() => {
                // User is automatically logged in after signup
              }}
            />
          ) : (
            <Login
              onSwitchToSignup={() => setShowSignup(true)}
              onLoginSuccess={() => {
                // User is automatically logged in
              }}
            />
          )}
        </Suspense>
      </div>
    );
  }

  // Render current page
  const renderPage = () => {
    switch (currentPage) {
      case 'recommendations':
        return <Recommendations />;
      case 'agent':
        return <ConversationAgent />;
      case 'wishlist':
        return <Wishlist />;
      case 'history':
        return <SearchHistory />;
      case 'profile':
        return <UserProfile />;
      default:
        return <Recommendations />;
    }
  };

  // Authenticated - show main app
  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>🛍️ AI-Powered Shopping</h1>
          <nav className="main-nav">
            <button
              className={currentPage === 'recommendations' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('recommendations')}
            >
              ✨ For You
            </button>
            <button
              className={currentPage === 'agent' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('agent')}
            >
              🤖 AI Assistant
            </button>
            <button
              className={currentPage === 'wishlist' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('wishlist')}
            >
              ❤️ Wishlist
            </button>
            <button
              className={currentPage === 'history' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('history')}
            >
              🔍 History
            </button>
            <button
              className={currentPage === 'profile' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('profile')}
            >
              👤 Profile
            </button>
          </nav>
          <div className="user-info">
            <span>Welcome, {user?.full_name || user?.username}!</span>
          </div>
        </div>
      </header>

      <main className="app-main">
        <Suspense fallback={<LoadingFallback />}>
          {renderPage()}
        </Suspense>
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 Product Recommendation System. All rights reserved.</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
