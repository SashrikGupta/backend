# 🚀 Streamlit Cloud Deployment — Step-by-Step Guide

Follow these steps to deploy **Review Insight AI** to Streamlit Community Cloud.

---

## Prerequisites

- [x] GitHub account
- [x] Streamlit Community Cloud account (sign up at [share.streamlit.io](https://share.streamlit.io))
- [x] All API keys ready in your `.env` file

---

## Step 1: Push to GitHub

### 1.1 — Initialize Git (if not already done)

```bash
cd "c:\Users\sashr\OneDrive\Desktop\desk\nirma\4th year\semester 8\Winter Internship\code\backend"
git init
```

### 1.2 — Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name it something like `review-insight-ai`
3. Set it to **Public** (Streamlit Cloud free tier requires public repos) or **Private** (if you connect your GitHub account to Streamlit Cloud)
4. **Do NOT** initialize with README (you already have one)

### 1.3 — Add Remote and Push

```bash
git remote add origin https://github.com/YOUR_USERNAME/review-insight-ai.git
git add .
git commit -m "Initial commit: Review Insight AI for Streamlit Cloud"
git branch -M main
git push -u origin main
```

> ⚠️ **Important**: The `.gitignore` we created will automatically exclude `.env`, `.streamlit/secrets.toml`, `sessions/`, `__pycache__/`, and temp directories. Your API keys will NOT be pushed.

### 1.4 — Verify What Got Pushed

Make sure these files are in your repo:

```
├── .gitignore
├── .python-version                 ← Python 3.12
├── .streamlit/
│   └── config.toml                 ← Theme config
├── requirements.txt                ← Dependencies
├── App/
│   ├── __init__.py
│   ├── streamlit_app.py            ← Main entry point
│   ├── session_manager.py
│   ├── styles.py
│   └── assets/
│       ├── ai_avatar.png
│       └── user_avatar.png
├── Core/
│   ├── __init__.py
│   ├── config.json
│   ├── LLMS/
│   ├── Results/
│   │   └── pr_id_0.json            ← Pre-computed results
│   └── Workflows/
│       ├── MainGraph/
│       ├── PlotGraph/
│       ├── SandBoxGraph/
│       └── TagGraph/
├── 7817_1.csv                      ← Product review data
├── langgraph.json
├── pyproject.toml
└── README.md
```

And these should **NOT** be in the repo:
- `.env` ← contains your API keys
- `sessions/` ← ephemeral session data
- `__pycache__/` ← compiled Python files

---

## Step 2: Deploy on Streamlit Community Cloud

### 2.1 — Sign In

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your **GitHub** account
3. Authorize Streamlit to access your repositories

### 2.2 — Create New App

1. Click **"New app"** (top-right)
2. Fill in the deployment form:

| Field | Value |
|-------|-------|
| **Repository** | `YOUR_USERNAME/review-insight-ai` |
| **Branch** | `main` |
| **Main file path** | `App/streamlit_app.py` |

### 2.3 — Configure Advanced Settings

1. Click **"Advanced settings"** before deploying
2. Set **Python version** to `3.12`
3. In the **Secrets** text box, paste the following (replace with your actual keys from `.env`):

```toml
GROQ_KEY_COLLECTION = '[\"gsk_YOUR_KEY_1\" , \"gsk_YOUR_KEY_2\" , \"gsk_YOUR_KEY_3\" , \"gsk_YOUR_KEY_4\" , \"gsk_YOUR_KEY_5\"]'
GEMINI_KEY_COLLECTION = '[\"YOUR_GEMINI_KEY_1\" , \"YOUR_GEMINI_KEY_2\"]'
OPEN_ROUTER_KEY_COLLECTION = '[\"sk-or-v1-YOUR_KEY_1\" , \"sk-or-v1-YOUR_KEY_2\" , \"sk-or-v1-YOUR_KEY_3\" , \"sk-or-v1-YOUR_KEY_4\"]'
E2B_API_KEY = "e2b_YOUR_KEY"
LANGSMITH_API_KEY = "lsv2_YOUR_KEY"
LANGSMITH_TRACING_V2 = "true"
LANGSMITH_PROJECT = "Learning App"
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
```

> 💡 **Tip**: Open your `.env` file and copy each value. The format is the same — just wrap the entire value in quotes for TOML.

### 2.4 — Deploy!

1. Click **"Deploy!"**
2. Wait for the app to build (first deploy takes 5-10 minutes due to dependency installation)
3. Watch the build logs for any errors

---

## Step 3: Verify the Deployment

### ✅ Check These

1. **App loads**: You should see the dark-themed welcome screen with "Review Insight AI" title
2. **Product selection**: Enter product ID `0` (pre-computed results exist for this)
3. **Chat works**: Send a message like "Summarize the reviews" and verify the AI responds
4. **Data analysis**: Ask "What are the most common complaints?" — this triggers the data analysis tool
5. **Plot generation**: Ask "Create a bar chart of sentiment distribution" — this triggers the plot generation tool
6. **Images render**: Verify generated plots appear inline in the chat

### ⚠️ Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| **ModuleNotFoundError** | Check `requirements.txt` — a dependency might be missing. Add it and redeploy |
| **API key errors** | Go to app settings → Secrets, verify all keys are correct. Make sure JSON arrays use escaped quotes (`\"`) |
| **App crashes on startup** | Check the Streamlit Cloud logs (click "Manage app" → "Logs") |
| **Timeout on first query** | The first query loads all LLMs into memory. This can take 30-60 seconds. Subsequent queries will be faster |
| **"No module named Core"** | Make sure the Main file path is set to `App/streamlit_app.py` (not a root wrapper) and the backend root contains `Core/` |

---

## Step 4: Updating the App

After any code changes:

```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```

Streamlit Cloud will **automatically redeploy** on every push to `main`.

---

## 🔗 Useful Links

- **Streamlit Cloud Dashboard**: [share.streamlit.io](https://share.streamlit.io)
- **Streamlit Secrets Docs**: [docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- **Streamlit Cloud Docs**: [docs.streamlit.io/deploy/streamlit-community-cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)

---

## App URL

After deployment, your app will be available at:

```
https://YOUR_USERNAME-review-insight-ai-appstreamlit-app-XXXXX.streamlit.app
```

You can customize this URL in the Streamlit Cloud dashboard settings.
