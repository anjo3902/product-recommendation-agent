/* eslint-disable react-hooks/exhaustive-deps */
/* Updated: 2026-02-03 - Fixed emoji icons */
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ProductCard from './ProductCard';
import PriceHistoryChart from './PriceHistoryChart';
import formatOrchestratorResponse from '../utils/formatOrchestratorResponse';
import API_BASE_URL from '../config';
import { getApiHeaders } from '../utils/api';
import './ConversationAgent.css';

/**
 * Format plain text response into styled HTML
 */
const formatTextResponse = (text) => {
  if (!text) return null;

  const lines = text.split('\n');
  const elements = [];
  let key = 0;

  lines.forEach((line, index) => {
    // Main section headers (with ====)
    if (line.includes('====')) {
      return; // Skip separator lines
    }
    
    // Section titles (ALL CAPS with spaces)
    if (line.trim().match(/^[A-Z][A-Z\s&]+$/)) {
      elements.push(
        <h3 key={key++} className="response-section-title">
          {line.trim()}
        </h3>
      );
      return;
    }

    // Subsection headers (with ----)
    if (line.includes('----')) {
      elements.push(<div key={key++} className="response-divider"></div>);
      return;
    }

    // Numbered items (1. 2. 3.)
    if (line.trim().match(/^\d+\.\s/)) {
      const content = line.trim();
      elements.push(
        <div key={key++} className="response-product-title">
          {content}
        </div>
      );
      return;
    }

    // Indented metadata (Price:, Rating:, etc.)
    if (line.trim().match(/^(Price|Rating|Reviews|Brand|Recommendation|Sentiment|Trust Score|Current|Average|Lowest|Highest|Trend|For):/) || 
        line.match(/^\s{3}(Price|Rating|Reviews|Brand|Recommendation|Sentiment|Trust Score|Current|Average|Lowest|Highest|Trend|For):/)) {
      const parts = line.split(':');
      const label = parts[0].trim();
      const value = parts.slice(1).join(':').trim();
      elements.push(
        <div key={key++} className="response-metadata">
          <span className="metadata-label">{label}:</span>
          <span className="metadata-value">{value}</span>
        </div>
      );
      return;
    }

    // Bullet points with +
    if (line.trim().startsWith('+')) {
      elements.push(
        <div key={key++} className="response-bullet-plus">
          <span className="bullet-icon">✓</span>
          {line.trim().substring(1).trim()}
        </div>
      );
      return;
    }

    // Bullet points with -
    if (line.trim().startsWith('-')) {
      elements.push(
        <div key={key++} className="response-bullet-minus">
          <span className="bullet-icon">✗</span>
          {line.trim().substring(1).trim()}
        </div>
      );
      return;
    }

    // Bullet points with *
    if (line.trim().startsWith('*')) {
      elements.push(
        <div key={key++} className="response-bullet-spec">
          <span className="spec-icon">•</span>
          {line.trim().substring(1).trim()}
        </div>
      );
      return;
    }

    // Key headers (WHAT CUSTOMERS LOVE, KEY SPECIFICATIONS, etc.)
    if (line.trim().match(/^(WHAT CUSTOMERS|KEY SPECIFICATIONS|KEY FEATURES|TECHNICAL SPECIFICATIONS|AI Recommendation|AI INSIGHTS|CATEGORY CHAMPIONS|BEST PAYMENT OPTIONS|OVERALL WINNER|REASON):/)) {
      elements.push(
        <h4 key={key++} className="response-subsection-title">
          {line.trim()}
        </h4>
      );
      return;
    }

    // Regular text with special formatting
    const trimmed = line.trim();
    if (trimmed) {
      // Check for Active Agents line
      if (trimmed.startsWith('Active Agents:')) {
        elements.push(
          <div key={key++} className="response-active-agents">
            {trimmed}
          </div>
        );
        return;
      }

      // Check for final summary lines
      if (trimmed.startsWith('Analyzed') || trimmed.startsWith('Execution Time:')) {
        elements.push(
          <div key={key++} className="response-stat-line">
            {trimmed}
          </div>
        );
        return;
      }

      // Regular paragraph
      elements.push(
        <p key={key++} className="response-paragraph">
          {trimmed}
        </p>
      );
    } else {
      // Empty line for spacing
      elements.push(<div key={key++} className="response-spacer"></div>);
    }
  });

  return elements;
};

