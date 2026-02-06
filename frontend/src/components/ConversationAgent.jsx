/* eslint-disable react-hooks/exhaustive-deps */
/* Updated: 2026-02-03 - Fixed emoji icons */
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ProductCard from './ProductCard';
import ProductDetailsModal from './ProductDetailsModal';
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
          <span className="bullet-icon">•</span>
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
  const [selectedProduct, setSelectedProduct] = useState(null);
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
        console.log('[AGENTS] ALL 5 ACTIVE:', allAgents, 'COUNT:', allAgents.length);
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
    console.log('[ORCHESTRATOR] Calling with query:', query);
    console.log('[AUTH] Using token:', token ? 'Yes' : 'No');
    console.log('[API] URL:', `${API_BASE_URL}/api/orchestrate/simple`);
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const requestBody = { query };
      console.log('[REQUEST] Body:', JSON.stringify(requestBody));

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

      console.log('[RESPONSE] Status:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[ERROR] Backend error:', response.status, errorText);
        return {
          success: false,
          error: `Backend error (${response.status}): ${errorText}`,
        };
      }

      const text = await response.text();
      console.log('[RESPONSE] Text length:', text.length);
      const result = JSON.parse(text);
      console.log('✅ Parsed result:', result.success, 'Products:', result.products?.length);

      return result;
    } catch (err) {
      console.error('[ERROR] Orchestrator error:', err);
      return {
        success: false,
        error: `Error: ${err.message}`,
      };
    }
  };

  const generateGeneralResponse = (message, user) => {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return `Hello ${user?.full_name || 'there'}! I'm SmartBuy AI, your intelligent shopping assistant. I can help you find and compare products, track prices, and make smart buying decisions. Just describe what you're looking for!`;
    }

    if (lowerMessage.includes('help')) {
      return `I'm here to help! I can:\n\n* Search for products\n* Compare multiple items\n* Analyze reviews and ratings\n* Track price trends\n* Recommend the best payment options\n\nJust tell me what product you're interested in!`;
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
    const intentLower = intent?.toLowerCase() || '';
    
    if (intentLower.includes('search')) {
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
      );
    }
    if (intentLower.includes('buy') || intentLower.includes('plan')) {
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="9" cy="21" r="1"/>
          <circle cx="20" cy="21" r="1"/>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
        </svg>
      );
    }
    if (intentLower.includes('compar')) {
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <line x1="9" y1="3" x2="9" y2="21"/>
        </svg>
      );
    }
    if (intentLower.includes('recommend')) {
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
      );
    }
    // General chat or processing
    return (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    );
  };

  const getAgentIcon = (agentName) => {
    const name = agentName.toLowerCase();
    
    if (name.includes('product') || name.includes('search')) {
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
      );
    }
    if (name.includes('review') || name.includes('analyz')) {
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
      );
    }
    if (name.includes('price') || name.includes('track')) {
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
        </svg>
      );
    }
    if (name.includes('compar')) {
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <line x1="9" y1="3" x2="9" y2="21"/>
        </svg>
      );
    }
    if (name.includes('buy') || name.includes('plan')) {
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="9" cy="21" r="1"/>
          <circle cx="20" cy="21" r="1"/>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
        </svg>
      );
    }
    return null;
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
          <h1>SmartBuy AI</h1>
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
              <span>ALL 5 AGENTS ACTIVE ({activeAgents.length}/5)</span>
            </div>
            <div className="active-agents">
              {console.log('[AGENTS] RENDERING:', activeAgents)}
              {activeAgents.map((agent, i) => (
                <div key={i} className="agent-chip">
                  <span className="agent-badge">{getAgentIcon(agent)}</span>
                  {agent}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="messages-container">
          {conversations.length === 0 ? (
            <div className="welcome-message">
              <div className="welcome-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="11" width="18" height="10" rx="2"/>
                  <circle cx="12" cy="5" r="2"/>
                  <path d="M12 7v4"/>
                  <line x1="8" y1="16" x2="8" y2="16"/>
                  <line x1="16" y1="16" x2="16" y2="16"/>
                </svg>
              </div>
              <h2>AI-Powered Shopping Assistant</h2>
              <p className="welcome-subtitle">Powered by 5 Specialized AI Agents</p>

              <div className="agent-features">
                <div className="feature-card">
                  <div className="icon-badge">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="11" cy="11" r="8"/>
                      <path d="m21 21-4.35-4.35"/>
                    </svg>
                  </div>
                  <div className="feature-name">Product Search</div>
                  <div className="feature-desc">Find products matching your needs</div>
                </div>
                <div className="feature-card">
                  <div className="icon-badge">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                  </div>
                  <div className="feature-name">Review Analysis</div>
                  <div className="feature-desc">Analyze customer reviews & ratings</div>
                </div>
                <div className="feature-card">
                  <div className="icon-badge">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                    </svg>
                  </div>
                  <div className="feature-name">Price Tracking</div>
                  <div className="feature-desc">Track price trends & best deals</div>
                </div>
                <div className="feature-card">
                  <div className="icon-badge">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                      <line x1="9" y1="3" x2="9" y2="21"/>
                    </svg>
                  </div>
                  <div className="feature-name">Comparison</div>
                  <div className="feature-desc">Compare products side-by-side</div>
                </div>
                <div className="feature-card">
                  <div className="icon-badge">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="9" cy="21" r="1"/>
                      <circle cx="20" cy="21" r="1"/>
                      <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                    </svg>
                  </div>
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
                    <div className="message-avatar user-avatar">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                      </svg>
                    </div>
                    <div className="message-content">
                      <div className="message-text">{conv.user_message}</div>
                      <div className="message-meta">
                        {new Date(conv.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })}
                      </div>
                    </div>
                  </div>

                  {/* Agent Response */}
                  <div className="message agent-message">
                    <div className="message-avatar ai-avatar">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="3" y="11" width="18" height="10" rx="2"/>
                        <circle cx="12" cy="5" r="2"/>
                        <path d="M12 7v4"/>
                        <line x1="8" y1="16" x2="8" y2="16"/>
                        <line x1="16" y1="16" x2="16" y2="16"/>
                      </svg>
                    </div>
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
                              <h4>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '8px', verticalAlign: 'middle'}}>
                                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                                </svg>
                                Recommended Products:
                              </h4>
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
                                    onViewDetails={setSelectedProduct}
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
                                <h3 className="section-title">
                                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '8px', verticalAlign: 'middle'}}>
                                    <line x1="18" y1="20" x2="18" y2="10"/>
                                    <line x1="12" y1="20" x2="12" y2="4"/>
                                    <line x1="6" y1="20" x2="6" y2="14"/>
                                  </svg>
                                  Interactive Price History Analysis
                                </h3>
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
                                            <div className="product-image-placeholder">
                                              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
                                                <line x1="3" y1="6" x2="21" y2="6"/>
                                                <path d="M16 10a4 4 0 0 1-8 0"/>
                                              </svg>
                                            </div>
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
                                      <td className="feature-name">Price</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_price?.product_id ? 'winner-cell' : ''}>
                                          <strong>₹{product.price?.toLocaleString()}</strong>
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_price?.product_id && ' (Best)'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">Rating</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_rating?.product_id ? 'winner-cell' : ''}>
                                          {'★'.repeat(Math.floor(product.rating))}{'☆'.repeat(5 - Math.floor(product.rating))} ({product.rating}/5)
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_rating?.product_id && ' (Best)'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">Value Score</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_value?.product_id ? 'winner-cell' : ''}>
                                          {product.value_score ? `${(product.value_score * 100).toFixed(0)}%` : 'N/A'}
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_value?.product_id && ' (Best)'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">Stock Status</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.in_stock ? 'in-stock' : 'out-of-stock'}>
                                          {product.in_stock ? 'In Stock' : 'Out of Stock'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">Delivery</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id}>
                                          {product.delivery_time || 'Standard Delivery'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">Specifications</td>
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
                                      <td className="feature-name">Customer Reviews</td>
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
                                  <h5>AI Recommendation:</h5>
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
              {loading ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="spinning">
                  <line x1="12" y1="2" x2="12" y2="6"/>
                  <line x1="12" y1="18" x2="12" y2="22"/>
                  <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
                  <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                  <line x1="2" y1="12" x2="6" y2="12"/>
                  <line x1="18" y1="12" x2="22" y2="12"/>
                  <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
                  <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
                </svg>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"/>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                  </svg>
                  <span>Send</span>
                </>
              )}
            </button>
          </form>

          <div className="input-actions">
            <button className="action-btn" onClick={handleClearConversations}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              <span>Clear History</span>
            </button>
            <button className="action-btn" onClick={generateSessionId}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
              <span>New Session</span>
            </button>
          </div>
        </div>
      </div>

      {/* Product Details Modal */}
      {selectedProduct && (
        <ProductDetailsModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}
    </div>
  );
};

export default ConversationAgent;
