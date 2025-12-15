# RAG PDF Chatbot System

AI-powered chatbot with PDF processing and Retrieval Augmented Generation (RAG) capabilities.

## Features

- 📄 **PDF Upload & Processing** - Extract and process text from PDF files
- 🔍 **Smart Search** - FAISS vector search for relevant context
- 🤖 **AI-Powered Responses** - GPT-3.5-turbo via OpenRouter
- 💬 **Dual Mode** - Works with or without PDF context
- 🚀 **Production Ready** - Optimized for Railway deployment

## Quick Start - Railway Deployment

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Railway optimized"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [Railway](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect the Dockerfile

### Step 3: Set Environment Variables

In Railway dashboard, go to **Variables** tab and add:

| Variable | Value |
|----------|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `ALLOWED_ORIGINS` | Your frontend URL (e.g., `https://your-app.vercel.app`) or `*` |
| `ENVIRONMENT` | `production` |

> **Note:** `PORT` is automatically set by Railway, don't add it manually.

### Step 4: Monitor Deployment

- Check the **Build Logs** tab
- Wait for "Deployment successful" message
- Expected image size: **~1-2 GB** (down from 7.8 GB)

## API Endpoints

### Health Check
```
GET /health
```
Returns health status and PDF loading state

### Upload PDF
```
POST /upload-pdf/
```
Upload and process a PDF file

**Request:** Multipart form data with PDF file

### Ask Question
```
POST /ask/
```
Ask a question with optional PDF context

**Request Body:**
```json
{
  "question": "What is machine learning?"
}
```

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Run server
python chatbot.py
```

The API will be available at `http://localhost:8000`

## Technology Stack

- **FastAPI** - Modern Python web framework
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **FAISS** - Vector similarity search
- **PyPDF2** - PDF text extraction
- **OpenRouter** - LLM API gateway

## Optimization Details

### What Was Fixed

1. **Multi-stage Docker Build** - Reduced image size by 70%
2. **CPU-Only Dependencies** - Removed CUDA packages (~4 GB saved)
3. **Environment Variables** - Moved secrets out of code
4. **Efficient Caching** - Optimized Docker layer caching
5. **.dockerignore** - Excluded unnecessary files from build

### Expected Performance

| Metric | Value |
|--------|-------|
| Image Size | ~1-2 GB |
| Cold Start | 2-3 seconds |
| RAM Usage | ~500 MB |
| Build Time | 3-5 minutes |

## Troubleshooting

### Build Fails with "Image too large"
- Check actual image size in Railway logs
- Verify .dockerignore is working
- Ensure CPU-only packages are installed

### "OPENROUTER_API_KEY not set" Error
- Go to Railway Variables tab
- Add `OPENROUTER_API_KEY` with your actual key
- Redeploy the service

### Model Loading Slow
- Model is cached during Docker build
- First request after sleep takes 2-3 seconds
- Consider Railway's "always-on" feature on Hobby plan

## Railway Pricing

- **Free Tier**: $0/month, 500 hours execution time
- **Hobby Tier**: $5/month, unlimited execution + better resources (recommended for ML apps)

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: `https://your-app.railway.app/docs`
- **ReDoc**: `https://your-app.railway.app/redoc`

## License

MIT

## Support

For issues or questions:
1. Check Railway deployment logs
2. Verify all environment variables are set
3. Test locally first with `.env` file
