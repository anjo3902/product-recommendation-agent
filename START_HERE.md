# 🎯 ONE-COMMAND STARTUP

## Start Everything (Auto-Save + All Services)

```powershell
.\start_all.ps1
```

**This single command will:**
1. ✅ **Auto-save your work** → Commits and pushes changes to GitHub
2. 🤖 **Start Ollama** → AI LLM server for intelligent responses  
3. ⚙️ **Start Backend** → FastAPI with 5 specialized agents
4. 🎨 **Start Frontend** → React app (auto-opens at http://localhost:3000)

---

## Other Commands

### Stop Everything
```powershell
.\stop_all.ps1
```
Stops Ollama, Backend, and Frontend safely.

### Check Status
```powershell
.\check_status.ps1
```
Shows which services are running and git status.

---

##  Services & URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React shopping interface |
| Backend | http://localhost:8000 | FastAPI + 5 AI agents |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Ollama | http://localhost:11434 | AI LLM server |

---

## The 5 AI Agents

Your system includes:
1. **Product Search** - Finds products using semantic search
2. **Review Analyzer** - Analyzes customer sentiment  
3. **Price Tracker** - Tracks prices & predicts best buy time
4. **Comparison** - Compares products side-by-side
5. **Buy Plan Optimizer** - Recommends EMI/cashback/cards

---

## Auto-Save Feature ✨

Every time you run `.\start_all.ps1`, it automatically:
- Detects uncommitted code changes
- Commits with timestamp: "Auto-save: 2026-02-07 10:30:15"
- Pushes to GitHub

**No manual git commands needed!**

---

## Troubleshooting

**Script won't run?**
```powershell
# Enable script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port already in use?**
```powershell
.\stop_all.ps1
.\start_all.ps1
```

**Services not starting?**
```powershell
.\check_status.ps1  # See what's running
```

---

## What Happens When You Run `start_all.ps1`

```
╔════════════════════════════════════════════════════════════════════╗
║        🚀 Product Recommendation Agent - Startup Manager 🚀        ║
╚════════════════════════════════════════════════════════════════════╝

📝 Step 1: Saving all work to GitHub...
======================================================================
   ✅ Changes saved to GitHub successfully!

🤖 Step 2: Starting Ollama LLM Server...
======================================================================
   ✅ Ollama started

⚙️  Step 3: Starting Backend Server...
======================================================================
   🚀 Launching Backend on http://localhost:8000...
   ✅ Backend is running - Status: healthy

🎨 Step 4: Starting Frontend...
======================================================================
   🚀 Launching Frontend on http://localhost:3000...

╔════════════════════════════════════════════════════════════════════╗
║                    ✅ ALL SYSTEMS RUNNING! ✅                       ║
╚════════════════════════════════════════════════════════════════════╝

📊 Service Status:
   🤖 Ollama:   http://localhost:11434 (AI LLM Server)
   ⚙️  Backend:  http://localhost:8000 (FastAPI + 5 Agents)
   🎨 Frontend: http://localhost:3000 (React App)

💡 Quick Commands:
   • Frontend will auto-open in browser
   • Check backend API: http://localhost:8000/docs
   • Check status: .\check_status.ps1
   • Stop all: .\stop_all.ps1

🎯 Ready to use! Open http://localhost:3000 to start shopping!
```

---

## Desktop Shortcut (Optional)

**Create a desktop shortcut for one-click startup:**

1. Right-click `start_all.ps1`
2. Send to → Desktop (create shortcut)
3. Double-click desktop icon to start!

---

**That's it! Just run `.\start_all.ps1` and everything works!** 🚀