/**
 * Conversation Agent Interface Component
 * Integrated with backend orchestrator for intelligent product recommendations
 */
const ConversationAgent = () => {
  const { token, user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [summary, setSummary] = useState(null);
  const [activeAgents, setActiveAgents] = useState([]);
  const [orchestrating, setOrchestrating] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    generateSessionId();
    fetchConversations();
    fetchSummary();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [conversations]);

  const generateSessionId = () => {
    const id = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(id);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/?limit=50`, {
        headers: getApiHeaders(token)
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      }
    } catch (err) {
      console.error('Error fetching conversations:', err);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/summary`, {
        headers: getApiHeaders(token)
      });

      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim() || loading) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    setLoading(true);
    setOrchestrating(true);

    // Add user message to UI immediately
    const tempMessage = {
      id: Date.now(),
      user_message: userMessage,
      agent_response: null,
      products: [],
      created_at: new Date().toISOString(),
      intent: 'processing',
      isLoading: true,
    };
    setConversations((prev) => [...prev, tempMessage]);
    scrollToBottom();

    try {
      // Detect if query is product-related
      const isProductQuery = detectProductQuery(userMessage);

      let agentResponse;
      let products = [];
      let intent = 'general';
      let sentiment = 'neutral';
      let orchestratorData = null;

      if (isProductQuery) {
        // Show all 5 active agents - FORCE REFRESH
        const allAgents = ['Product Search', 'Review Analyzer', 'Price Tracker', 'Comparison', 'Buy Plan'];
        console.log('🔥 ALL 5 AGENTS ACTIVE:', allAgents, 'COUNT:', allAgents.length);
        setActiveAgents(allAgents);

        // Call backend orchestrator
        const orchestratorResult = await callOrchestratorAgent(userMessage);

        if (orchestratorResult.success) {
          agentResponse = formatOrchestratorResponse(orchestratorResult);
          products = orchestratorResult.products || [];
          orchestratorData = orchestratorResult;
          intent = 'search';
          sentiment = 'positive';
        } else {
          agentResponse = orchestratorResult.error || 'Sorry, I could not process your request.';
          intent = 'error';
        }

        setActiveAgents([]);
      } else {
        // General conversation
        agentResponse = generateGeneralResponse(userMessage, user);
        intent = detectIntent(userMessage);
        sentiment = detectSentiment(userMessage);
      }

      // Save conversation to backend
      const response = await fetch(`${API_BASE_URL}/conversations/`, {
        method: 'POST',
        headers: getApiHeaders(token, { 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          session_id: sessionId,
          user_message: userMessage,
          agent_response: agentResponse,
          intent: intent,
          sentiment: sentiment,
          products_mentioned: products.map(p => p.id),
        }),
      });

      if (response.ok) {
        const savedConversation = await response.json();

        // Update the conversation with full data
        setConversations((prev) => {
          const updated = [...prev];
          const index = updated.findIndex(c => c.id === tempMessage.id);
          if (index !== -1) {
            updated[index] = {
              ...savedConversation,
              products: products,
              orchestratorData: orchestratorData,
              isLoading: false,
            };
          }
          return updated;
        });

        fetchSummary();
      }
    } catch (err) {
      console.error('Error sending message:', err);

      // Update with error message
      setConversations((prev) => {
        const updated = [...prev];
        const index = updated.findIndex(c => c.id === tempMessage.id);
        if (index !== -1) {
          updated[index] = {
            ...updated[index],
            agent_response: 'Sorry, I encountered an error. Please try again.',
            intent: 'error',
            isLoading: false,
          };
        }
        return updated;
      });
    } finally {
      setLoading(false);
      setOrchestrating(false);
      setActiveAgents([]);
      scrollToBottom();
    }
  };

  const detectProductQuery = (message) => {
    const productKeywords = [
      'find', 'search', 'looking for', 'show me', 'recommend', 'suggest',
      'buy', 'purchase', 'compare', 'laptop', 'phone', 'headphone', 'camera',
      'product', 'price', 'best', 'cheap', 'under', 'below', 'reviews'
    ];

    const lowerMessage = message.toLowerCase();
    return productKeywords.some(keyword => lowerMessage.includes(keyword));
  };

  const callOrchestratorAgent = async (query) => {
    console.log('🔍 Calling orchestrator with query:', query);
    console.log('🔑 Using token:', token ? 'Yes' : 'No');
    console.log('📡 API URL:', `${API_BASE_URL}/api/orchestrate/simple`);
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const requestBody = { query };
      console.log('📤 Request body:', JSON.stringify(requestBody));

      const response = await fetch(`${API_BASE_URL}/api/orchestrate/simple`, {
        method: 'POST',
        headers: getApiHeaders(token, {
          'Content-Type': 'application/json; charset=UTF-8',
          'Accept': 'application/json; charset=UTF-8',
        }),
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      console.log('📥 Response status:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Backend error:', response.status, errorText);
        return {
          success: false,
          error: `Backend error (${response.status}): ${errorText}`,
        };
      }

      const text = await response.text();
      console.log('📥 Response text length:', text.length);
      const result = JSON.parse(text);
      console.log('✅ Parsed result:', result.success, 'Products:', result.products?.length);

      return result;
    } catch (err) {
      console.error('❌ Orchestrator error:', err);
      return {
        success: false,
        error: `Error: ${err.message}`,
      };
    }
  };

  const generateGeneralResponse = (message, user) => {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return `Hello ${user?.full_name || 'there'}! I'm your AI shopping assistant. I can help you find and compare products. Just describe what you're looking for!`;
    }

    if (lowerMessage.includes('help')) {
      return `🤖 I'm here to help! I can:\n\n* Search for products\n* Compare multiple items\n* Analyze reviews and ratings\n* Track price trends\n* Recommend the best payment options\n\nJust tell me what product you're interested in!`;
    }

    if (lowerMessage.includes('thank')) {
      return `You're welcome! Let me know if you need anything else!`;
    }

    return `I'm your product recommendation assistant. To help you better, please tell me what product you're looking for. For example:\n\n* "Find gaming laptops under $1500"\n* "Show me wireless headphones"\n* "Compare iPhone 14 and Samsung S23"`;
  };

  const detectIntent = (message) => {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('search') || lowerMessage.includes('find') || lowerMessage.includes('show')) {
      return 'search';
    }
    if (lowerMessage.includes('compare') || lowerMessage.includes('vs') || lowerMessage.includes('difference')) {
      return 'compare';
    }
    if (lowerMessage.includes('buy') || lowerMessage.includes('purchase') || lowerMessage.includes('order')) {
      return 'buy_plan';
    }
    if (lowerMessage.includes('recommend') || lowerMessage.includes('suggest')) {
      return 'recommendation';
    }

    return 'general';
  };

  const detectSentiment = (message) => {
    const lowerMessage = message.toLowerCase();

    const positiveWords = ['great', 'love', 'excellent', 'amazing', 'perfect', 'good', 'thanks'];
    const negativeWords = ['bad', 'hate', 'terrible', 'awful', 'worst', 'disappointed'];

    const hasPositive = positiveWords.some(word => lowerMessage.includes(word));
    const hasNegative = negativeWords.some(word => lowerMessage.includes(word));

    if (hasPositive && !hasNegative) return 'positive';
    if (hasNegative && !hasPositive) return 'negative';
    return 'neutral';
  };

  const handleClearConversations = async () => {
    if (!window.confirm('Are you sure you want to clear all conversations?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/conversations/clear`, {
        method: 'DELETE',
        headers: getApiHeaders(token)
      });

      if (response.ok) {
        setConversations([]);
        setSummary(null);
        generateSessionId();
        alert('Conversations cleared!');
      }
    } catch (err) {
      console.error('Error clearing conversations:', err);
    }
  };

  const getIntentIcon = (intent) => {
    const icons = {
      search: '[Search]',
      buy_plan: '🛒',
      compare: '[Compare]',
      recommendation: '⭐',
      general: '[Chat]',
      processing: '[...]',
    };
    return icons[intent] || '[Chat]';
  };

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: '#48bb78',
      negative: '#f56565',
      neutral: '#718096',
    };
    return colors[sentiment] || '#718096';
  };

  return (
    <div className="conversation-agent-container">
      {/* Header */}
      <div className="agent-header">
        <div className="header-content">
          <h1>🤖 AI Shopping Assistant</h1>
          <p>Chat with our intelligent agent for personalized shopping help</p>
        </div>
        {summary && (
          <div className="summary-card">
            <div className="summary-stat">
              <span className="summary-value">{summary.total_conversations}</span>
              <span className="summary-label">Conversations</span>
            </div>
            <div className="summary-stat">
              <span className="summary-value">{summary.total_sessions}</span>
              <span className="summary-label">Sessions</span>
            </div>
          </div>
        )}
      </div>

      {/* Conversation Area */}
      <div className="conversation-area">
        {/* Agent Activity Indicator */}
        {orchestrating && activeAgents.length > 0 && (
          <div className="agent-activity-bar">
            <div className="activity-header">
              <div className="pulse-indicator"></div>
              <span>🤖 ALL 5 AGENTS ACTIVE ({activeAgents.length}/5)</span>
            </div>
            <div className="active-agents">
              {console.log('🔥 RENDERING AGENTS:', activeAgents)}
              {activeAgents.map((agent, i) => (
                <div key={i} className="agent-chip">
                  {agent === 'Product Search' && '🔍'}
                  {agent === 'Review Analyzer' && '⭐'}
                  {agent === 'Price Tracker' && '💰'}
                  {agent === 'Comparison' && '⚖️'}
                  {agent === 'Buy Plan' && '🛒'}
                  {' '}{agent}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="messages-container">
          {conversations.length === 0 ? (
            <div className="welcome-message">
              <span className="icon-badge icon-robot" style={{fontSize: '64px', marginBottom: '20px'}}>🤖</span>
              <h2>AI-Powered Shopping Assistant</h2>
              <p className="welcome-subtitle">Powered by 5 Specialized AI Agents</p>

              <div className="agent-features">
                <div className="feature-card">
                  <span className="icon-badge icon-search">🔍</span>
                  <div className="feature-name">Product Search</div>
                  <div className="feature-desc">Find products matching your needs</div>
                </div>
                <div className="feature-card">
                  <span className="icon-badge icon-star">⭐</span>
                  <div className="feature-name">Review Analysis</div>
                  <div className="feature-desc">Analyze customer reviews & ratings</div>
                </div>
                <div className="feature-card">
                  <span className="icon-badge icon-money">💰</span>
                  <div className="feature-name">Price Tracking</div>
                  <div className="feature-desc">Track price trends & best deals</div>
                </div>
                <div className="feature-card">
                  <span className="icon-badge icon-balance">⚖️</span>
                  <div className="feature-name">Comparison</div>
                  <div className="feature-desc">Compare products side-by-side</div>
                </div>
                <div className="feature-card">
                  <span className="icon-badge icon-cart">🛒</span>
                  <div className="feature-name">Buy Plan</div>
                  <div className="feature-desc">Best payment & savings options</div>
                </div>
              </div>

              <div className="example-queries">
                <h3>Try asking:</h3>
                <button
                  className="example-query"
                  onClick={() => setCurrentMessage("Find gaming laptops under ₹80000")}
                >
                  "Find gaming laptops under ₹80000"
                </button>
                <button
                  className="example-query"
                  onClick={() => setCurrentMessage("Show me wireless headphones under ₹5000")}
                >
                  "Show me wireless headphones under ₹5000"
                </button>
                <button
                  className="example-query"
                  onClick={() => setCurrentMessage("Compare iPhone 15 vs Samsung S24")}
                >
                  "Compare iPhone 15 vs Samsung S24"
                </button>
              </div>
            </div>
          ) : (
            <>
              {conversations.map((conv, index) => (
                <div key={conv.id || index} className="conversation-pair">
                  {/* User Message */}
                  <div className="message user-message">
                    <div className="message-avatar">👤</div>
                    <div className="message-content">
                      <div className="message-text">{conv.user_message}</div>
                      <div className="message-meta">
                        {new Date(conv.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })}
                      </div>
                    </div>
                  </div>

                  {/* Agent Response */}
                  <div className="message agent-message">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content">
                      {conv.isLoading ? (
                        <div className="agent-loading">
                          <div className="loading-spinner"></div>
                          <p>Orchestrating agents for best results...</p>
                        </div>
                      ) : (
                        <>
                          <div className="message-header">
                            <span className="intent-badge">
                              {getIntentIcon(conv.intent)} {conv.intent}
                            </span>
                            {conv.sentiment && (
                              <span
                                className="sentiment-indicator"
                                style={{ background: getSentimentColor(conv.sentiment) }}
                              />
                            )}
                          </div>
                          <div className="message-text formatted-response">
                            {formatTextResponse(conv.agent_response)}
                          </div>

                          {/* Product Cards */}
                          {conv.products && conv.products.length > 0 && (
                            <div className="message-products">
                              <h4>[+] Recommended Products:</h4>
                              <div className="products-grid-mini">
                                {conv.products.map((product) => (
                                  <ProductCard
                                    key={product.id}
                                    product={product}
                                    compact={true}
                                    onAddToWishlist={(p) => {
                                      // Add to wishlist logic
                                      console.log('Add to wishlist:', p);
                                    }}
                                    onViewDetails={(p) => {
                                      console.log('View details:', p);
                                    }}
                                  />
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Professional Price History Charts - Similar to PriceHistory.app */}
                          {conv.orchestratorData?.products && conv.orchestratorData.products.some(p => {
                            const pd = p.price_tracking || p.price_analysis;
                            return pd?.chart_data?.data?.length > 0;
                          }) && (
                              <div className="message-price-history-section">
                                <h3 className="section-title">[Chart] Interactive Price History Analysis</h3>
                                {conv.orchestratorData.products.map((product) => {
                                  // Access price data - check both fields for backward compatibility
                                  const priceData = product.price_tracking || product.price_analysis;
                                  if (!priceData?.chart_data || !priceData.chart_data.data || priceData.chart_data.data.length === 0) return null;

                                  return (
                                    <PriceHistoryChart
                                      key={product.id}
                                      productName={product.name}
                                      priceData={priceData}
                                    />
                                  );
                                })}
                              </div>
                            )}

                          {/* Comparison Table - v2.0 Enhanced */}
                          {conv.orchestratorData?.comparison?.available && conv.orchestratorData.comparison.full_comparison?.products && (
                            <div className="message-comparison-table">
                              <h4>⚖️ Detailed Product Comparison (Enhanced)</h4>
                              <div className="comparison-table-container">
                                <table className="battle-comparison-table">
                                  <thead>
                                    <tr>
                                      <th className="feature-column">Feature</th>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product, idx) => (
                                        <th key={product.product_id} className={`product-column ${
                                          conv.orchestratorData.comparison.winner?.product_id === product.product_id ? 'best-choice' : 
                                          conv.orchestratorData.comparison.category_winners?.best_price?.product_id === product.product_id ? 'best-price' : ''
                                        }`}>
                                          {conv.orchestratorData.comparison.winner?.product_id === product.product_id && (
                                            <div className="badge-tag best-choice-badge">Best Choice</div>
                                          )}
                                          {conv.orchestratorData.comparison.category_winners?.best_price?.product_id === product.product_id && 
                                           conv.orchestratorData.comparison.winner?.product_id !== product.product_id && (
                                            <div className="badge-tag best-price-badge">Best Price</div>
                                          )}
                                          <div className="product-header">
                                            <div className="product-image-placeholder">📱</div>
                                            <div className="product-title">{product.product_name}</div>
                                          </div>
                                        </th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    <tr className="preview-row">
                                      <td className="feature-name">Preview</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className="product-preview">
                                          {product.image_url ? (
                                            <img src={product.image_url} alt={product.product_name} className="comparison-product-image" />
                                          ) : (
                                            <div className="no-image">No Image</div>
                                          )}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr className="title-row">
                                      <td className="feature-name">Title</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className="product-title-cell">
                                          {product.product_name}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">Brand</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id}>
                                          {product.brand || product.product_name.split(' ')[0]}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">Category</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id}>
                                          {product.category || 'Electronics'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr className="highlight-row">
                                      <td className="feature-name">💰 Price</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_price?.product_id ? 'winner-cell' : ''}>
                                          <strong>₹{product.price?.toLocaleString()}</strong>
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_price?.product_id && ' ✓'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">⭐ Rating</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_rating?.product_id ? 'winner-cell' : ''}>
                                          {'★'.repeat(Math.floor(product.rating))}{'☆'.repeat(5 - Math.floor(product.rating))} ({product.rating}/5)
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_rating?.product_id && ' ✓'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">📊 Value Score</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_value?.product_id ? 'winner-cell' : ''}>
                                          {product.value_score ? `${(product.value_score * 100).toFixed(0)}%` : 'N/A'}
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_value?.product_id && ' ✓'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">📦 Stock Status</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.in_stock ? 'in-stock' : 'out-of-stock'}>
                                          {product.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">🚚 Delivery</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id}>
                                          {product.delivery_time || 'Standard Delivery'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">🔧 Specifications</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id}>
                                          {product.specifications ? (
                                            <ul className="spec-list">
                                              {Object.entries(product.specifications).slice(0, 3).map(([key, value]) => (
                                                <li key={key}>{key}: {value}</li>
                                              ))}
                                            </ul>
                                          ) : (
                                            product.description?.substring(0, 100) + '...' || 'No details available'
                                          )}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">💬 Customer Reviews</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id}>
                                          {product.review_count ? `${product.review_count} reviews` : 'No reviews yet'}
                                        </td>
                                      ))}
                                    </tr>
                                  </tbody>
                                </table>
                              </div>
                              {conv.orchestratorData.comparison.recommendation && (
                                <div className="comparison-recommendation">
                                  <h5>💡 AI Recommendation:</h5>
                                  <p>{conv.orchestratorData.comparison.recommendation}</p>
                                </div>
                              )}
                            </div>
                          )}

                          <div className="message-meta">
                            {new Date(conv.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="input-area">
          {summary && summary.top_intents && summary.top_intents.length > 0 && (
            <div className="quick-suggestions">
              <span className="suggestions-label">[Tip] Trending Topics:</span>
              {summary.top_intents.slice(0, 3).map((intent, i) => (
                <button
                  key={i}
                  className="suggestion-chip"
                  onClick={() => setCurrentMessage(`Tell me more about ${intent}`)}
                >
                  {getIntentIcon(intent)} {intent}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={handleSendMessage} className="input-form">
            <input
              type="text"
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              placeholder="Type your message here..."
              className="message-input"
              disabled={loading}
            />
            <button
              type="submit"
              className="send-button"
              disabled={loading || !currentMessage.trim()}
            >
              {loading ? '[...]' : 'Send'}
            </button>
          </form>

          <div className="input-actions">
            <button className="action-btn" onClick={handleClearConversations}>
              🗑️ Clear History
            </button>
            <button className="action-btn" onClick={generateSessionId}>
              ✨ New Session
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationAgent;
