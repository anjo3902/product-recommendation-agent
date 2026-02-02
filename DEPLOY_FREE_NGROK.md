# 🆓 100% FREE Deployment - Using ngrok

## Overview
Deploy your entire project **completely FREE** using:
- ✅ Frontend → Vercel (Free)
- ✅ Backend → Your PC with Ollama (Free)
- ✅ ngrok → Expose backend to internet (Free)

**Total Cost: $0/month** 🎉

---

## PART 1: Setup ngrok

### Step 1.1: Create ngrok Account

1. Go to [ngrok.com](https://ngrok.com/)
2. Click "Sign up" (Free forever plan)
3. Sign up with GitHub/Google

### Step 1.2: Download ngrok

1. After login, go to [dashboard.ngrok.com/get-started/setup](https://dashboard.ngrok.com/get-started/setup)
2. Download ngrok for Windows
3. Extract `ngrok.exe` to a folder (e.g., `C:\ngrok\`)

### Step 1.3: Get Your Auth Token

1. In ngrok dashboard, go to "Your Authtoken"
2. Copy your authtoken

### Step 1.4: Configure ngrok

```powershell
# Open PowerShell
cd C:\ngrok

# Add your authtoken (replace with your actual token)
.\ngrok.exe config add-authtoken YOUR_AUTHTOKEN_HERE
```

---

## PART 2: Start Your Backend

### Step 2.1: Make Sure Backend is Running

```powershell
cd "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent"

# Start backend (if not already running)
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Keep this terminal open.

### Step 2.2: Start ngrok Tunnel

**Open a NEW PowerShell window:**

```powershell
cd C:\ngrok

# Start ngrok tunnel to your backend
.\ngrok.exe http 8000
```

You'll see output like:
```
ngrok

Session Status    online
Account           Your Name (Plan: Free)
Forwarding        https://abc123.ngrok-free.app -> http://localhost:8000
```

### Step 2.3: Copy Your ngrok URL

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

**Important:** This URL changes each time you restart ngrok on free plan!

---

## PART 3: Update Backend CORS

Your backend needs to allow requests from Vercel and ngrok.

**File: `main.py`**

Find the CORS section and make sure it includes:

```python
# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.ngrok-free.app",
        "https://*.ngrok.io",
        "*"  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Restart your backend after this change.

---

## PART 4: Deploy Frontend to Vercel

### Step 4.1: Update Frontend Config

```powershell
cd frontend
```

**Edit `.env.production`:**
```env
REACT_APP_API_URL=https://YOUR_NGROK_URL.ngrok-free.app
```

Replace with your actual ngrok URL from Step 2.3

### Step 4.2: Deploy to Vercel

```powershell
# Install Vercel CLI (if not installed)
npm install -g vercel

# Login
vercel login

# Deploy to production
vercel --prod
```

### Step 4.3: Add Environment Variable

**Option A: Via CLI**
```powershell
vercel env add REACT_APP_API_URL production
# When prompted, enter: https://YOUR_NGROK_URL.ngrok-free.app
```

**Option B: Via Dashboard**
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project
3. Settings → Environment Variables
4. Add:
   - Name: `REACT_APP_API_URL`
   - Value: `https://YOUR_NGROK_URL.ngrok-free.app`
   - Environment: Production ✓
5. Redeploy

---

## PART 5: Test Your Deployment

### Test Backend (via ngrok)
```
https://YOUR_NGROK_URL.ngrok-free.app/docs
```

Should show FastAPI documentation ✅

### Test Frontend
```
https://your-app.vercel.app
```

Should load login page and connect to backend ✅

---

## 🔄 Daily Usage Workflow

Since ngrok free plan gives you a new URL each restart:

### **Every time you start working:**

1. **Start Backend**
   ```powershell
   cd "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent"
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

2. **Start ngrok** (in new terminal)
   ```powershell
   cd C:\ngrok
   .\ngrok.exe http 8000
   ```

3. **Copy new ngrok URL** (e.g., `https://xyz789.ngrok-free.app`)

4. **Update Vercel environment variable:**
   ```powershell
   cd frontend
   vercel env rm REACT_APP_API_URL production
   vercel env add REACT_APP_API_URL production
   # Enter new ngrok URL
   
   # Redeploy
   vercel --prod
   ```

---

## 💡 Keep Same URL (ngrok Static Domain)

### Option 1: ngrok Paid Plan ($8/month)
- Get a static domain that never changes
- No need to update frontend daily

### Option 2: Use Startup Script

Create `start-with-ngrok.ps1`:

```powershell
# Start backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent'; python -m uvicorn main:app --host 127.0.0.1 --port 8000"

# Wait for backend to start
Start-Sleep -Seconds 5

# Start ngrok
cd C:\ngrok
.\ngrok.exe http 8000
```

Run this script to start both backend and ngrok together.

---

## 🎯 Pro Tips for ngrok Free Tier

### 1. Keep PC Awake
```powershell
# Prevent PC from sleeping
powercfg /change standby-timeout-ac 0
```

### 2. Auto-start on Windows Boot

Create a scheduled task:
```powershell
# Create start_backend.bat
echo @echo off > C:\start_backend.bat
echo cd "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent" >> C:\start_backend.bat
echo python -m uvicorn main:app --host 127.0.0.1 --port 8000 >> C:\start_backend.bat

# Create start_ngrok.bat
echo @echo off > C:\start_ngrok.bat
echo cd C:\ngrok >> C:\start_ngrok.bat
echo ngrok.exe http 8000 >> C:\start_ngrok.bat
```

Then create Windows Startup shortcuts to these batch files.

### 3. Monitor ngrok Status

ngrok dashboard: [dashboard.ngrok.com](https://dashboard.ngrok.com)
- See active tunnels
- View request logs
- Check bandwidth usage

---

## 📊 ngrok Free vs Paid

| Feature | Free | Paid ($8/month) |
|---------|------|-----------------|
| Tunnels | 1 active | 3 active |
| URL | Random (changes) | Static domain |
| Bandwidth | 1 GB/month | Unlimited |
| Connections | 40/min | Unlimited |

For testing/demo: **Free is perfect!** ✅

---

## Alternative FREE Option: Cloudflare Tunnel

If you want a static URL for free:

### Setup Cloudflare Tunnel

1. **Install:**
   ```powershell
   # Download from https://github.com/cloudflare/cloudflared/releases
   ```

2. **Setup:**
   ```powershell
   cloudflared tunnel login
   cloudflared tunnel create product-recommendation
   cloudflared tunnel route dns product-recommendation api.yourdomain.com
   ```

3. **Run:**
   ```powershell
   cloudflared tunnel run product-recommendation --url http://localhost:8000
   ```

**Pros:** Free, static URL
**Cons:** Need a domain (can use free from Freenom)

---

## 🔧 Troubleshooting

### ngrok shows "ERR_NGROK_3200"
- Your authtoken is not configured
- Run: `ngrok config add-authtoken YOUR_TOKEN`

### Frontend shows CORS error
- Update CORS in `main.py` to include ngrok URLs
- Restart backend

### ngrok URL changes too often
- Upgrade to ngrok paid ($8/month) for static domain
- OR use Cloudflare Tunnel (free with domain)

### PC goes to sleep, backend stops
- Change power settings
- Keep PC plugged in

---

## ✅ Complete Setup Checklist

- [ ] ngrok account created
- [ ] ngrok.exe downloaded and configured
- [ ] Authtoken added
- [ ] Backend running on localhost:8000
- [ ] ngrok tunnel started
- [ ] ngrok URL copied
- [ ] CORS updated in main.py
- [ ] Frontend .env.production updated with ngrok URL
- [ ] Frontend deployed to Vercel
- [ ] Environment variable added in Vercel
- [ ] Tested backend via ngrok URL
- [ ] Tested frontend on Vercel
- [ ] Everything working ✅

---

## 🎉 You're Live - 100% FREE!

**Your Setup:**
```
User Browser
    ↓
Frontend (Vercel - Free)
    ↓
ngrok (Free)
    ↓
Backend (Your PC - Free)
    ↓
Ollama (Free)
```

**Monthly Cost: $0** 🎉

---

## 📱 Share Your App

Frontend URL: `https://your-app.vercel.app`

Your app is now accessible to anyone on the internet - completely free!

---

## Need Help?

If you encounter issues:
1. Check ngrok dashboard for errors
2. Check backend logs
3. Check Vercel deployment logs
4. Check browser console (F12)

Let me know which step you're on and I'll help! 🚀
