# 🚀 Quick Start Guide - AI Product Recommendation System

## Overview
This guide will help you start the complete AI product recommendation system with the newly integrated orchestrator agent in the frontend.

---

## Prerequisites

### Required Software
- ✅ Python 3.8+ installed
- ✅ Node.js 16+ and npm installed  
- ✅ Ollama installed with llama3.1 model
- ✅ Database setup complete with product data

### Check Installations
```bash
# Python
python --version

# Node.js & npm
node --version
npm --version

# Ollama
ollama --version
ollama list  # Should show llama3.1
```

---

## 🎯 Starting the Application

### Step 1: Start Backend Server

Open **Terminal 1** (PowerShell):

```powershell
# Navigate to project root
cd "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent"

# Activate virtual environment (if using one)
# .\venv\Scripts\Activate.ps1

# Start FastAPI server
python -m uvicorn src.main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend**:
Open browser → http://localhost:8000/docs
You should see the Swagger API documentation.

---

### Step 2: Start Frontend Server

Open **Terminal 2** (PowerShell):

```powershell
# Navigate to frontend directory
cd "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent\frontend"

# Install dependencies (first time only)
# npm install

# Start React development server
npm start
```

**Expected Output**:
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000

webpack compiled successfully
```

**Verify Frontend**:
Browser should auto-open → http://localhost:3000
You should see the login page.

---

### Step 3: Ensure Ollama is Running

Open **Terminal 3** (PowerShell):

```powershell
# Check if Ollama service is running
ollama list

# If not running as service, start it:
# ollama serve

# Verify llama3.1 model is available
ollama list
```

**Expected Output**:
```
NAME            ID              SIZE    MODIFIED
llama3.1:latest abc123...       4.7GB   2 weeks ago
```

---

## 🔐 Login & Access

### Default Test User
```
Email: test@example.com
Password: testpass123
```

### Create New User
```powershell
# In Terminal 1 (backend directory)
python scripts/create_user.py
```

---

## 🧪 Testing the Orchestrator Integration

### 1. Navigate to AI Assistant
After login:
1. Click on **"AI Assistant"** in the navigation
2. You should see the ConversationAgent interface
3. Look for the welcome message with 5 feature cards

### 2. Test Product Query
Type in the chat:
```
Find me a laptop under $1000
```

**What to Watch For**:
1. ✅ Agent activity bar appears at top (green gradient)
2. ✅ Five agent chips light up:
   - 🔍 Search
   - ⭐ Review
   - 💰 Price
   - 📊 Comparison
   - 💳 BuyPlan
3. ✅ Loading spinner shows "Searching and analyzing products..."
4. ✅ Products appear as cards in the chat message
5. ✅ AI summary included with insights

### 3. Test General Query
Type:
```
Hello! How are you?
```

**What to Watch For**:
1. ❌ Orchestrator should NOT activate
2. ❌ No agent chips shown
3. ✅ Simple conversational response
4. ✅ Fast response time

---

## 📊 Monitoring the System

### Backend Logs (Terminal 1)
Watch for:
```
[Orchestrator] Processing query: Find me a laptop under $1000
[SearchAgent] Found 5 products
[ReviewAgent] Analyzing reviews for 5 products
[PriceAgent] Tracking prices for 5 products  
[ComparisonAgent] Comparing 5 products
[BuyPlanAgent] Generating payment plans
[Orchestrator] Generated AI summary with llama3.1
INFO:     127.0.0.1:XXXX - "POST /api/orchestrate/simple HTTP/1.1" 200 OK
```

### Frontend Console (Browser DevTools)
Press **F12** → Console tab

Watch for:
```
Sending message: Find me a laptop under $1000
Detected product query: true
Calling orchestrator agent...
Agent Search activated
Agent Review activated
Orchestrator response received: {success: true, products: [...]}
```

### Network Tab (Browser DevTools)
Press **F12** → Network tab

Look for:
```
POST /api/orchestrate/simple
Status: 200 OK
Response time: ~3-7 seconds
```

---

## 🐛 Troubleshooting

### Issue: Backend won't start
**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```powershell
pip install -r requirements.txt
```

---

### Issue: Frontend won't start
**Error**: `npm ERR! missing script: start`

**Solution**:
```powershell
cd frontend
npm install
npm start
```

---

### Issue: CORS errors in browser
**Error**: `Access to fetch at 'http://localhost:8000' has been blocked by CORS policy`

**Solution**:
Check `src/main.py` has CORS middleware:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: Ollama not responding
**Error**: Backend logs show timeout errors for AI summary

**Solution**:
```powershell
# Restart Ollama service
ollama serve

# Or check if model is available
ollama run llama3.1
```

---

### Issue: No products found
**Error**: "I searched but could not find any products"

