# RAG PDF Chatbot - Deployment Guide

## Optimized for Railway Deployment

This version is optimized to keep the Docker image under 2 GB (Railway's limit is 4 GB).

## Quick Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Optimized for Railway deployment"
git push origin main
```

### 2. Deploy to Railway
1. Go to [Railway](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect the Dockerfile

### 3. Configure Environment Variables
In Railway dashboard, add these variables:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `ALLOWED_ORIGINS`: Your frontend URL (e.g., https://your-app.vercel.app)

### 4. Monitor Deployment
- Check the build logs
- Wait for "Deployment successful" message
- Image size should be ~1-2 GB (down from 7.8 GB)

## What Was Optimized?

### Multi-Stage Docker Build
- **Stage 1 (Builder)**: Installs dependencies and downloads models
- **Stage 2 (Runtime)**: Only copies necessary files, reducing final image size by ~70%

### CPU-Only Dependencies
- Uses `torch` CPU version instead of CUDA (saves ~4 GB)
- Installs from PyTorch CPU-only wheel index

### .dockerignore File
- Excludes unnecessary files from build context
- Reduces build time and image size

### Model Pre-caching
- Downloads sentence-transformers model during build
- Prevents runtime downloads and ensures consistent deployments

## Expected Image Sizes

| Component | Size |
|-----------|------|
| Base Python image | ~150 MB |
| Dependencies | ~800 MB |
| Model cache | ~100 MB |
| **Total** | **~1-1.5 GB** |

## Troubleshooting

### Build Still Too Large?
1. Check Railway build logs for actual size
2. Ensure .dockerignore is working: `docker build -t test .`
3. Verify CPU-only torch is installed: Check logs for "cpu" in torch installation

### Memory Issues at Runtime?
- Railway free tier: 512 MB RAM (might struggle)
- Upgrade to Hobby tier: 8 GB RAM (recommended for ML apps)

### Slow Cold Starts?
- Model is pre-cached during build
- First request after sleep will still take 2-3 seconds
- Consider Railway's "always-on" feature

## File Structure
```
├── chatbot.py              # Main application
├── requirements.txt        # Optimized dependencies
├── Dockerfile             # Multi-stage build
├── .dockerignore          # Exclude unnecessary files
├── railway.json           # Railway configuration
├── .env.example           # Environment template
└── README.md              # This file
```

## Cost Estimate (Railway)

- **Free Tier**: $0/month, 500 hours execution time
- **Hobby Tier**: $5/month, unlimited execution time + better resources

## Support

If deployment fails:
1. Check Railway logs: Click "View Logs" in dashboard
2. Verify image size: Should see "Image size: X GB" in logs
3. Check environment variables: All required vars set?

## License
MIT
