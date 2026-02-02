// frontend/src/components/SearchHistory.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './SearchHistory.css';

const SearchHistory = () => {
  const { token } = useAuth();
  const [searchHistory, setSearchHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);

  const API_BASE_URL = 'http://localhost:8000';

  // Fetch search history
  useEffect(() => {
    fetchSearchHistory();
    fetchStats();
  }, []);

  const fetchSearchHistory = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(`${API_BASE_URL}/preferences/search-history`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch search history');
      }

      const data = await response.json();
      setSearchHistory(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching search history:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/preferences/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const handleDeleteItem = async (historyId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/preferences/search-history/${historyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete search history item');
      }

      // Update UI
      setSearchHistory(searchHistory.filter(item => item.id !== historyId));
      fetchStats(); // Refresh stats
    } catch (err) {
      setError(err.message);
      console.error('Error deleting item:', err);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to clear all search history? This cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/preferences/search-history`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to clear search history');
      }

      // Update UI
      setSearchHistory([]);
      fetchStats(); // Refresh stats
    } catch (err) {
      setError(err.message);
      console.error('Error clearing history:', err);
    }
  };

  const handleSearchAgain = (query) => {
    // This would trigger a new search with the query
    // You can integrate this with your search functionality
    console.log('Searching for:', query);
    alert(`This would search for: "${query}"\n\nIntegrate this with your product search component.`);
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const groupSearchesByDate = () => {
    const grouped = {
      today: [],
      yesterday: [],
      thisWeek: [],
      older: []
    };

    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterdayStart = new Date(todayStart);
    yesterdayStart.setDate(yesterdayStart.getDate() - 1);
    const weekStart = new Date(todayStart);
    weekStart.setDate(weekStart.getDate() - 7);

    searchHistory.forEach(item => {
      const itemDate = new Date(item.search_timestamp);
      
      if (itemDate >= todayStart) {
        grouped.today.push(item);
      } else if (itemDate >= yesterdayStart) {
        grouped.yesterday.push(item);
      } else if (itemDate >= weekStart) {
        grouped.thisWeek.push(item);
      } else {
        grouped.older.push(item);
      }
    });

    return grouped;
  };

  if (loading) {
    return (
      <div className="search-history-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading search history...</p>
        </div>
      </div>
    );
  }

  const groupedSearches = groupSearchesByDate();

  return (
    <div className="search-history-container">
      <div className="history-header">
        <div className="header-left">
          <h1>Search History</h1>
          {stats && (
            <p className="history-count">{stats.search_history_count} total searches</p>
          )}
        </div>
        {searchHistory.length > 0 && (
          <button className="btn-clear-all" onClick={handleClearAll}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Clear All
          </button>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {searchHistory.length === 0 ? (
        <div className="empty-history">
          <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h2>No search history</h2>
          <p>Your searches will appear here</p>
        </div>
      ) : (
        <div className="history-content">
          {groupedSearches.today.length > 0 && (
            <div className="history-section">
              <h3 className="section-title">Today</h3>
              <div className="history-list">
                {groupedSearches.today.map(item => (
                  <SearchHistoryItem
                    key={item.id}
                    item={item}
                    onDelete={handleDeleteItem}
                    onSearchAgain={handleSearchAgain}
                    formatDateTime={formatDateTime}
                  />
                ))}
              </div>
            </div>
          )}

          {groupedSearches.yesterday.length > 0 && (
            <div className="history-section">
              <h3 className="section-title">Yesterday</h3>
              <div className="history-list">
                {groupedSearches.yesterday.map(item => (
                  <SearchHistoryItem
                    key={item.id}
                    item={item}
                    onDelete={handleDeleteItem}
                    onSearchAgain={handleSearchAgain}
                    formatDateTime={formatDateTime}
                  />
                ))}
              </div>
            </div>
          )}

          {groupedSearches.thisWeek.length > 0 && (
            <div className="history-section">
              <h3 className="section-title">This Week</h3>
              <div className="history-list">
                {groupedSearches.thisWeek.map(item => (
                  <SearchHistoryItem
                    key={item.id}
                    item={item}
                    onDelete={handleDeleteItem}
                    onSearchAgain={handleSearchAgain}
                    formatDateTime={formatDateTime}
                  />
                ))}
              </div>
            </div>
          )}

          {groupedSearches.older.length > 0 && (
            <div className="history-section">
              <h3 className="section-title">Older</h3>
              <div className="history-list">
                {groupedSearches.older.map(item => (
                  <SearchHistoryItem
                    key={item.id}
                    item={item}
                    onDelete={handleDeleteItem}
                    onSearchAgain={handleSearchAgain}
                    formatDateTime={formatDateTime}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {stats && stats.recent_searches.length > 0 && (
        <div className="frequent-searches">
          <h3>Frequent Searches</h3>
          <div className="search-tags">
            {[...new Set(stats.recent_searches)].slice(0, 10).map((query, index) => (
              <button
                key={index}
                className="search-tag"
                onClick={() => handleSearchAgain(query)}
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Search History Item Component
const SearchHistoryItem = ({ item, onDelete, onSearchAgain, formatDateTime }) => {
  return (
    <div className="history-item">
      <div className="item-icon">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      
      <div className="item-content">
        <div className="query-text">{item.query}</div>
        <div className="item-meta">
          <span className="timestamp">{formatDateTime(item.search_timestamp)}</span>
          {item.results_count !== null && (
            <>
              <span className="separator">•</span>
              <span className="results-count">{item.results_count} results</span>
            </>
          )}
          {item.product_name && (
            <>
              <span className="separator">•</span>
              <span className="clicked-product">Clicked: {item.product_name}</span>
            </>
          )}
        </div>
      </div>

      <div className="item-actions">
        <button
          className="btn-search-again"
          onClick={() => onSearchAgain(item.query)}
          title="Search again"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        <button
          className="btn-delete"
          onClick={() => onDelete(item.id)}
          title="Delete"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default SearchHistory;
