import React, { useState } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import Login from './components/Login';
import Signup from './components/Signup';
import UserProfile from './components/UserProfile';
import Wishlist from './components/Wishlist';
import SearchHistory from './components/SearchHistory';
import Recommendations from './components/Recommendations';
import ConversationAgent from './components/ConversationAgent';
import { useAuth } from './contexts/AuthContext';
import './App.css';

/**
 * Main App Component with Authentication
 */
function AppContent() {
  const { user, isAuthenticated, loading } = useAuth();
  const [showSignup, setShowSignup] = useState(false);
  const [currentPage, setCurrentPage] = useState('recommendations'); // 'recommendations', 'agent', 'wishlist', 'history', 'profile'

  // Loading state
  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner-large"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Not authenticated - show login/signup
  if (!isAuthenticated) {
    return (
      <div className="app">
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
        {renderPage()}
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
