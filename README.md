# RAG PDF System v2 - Railway Deployment (Nixpacks)

AI-powered PDF question-answering system using Retrieval Augmented Generation (RAG).

## 🚀 NEW APPROACH: Using Nixpacks (Railway Default)

**Why Changed?**
- Docker builds were producing 7.8 GB images
- Nixpacks is Railway's optimized builder for Python
- Better handling of ML dependencies
- Smaller final deployment size

## 📦 Files Included

1. **chatbot.py** - FastAPI application
2. **requirements.txt** - Dependencies with CPU-only PyTorch
3. **Procfile** - Deployment command
4. **nixpacks.toml** - Nixpacks configuration
5. **runtime.txt** - Python version specification
6. **.env.example** - Environment template
7. **.env** - Local development config
8. **.gitignore** - Git ignore rules
9. **README.md** - This file

**IMPORTANT:** No Dockerfile or railway.json - Railway will use Nixpacks automatically!

## 🚀 Quick Deploy to Railway

### Step 1: Clean Up Old Docker Files

**Delete these if they exist:**
- `Dockerfile`
- `railway.json`
- `.dockerignore`

Railway will automatically detect Python and use Nixpacks.

### Step 2: Push to GitHub

```bash
git rm Dockerfile railway.json .dockerignore 2>/dev/null || true
git add .
git commit -m "Switch to Nixpacks deployment"
git push origin main
```

### Step 3: Deploy on Railway

1. Go to [Railway](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Railway will auto-detect Nixpacks

### Step 4: Set Environment Variables

**CRITICAL:** Go to Railway Dashboard → **Variables** tab and add:

| Variable | Value |
|----------|-------|
| `OPENROUTER_API_KEY` | `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` |
| `ALLOWED_ORIGINS` | `https://mostafarady29-front-end.vercel.app` |

⚠️ **DO NOT set PORT** - Railway sets it automatically!

### Step 5: Wait for Build

Build should complete in 5-8 minutes.

## 📊 Expected Results

- **Build method**: Nixpacks (not Docker)
- **Build time**: 5-8 minutes
- **Deployment size**: Optimized by Nixpacks
- **No image size limit issues**

## 🔌 API Endpoints

### Health Check
```
GET /health
```

### Upload PDF
```
POST /upload-pdf/
```

### Ask Question
```
POST /ask/
```

### API Docs
```
GET /docs
```

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Run server
python chatbot.py
```

## 📦 Technology Stack

- FastAPI - Web framework
- Sentence Transformers - Text embeddings
- FAISS - Vector search
- PyPDF2 - PDF processing
- OpenRouter - LLM API
- **Nixpacks** - Railway's optimized builder

## 🐛 Troubleshooting

### Build still fails?
- Make sure you deleted Dockerfile and railway.json
- Railway should show "Detected: Python" in build logs
- Check that nixpacks.toml exists in repo

### "OPENROUTER_API_KEY not configured"
- Add key in Railway Variables tab
- Redeploy after adding

### Model loading slow
- First request takes 10-20 seconds (downloads model)
- Subsequent requests are fast (cached)

## 📈 Why Nixpacks?

| Feature | Docker | Nixpacks |
|---------|--------|----------|
| Image Size | 7.8 GB ❌ | Optimized ✅ |
| ML Dependencies | Manual setup | Auto-optimized ✅ |
| Build Time | 10+ minutes | 5-8 minutes ✅ |
| Configuration | Complex Dockerfile | Simple Procfile ✅ |

## License

MIT
