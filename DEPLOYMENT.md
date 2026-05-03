# Deployment Guide

## Quick Summary
- ✅ **Recommended: Streamlit Cloud** - Best for this app
- ❌ **Netlify** - Not suitable (static site hosting only)

---

## Deployment Option 1: Streamlit Cloud (RECOMMENDED) ✅

### Why Streamlit?
- ⭐ **Free hosting** for public apps
- 🐍 **Python-native** - perfect for your MCP server
- 🔐 **Built-in secrets management** for API keys
- 🚀 **One-click deployment** from GitHub
- 📊 **No infrastructure setup needed**

### Step-by-Step Deployment

#### 1. **Prepare Your Repository**
```bash
# Files already created:
# - streamlit_app.py (main app)
# - requirements.txt (dependencies)
# - .streamlit/config.toml (Streamlit config)
# - .streamlit/secrets.toml.example (template)

# Commit and push to GitHub
git add .
git commit -m "Add Streamlit deployment files"
git push
```

#### 2. **Create Streamlit Cloud Account**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign up with GitHub
- Authorize Streamlit to access your repositories

#### 3. **Deploy Your App**
1. Click "**New app**"
2. Select your repository: `mcp_server_weather_agent`
3. Select branch: `main`
4. Set main file path: `streamlit_app.py`
5. Click "**Deploy**"

#### 4. **Add API Keys (Secrets)**
1. In your Streamlit Cloud dashboard, click your app
2. Go to **Settings** → **Secrets**
3. Paste your secrets (TOML format):
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

#### 5. **Done!** 🎉
Your app is now live at: `https://your-username-weatheragent.streamlit.app`

### Get API Keys
- **GROQ API Key**: [https://console.groq.com](https://console.groq.com) (free)
- **OpenWeather API Key**: Optional (wttr.in used by default, free)

---

## Deployment Option 2: Alternative Platforms (if not using Streamlit)

### Railway.app (Good Alternative)
```bash
# Simple deployment to Railway
# Files needed: requirements.txt ✅, Procfile

# Add to project root:
echo "web: streamlit run streamlit_app.py --server.port=\$PORT" > Procfile

# Deploy
railway up
```

### Render.com
```bash
# Create render.yaml in project root:
# (See render.yaml example below)
```

### Fly.io
```bash
# Similar setup with requirements.txt and Dockerfile
flyctl launch
```

---

## Why NOT Netlify ❌

Netlify is **not suitable** for this project because:

| Feature | Netlify | This App |
|---------|---------|----------|
| **Designed for** | Static sites & Frontend | Python backend server |
| **Backend support** | Functions only (very limited) | Full Python MCP server |
| **Docker** | No direct support | Needs container |
| **Runtime** | Node.js focused | Python 3.12+ required |
| **API Keys** | No easy secrets management | Needs GROQ + OpenWeather keys |

**What would be needed:** 
- Rewrite as REST API (Flask/FastAPI)
- Deploy separately from frontend
- Complex serverless function setup
- Much more difficult than Streamlit

**Not worth it** - use Streamlit instead! 🚀

---

## Local Testing Before Deployment

### Test Streamlit locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

### Test with sample queries
- "Get weather alerts for CA"
- "What's the weather in London?"
- "Weather in New York"

---

## Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution:** Add your key to Streamlit Cloud secrets (Settings → Secrets)

### Issue: "MCP Client connection failed"
**Solution:** Ensure `server/weather.json` exists and is configured correctly

### Issue: "Slow response time"
**Solution:** MCP server startup can take 5-10 seconds on first run - normal

### Issue: "Module not found"
**Solution:** Update `requirements.txt` and redeploy

---

## Environment Variables Needed

| Variable | Where to get | Required? |
|----------|-------------|-----------|
| `GROQ_API_KEY` | [groq.com](https://groq.com) | **YES** |
| `OPENWEATHER_API_KEY` | [openweathermap.org](https://openweathermap.org/api_keys) | No (wttr.in used as fallback) |

---

## Post-Deployment Checklist

- [ ] App is visible at your Streamlit Cloud URL
- [ ] GROQ API key is configured in secrets
- [ ] Chat works and returns weather data
- [ ] Example queries work:
  - [ ] "Get alerts for CA"
  - [ ] "Weather in London"

---

## Next Steps

1. **Deploy to Streamlit Cloud** (5 minutes)
2. **Test the app** with sample queries
3. **Share your app URL** with others
4. **Monitor usage** in Streamlit Cloud dashboard

---

## Summary

**Best Choice: Streamlit Cloud ✅**
- Easiest deployment
- Free hosting
- Perfect for this app
- Takes ~5 minutes

**Don't use Netlify ❌** - it's for static sites, not Python servers
