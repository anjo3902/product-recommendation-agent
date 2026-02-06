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

  // Authenticated - show main app
  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <div className="header-brand">
            <h1>Product Recommendation</h1>
            <span className="header-subtitle">Intelligent Shopping Assistant</span>
          </div>
          <nav className="main-nav">
            <button
              className={currentPage === 'recommendations' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('recommendations')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              <span>For You</span>
            </button>
            <button
              className={currentPage === 'agent' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('agent')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              <span>AI Chat</span>
            </button>
            <button
              className={currentPage === 'wishlist' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('wishlist')}            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
              <span>Wishlist</span>
            </button>
            <button
              className={currentPage === 'history' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('history')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span>History</span>
            </button>
            <button
              className={currentPage === 'profile' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setCurrentPage('profile')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <span>Profile</span>
            </button>
          </nav>
          <div className="user-info">
            <span className="user-name">{user?.full_name || user?.username}</span>
          </div>
        </div>
      </header>

      <main className="app-main">
        <Suspense fallback={<LoadingFallback />}>
          {/* Render all pages but only show the active one - preserves state when switching tabs */}
          <div className={currentPage === 'recommendations' ? 'page-container active' : 'page-container'}>
            <Recommendations isActive={currentPage === 'recommendations'} />
          </div>
          <div className={currentPage === 'agent' ? 'page-container active' : 'page-container'}>
            <ConversationAgent isActive={currentPage === 'agent'} />
          </div>
          <div className={currentPage === 'wishlist' ? 'page-container active' : 'page-container'}>
            <Wishlist isActive={currentPage === 'wishlist'} />
          </div>
          <div className={currentPage === 'history' ? 'page-container active' : 'page-container'}>
            <SearchHistory isActive={currentPage === 'history'} />
          </div>
          <div className={currentPage === 'profile' ? 'page-container active' : 'page-container'}>
            <UserProfile isActive={currentPage === 'profile'} />
          </div>
        </Suspense>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>&copy; 2026 Product Recommendation System. All rights reserved.</p>
        </div>
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
