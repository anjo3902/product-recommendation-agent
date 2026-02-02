"""
FastAPI Application - Product Recommendation System
Main entry point for the application server
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.routes.products import router as products_router
from src.routes.reviews import router as reviews_router
from src.routes.prices import router as prices_router
from src.routes.comparisons import router as comparisons_router
from src.routes.buyplan import router as buyplan_router
from src.routes.orchestrator import router as orchestrator_router
from src.routes.auth import router as auth_router  # Authentication routes
from src.routes.profile import router as profile_router  # User profile routes
from src.routes.preferences import router as preferences_router  # User preferences (wishlist, history)
from src.routes.conversations import router as conversations_router  # Conversation history (agent memory)
from src.routes.recommendations import router as recommendations_router  # AI-powered recommendations

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Product Recommendation System",
    description="AI-powered product search and recommendations using Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",  # Vercel deployments
        "https://*.ngrok-free.app",  # ngrok free tier
        "https://*.ngrok.io",  # ngrok legacy
        "*"  # Allow all for development (remove in production if needed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)  # Authentication (signup/login)
app.include_router(profile_router)  # User profile management
app.include_router(preferences_router)  # User preferences (wishlist, search history)
app.include_router(conversations_router)  # Conversation history (agent memory)
app.include_router(recommendations_router)  # AI-powered recommendations
app.include_router(products_router)
app.include_router(reviews_router)
app.include_router(prices_router)
app.include_router(comparisons_router)
app.include_router(buyplan_router)
app.include_router(orchestrator_router)  # Master coordinator


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Product Recommendation System API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            
            # 🔐 AUTHENTICATION ENDPOINTS
            "signup": "POST /auth/signup",  # Create new account
            "login": "POST /auth/login",  # Login and get token
            "me": "GET /auth/me",  # Get current user info (requires auth)
            "logout": "POST /auth/logout",  # Logout
            "verify_token": "POST /auth/verify-token",  # Verify token validity
            
            # 👤 USER PROFILE ENDPOINTS
            "get_profile": "GET /profile/",  # Get profile info (requires auth)
            "update_profile": "PATCH /profile/",  # Update profile (requires auth)
            "change_password": "POST /profile/change-password",  # Change password (requires auth)
            "delete_account": "DELETE /profile/",  # Delete account (requires auth)
            "user_stats": "GET /profile/stats",  # Get user statistics (requires auth)
            
            # ⭐ USER PREFERENCES ENDPOINTS
            "add_to_wishlist": "POST /preferences/wishlist",  # Add product to wishlist (requires auth)
            "get_wishlist": "GET /preferences/wishlist",  # Get user wishlist (requires auth)
            "remove_from_wishlist": "DELETE /preferences/wishlist/{item_id}",  # Remove from wishlist (requires auth)
            "check_in_wishlist": "GET /preferences/wishlist/check/{product_id}",  # Check if product in wishlist (requires auth)
            "add_search_history": "POST /preferences/search-history",  # Record search (requires auth)
            "get_search_history": "GET /preferences/search-history",  # Get search history (requires auth)
            "clear_search_history": "DELETE /preferences/search-history",  # Clear all search history (requires auth)
            "preferences_stats": "GET /preferences/stats",  # Get preferences statistics (requires auth)
            
            # 💬 CONVERSATION HISTORY ENDPOINTS (Agent Memory)
            "create_conversation": "POST /conversations/",  # Record conversation (requires auth)
            "get_conversations": "GET /conversations/",  # Get conversation history (requires auth)
            "get_conversation_context": "GET /conversations/context",  # Get recent context for agent (requires auth)
            "get_conversation_summary": "GET /conversations/summary",  # Get conversation statistics (requires auth)
            "clear_conversations": "DELETE /conversations/",  # Clear all conversations (requires auth)
            
            # 🤖 AI RECOMMENDATIONS ENDPOINTS
            "personalized_recommendations": "GET /recommendations/personalized",  # Get personalized recommendations (requires auth)
            "trending_products": "GET /recommendations/trending",  # Get trending products
            "category_recommendations": "GET /recommendations/category/{category}",  # Category-specific recommendations (requires auth)
            "similar_products": "GET /recommendations/similar/{product_id}",  # Get similar products
            "for_you": "GET /recommendations/for-you",  # Comprehensive "For You" page (requires auth)
            "recommendation_insights": "GET /recommendations/insights",  # Understanding recommendations (requires auth)
            
            # 🎯 MASTER ENDPOINT (All-in-One)
            "orchestrate_full": "POST /api/orchestrate/",  # Complete recommendation (all agents)
            "orchestrate_simple": "POST /api/orchestrate/simple",  # Quick search with defaults
            "orchestrate_health": "GET /api/orchestrate/health",  # Health check
            
            # Individual Agent Endpoints
            "search": "/api/products/search",
            "product_details": "/api/products/{product_id}",
            "list_products": "/api/products/",
            "analyze_reviews": "/api/reviews/analyze/{product_id}",
            "get_reviews": "/api/reviews/{product_id}",
            "track_price": "/api/price/track/{product_id}",
            "find_deals": "/api/price/deals",
            "flash_deals": "/api/price/flash-deals",
            "price_history": "/api/price/history/{product_id}",
            "compare_products": "/api/compare",
            "battle_compare": "/api/compare/battle/{id1}/{id2}",
            "get_winner": "/api/compare/winner",
            "search_and_compare": "/api/compare/search-and-compare",
            "purchase_plan": "/api/buyplan/{product_id}",
            "payment_recommendation": "/api/buyplan/recommend",
            "card_offers": "/api/buyplan/offers/{product_id}",
            "emi_plans": "/api/buyplan/emi/{product_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "llm": "configured" if (os.getenv("OPENAI_API_KEY") or os.getenv("USE_OLLAMA")) else "not configured",
        "environment": os.getenv("ENVIRONMENT", "development")
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