**Solution**:
```powershell
# Check database has products
python scripts/check_products.py

# Or seed database
python scripts/seed_database.py
```

---

### Issue: Agent activity bar not showing
**Check**:
1. Open browser DevTools (F12) → Console
2. Look for errors
3. Verify fetch call to `/api/orchestrate/simple` succeeds
4. Check `activeAgents` state in React DevTools

---

### Issue: Products not displaying as cards
**Check**:
1. Verify ProductCard component imported
2. Check browser console for React errors
3. Verify product data has required fields:
   - `name`
   - `price`
   - `image_url`
   - `rating`

---

## 📱 Mobile Testing

### Desktop Browser Emulation
1. Press **F12** → Toggle device toolbar (Ctrl+Shift+M)
2. Select device: iPhone 12 Pro, Samsung Galaxy S20, etc.
3. Test chat interface
4. Verify responsive design

### Real Device Testing
1. Find your PC's IP address:
   ```powershell
   ipconfig
   # Look for IPv4 Address
   ```
2. Open on mobile: `http://YOUR_IP:3000`
3. Login and test

---

## 🎯 Example Test Scenarios

### Scenario 1: Budget Shopping
```
Query: "Show me smartphones under $500 with good battery life"

Expected:
- Search agent finds phones
- Review analyzer checks battery reviews
- Price tracker shows deals
- Products displayed with ratings
- AI summary mentions battery life
```

### Scenario 2: Product Comparison
```
Query: "Compare MacBook Air vs Dell XPS 13"

Expected:
- Search finds both products
- Comparison agent highlights differences
- Side-by-side analysis
- Pros/cons listed
- Recommendation provided
```

### Scenario 3: Payment Planning
```
Query: "I want to buy a $2000 laptop, what are my payment options?"

Expected:
- Buy plan optimizer activates
- EMI calculations shown
- Credit card offers listed
- Cashback opportunities
- Total cost breakdown
```

---

## ✅ Success Checklist

Before considering the system ready:

### Backend
- [ ] Server running on port 8000
- [ ] API docs accessible at /docs
- [ ] Ollama service running
- [ ] Database has products
- [ ] All agents working

### Frontend  
- [ ] Server running on port 3000
- [ ] Can login successfully
- [ ] Can navigate to AI Assistant
- [ ] Welcome screen displays
- [ ] Can send messages

### Integration
- [ ] Product queries activate orchestrator
- [ ] Agent activity bar appears
- [ ] 5 agents light up
- [ ] Products display in chat
- [ ] AI summary generated
- [ ] Wishlist button works
- [ ] No console errors

### UX/UI
- [ ] Smooth animations
- [ ] Professional design
- [ ] Mobile responsive
- [ ] Fast response times
- [ ] Clear visual feedback

---

## 🔄 Daily Development Workflow

### Morning Startup
```powershell
# Terminal 1: Backend
cd "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent"
python -m uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent\frontend"
npm start

# Terminal 3: Logs/Testing
# Keep open for running tests or checking logs
```

### During Development
- Backend hot-reloads automatically on code changes
- Frontend hot-reloads automatically on code changes
- Check both terminal logs for errors
- Use browser DevTools for frontend debugging

### End of Day Shutdown
```powershell
# Press Ctrl+C in each terminal to stop servers
# Terminal 1: Backend stops
# Terminal 2: Frontend stops
```

---

## 📚 Additional Resources

### Documentation Files
- **TEST_ORCHESTRATOR.md** - Comprehensive testing guide
- **ORCHESTRATOR_INTEGRATION_SUMMARY.md** - Complete change summary
- **README.md** - Project overview
- **API_DOCUMENTATION.md** - API endpoints

### Component Files
- **ConversationAgent.jsx** - Main chat interface
- **ConversationAgent.css** - Styles and animations
- **ProductCard.jsx** - Product card component
- **orchestrator_agent.py** - Backend orchestrator logic
- **orchestrator.py** - API routes

### API Endpoints
- **POST /api/orchestrate/simple** - Main orchestrator endpoint
- **GET /api/orchestrate/health** - Health check
- **GET /recommendations/for-you** - Personalized recommendations
- **GET /recommendations/trending** - Trending products

---

## 🎉 You're Ready!

Your AI product recommendation system with orchestrator integration is now running!

**Next Steps**:
1. Try the example queries in TEST_ORCHESTRATOR.md
2. Explore all 5 specialized agents
3. Test wishlist functionality
4. Check mobile responsiveness
5. Review analytics (if available)

**Need Help?**
- Check troubleshooting section above
- Review backend logs in Terminal 1
- Check frontend console in browser DevTools
- Verify Ollama is running and responding

Happy Testing! 🚀✨
