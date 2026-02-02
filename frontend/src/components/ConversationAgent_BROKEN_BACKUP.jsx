  const generateGeneralResponse = (message, user) => {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return `ðŸ‘‹ Hello ${user?.full_name || 'there'}! I'm your AI shopping assistant. I can help you find and compare products. Just describe what you're looking for!`;
    }

    if (lowerMessage.includes('help')) {
      return `ðŸ¤– I'm here to help! I can:\n\nâ€¢ Search for products\nâ€¢ Compare multiple items\nâ€¢ Analyze reviews and ratings\nâ€¢ Track price trends\nâ€¢ Recommend the best payment options\n\nJust tell me what product you're interested in!`;
    }

    if (lowerMessage.includes('thank')) {
      return `You're welcome! ðŸ˜Š Let me know if you need anything else!`;
    }

    return `I'm your product recommendation assistant. To help you better, please tell me what product you're looking for. For example:\n\nâ€¢ "Find gaming laptops under $1500"\nâ€¢ "Show me wireless headphones"\nâ€¢ "Compare iPhone 14 and Samsung S23"`;
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
      const response = await fetch('http://localhost:8000/conversations/clear', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
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
      search: 'ðŸ”',
      buy_plan: 'ðŸ›’',
      compare: 'ðŸ“Š',
      recommendation: 'âœ¨',
      general: 'ðŸ’¬',
      processing: 'â³',
    };
    return icons[intent] || 'ðŸ’¬';
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
          <h1>ðŸ¤– AI Shopping Assistant</h1>
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
              <span>ðŸ¤– AI Agents Working...</span>
            </div>
            <div className="active-agents">
              {activeAgents.map((agent, i) => (
                <div key={i} className="agent-chip">
                  {agent === 'Search' && 'ðŸ”'}
                  {agent === 'Review' && 'â­'}
                  {agent === 'Price' && 'ðŸ’°'}
                  {agent === 'Comparison' && 'ðŸ“Š'}
                  {agent === 'BuyPlan' && 'ðŸ’³'}
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
              <div className="welcome-icon">ðŸ¤–</div>
              <h2>AI-Powered Shopping Assistant</h2>
              <p className="welcome-subtitle">Powered by 5 Specialized AI Agents</p>

              <div className="agent-features">
                <div className="feature-card">
                  <div className="feature-icon">ðŸ”</div>
                  <div className="feature-name">Product Search</div>
                  <div className="feature-desc">Find products matching your needs</div>
                </div>
                <div className="feature-card">
                  <div className="feature-icon">â­</div>
                  <div className="feature-name">Review Analysis</div>
                  <div className="feature-desc">Analyze customer reviews & ratings</div>
                </div>
                <div className="feature-card">
                  <div className="feature-icon">ðŸ’°</div>
                  <div className="feature-name">Price Tracking</div>
                  <div className="feature-desc">Track price trends & best deals</div>
                </div>
                <div className="feature-card">
                  <div className="feature-icon">ðŸ“Š</div>
                  <div className="feature-name">Comparison</div>
                  <div className="feature-desc">Compare products side-by-side</div>
                </div>
                <div className="feature-card">
                  <div className="feature-icon">ðŸ’³</div>
                  <div className="feature-name">Buy Plan</div>
                  <div className="feature-desc">Best payment & savings options</div>
                </div>
              </div>

              <div className="example-queries">
                <h3>Try asking:</h3>
                <button
                  className="example-query"
                  onClick={() => setCurrentMessage("Find gaming laptops under $1500")}
                >
                  "Find gaming laptops under $1500"
                </button>
                <button
                  className="example-query"
                  onClick={() => setCurrentMessage("Show me wireless headphones")}
                >
                  "Show me wireless headphones"
                </button>
                <button
                  className="example-query"
                  onClick={() => setCurrentMessage("Compare best smartphones")}
                >
                  "Compare best smartphones"
                </button>
              </div>
            </div>
          ) : (
            <>
              {conversations.map((conv, index) => (
                <div key={conv.id || index} className="conversation-pair">
                  {/* User Message */}
                  <div className="message user-message">
                    <div className="message-avatar">ðŸ‘¤</div>
                    <div className="message-content">
                      <div className="message-text">{conv.user_message}</div>
                      <div className="message-meta">
                        {new Date(conv.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>

                  {/* Agent Response */}
                  <div className="message agent-message">
                    <div className="message-avatar">ðŸ¤–</div>
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
                          <div className="message-text" style={{ fontFamily: 'Consolas, Monaco, "Courier New", monospace, "Segoe UI Emoji", "Segoe UI Symbol"', whiteSpace: 'pre-wrap' }}>
                            {conv.agent_response}
                          </div>

                          {/* Product Cards */}
                          {conv.products && conv.products.length > 0 && (
                            <div className="message-products">
                              <h4>ï¿½ï¸ Recommended Products:</h4>
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
                                <h3 className="section-title">ðŸ“Š Interactive Price History Analysis</h3>
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

                          {/* Comparison Table */}
                          {conv.orchestratorData?.comparison?.available && conv.orchestratorData.comparison.full_comparison?.products && (
                            <div className="message-comparison-table">
                              <h4>âš”ï¸ Battle-Style Comparison:</h4>
                              <div className="comparison-table-container">
                                <table className="battle-comparison-table">
                                  <thead>
                                    <tr>
                                      <th>Feature</th>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <th key={product.product_id}>
                                          {product.product_name}
                                          {conv.orchestratorData.comparison.winner?.product_id === product.product_id && (
                                            <span className="winner-badge">ðŸ† Winner</span>
                                          )}
                                        </th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    <tr>
                                      <td className="feature-name">ðŸ’° Price</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_price?.product_id ? 'winner-cell' : ''}>
                                          â‚¹{product.price}
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_price?.product_id && ' âœ“'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">â­ Rating</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_rating?.product_id ? 'winner-cell' : ''}>
                                          {product.rating}/5
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_rating?.product_id && ' âœ“'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">ðŸ’Ž Value Score</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id} className={product.product_id === conv.orchestratorData.comparison.category_winners?.best_value?.product_id ? 'winner-cell' : ''}>
                                          {product.value_score ? `${(product.value_score * 100).toFixed(0)}%` : 'N/A'}
                                          {product.product_id === conv.orchestratorData.comparison.category_winners?.best_value?.product_id && ' âœ“'}
                                        </td>
                                      ))}
                                    </tr>
                                    <tr>
                                      <td className="feature-name">ðŸ“¦ Stock</td>
                                      {conv.orchestratorData.comparison.full_comparison.products.map((product) => (
                                        <td key={product.product_id}>
                                          {product.in_stock ? 'âœ… In Stock' : 'âŒ Out of Stock'}
                                        </td>
                                      ))}
                                    </tr>
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          )}

                          <div className="message-meta">
                            {new Date(conv.created_at).toLocaleTimeString()}
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
              <span className="suggestions-label">ðŸ’¡ Trending Topics:</span>
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
              {loading ? 'â³' : 'ðŸ“¤'}
            </button>
          </form>

          <div className="input-actions">
            <button className="action-btn" onClick={handleClearConversations}>
              ðŸ—‘ï¸ Clear History
            </button>
            <button className="action-btn" onClick={generateSessionId}>
              ðŸ”„ New Session
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationAgent;

