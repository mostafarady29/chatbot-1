# RAG PDF System v2

AI-powered PDF question-answering system using Retrieval Augmented Generation (RAG).

## Features

- 📄 PDF upload and text extraction
- 🔍 FAISS vector similarity search
- 🤖 DeepSeek AI model via OpenRouter
- 🚀 Optimized for Railway deployment

## Quick Deploy to Railway

### Step 1: Prepare Files

All required files are included:
- `main.py` - Application code
- `requirements.txt` - Dependencies
- `Dockerfile` - Container configuration
- `railway.json` - Railway settings
- `.dockerignore` - Build optimization

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Railway deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 3: Deploy on Railway

1. Go to [Railway](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect the Dockerfile

### Step 4: Set Environment Variables

In Railway dashboard, go to **Variables** tab and add:

| Variable | Value |
|----------|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `ALLOWED_ORIGINS` | `https://mostafarady29-front-end.vercel.app` |

**Important:** Don't set `PORT` - Railway sets it automatically!

### Step 5: Deploy

Click **"Deploy"** and wait for build to complete (~5-10 minutes for first build).

## API Endpoints

### Health Check
```
GET /health
```

### Upload PDF
```
POST /upload-pdf/
Content-Type: multipart/form-data

Body: PDF file
```

### Ask Question
```
POST /ask/
Content-Type: application/json

Body: {"question": "Your question here"}
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Run server
python main.py
```

API will be available at `http://localhost:8000`

## Technology Stack

- **FastAPI** - Web framework
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **FAISS** - Vector similarity search
- **PyPDF2** - PDF processing
- **OpenRouter** - LLM API (DeepSeek model)

## Troubleshooting

### Build Failed
- Check Railway build logs
- Verify environment variables are set
- Ensure Dockerfile is in project root

### "OPENROUTER_API_KEY not configured"
- Add key in Railway Variables tab
- Redeploy after adding variables

### Model Loading Slow
- First deployment takes 5-10 minutes
- Model is cached in Docker image
- Subsequent deploys are faster

## Expected Performance

| Metric | Value |
|--------|-------|
| Image Size | ~1-2 GB |
| Build Time | 5-10 minutes (first), 2-3 minutes (subsequent) |
| Cold Start | 2-3 seconds |
| RAM Usage | ~500 MB |

## License

MIT
