from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2
import io
import faiss
import numpy as np
import requests
import os
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load API key from environment
API_KEY = os.getenv("OPENROUTER_API_KEY")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

if not API_KEY:
    logger.warning("OPENROUTER_API_KEY not set - API calls will fail")

# Initialize FastAPI
app = FastAPI(title="RAG PDF System-v2")

# CORS Configuration
allowed_origins = ALLOWED_ORIGINS.split(",") if ALLOWED_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable - LAZY LOADED
embedder = None

def get_embedder():
    """Lazy load the sentence transformer model on first use"""
    global embedder
    if embedder is None:
        logger.info("Loading sentence transformer model (first time)...")
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully!")
    return embedder

# PDF storage
pdf_store = {
    "chunks": [],
    "embeddings": None,
    "index": None
}


class Question(BaseModel):
    question: str


def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text


def split_text(text, chunk_size=500):
    """Split text into chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def create_embeddings(chunks):
    """Create embeddings for text chunks"""
    model = get_embedder()  # Load model only when needed
    embeddings = model.encode(chunks)
    return np.array(embeddings).astype('float32')


def create_faiss_index(embeddings):
    """Create FAISS index for vector search"""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def search_similar(query, top_k=3):
    """Search for similar chunks in the PDF"""
    if pdf_store["index"] is None:
        return []

    model = get_embedder()  # Load model only when needed
    query_embedding = np.array(model.encode([query])).astype('float32')
    _, indices = pdf_store["index"].search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if idx < len(pdf_store["chunks"]):
            results.append(pdf_store["chunks"][idx])
    return results


def ask_llm(question, context):
    """Ask LLM with context"""
    if not API_KEY:
        return "Error: OPENROUTER_API_KEY not configured"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Based on the following information, answer the question in detail:

Information:

{context}

Question: {question}

Answer:"""

    data = {
        "model": "nex-agi/deepseek-v3.1-nex-n1:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to OpenRouter: {str(e)}")
        return f"Error connecting to model: {str(e)}"
    except KeyError as e:
        logger.error(f"Error parsing response: {str(e)}")
        return f"Error parsing response: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Unexpected error: {str(e)}"


@app.get("/")
async def root():
    """API information"""
    return {
        "message": "RAG System for PDF Processing",
        "version": "2.0.0",
        "pdf_loaded": pdf_store["index"] is not None,
        "model_loaded": embedder is not None,
        "endpoints": {
            "/upload-pdf/": "POST - Upload PDF file",
            "/ask/": "POST - Ask a question",
            "/health": "GET - Health check",
            "/docs": "GET - Swagger UI for testing"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": embedder is not None,
        "pdf_loaded": pdf_store["index"] is not None,
        "chunks_count": len(pdf_store["chunks"]) if pdf_store["chunks"] else 0,
        "api_key_configured": API_KEY is not None
    }


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file - Model loads on first use"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be PDF")

    try:
        logger.info(f"Processing PDF: {file.filename}")
        contents = await file.read()
        pdf_file = io.BytesIO(contents)

        text = extract_text_from_pdf(pdf_file)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")

        chunks = split_text(text)
        logger.info(f"Created {len(chunks)} chunks")

        # This will trigger model download on first call
        embeddings = create_embeddings(chunks)
        index = create_faiss_index(embeddings)

        pdf_store["chunks"] = chunks
        pdf_store["embeddings"] = embeddings
        pdf_store["index"] = index

        logger.info("PDF processed successfully")

        return JSONResponse({
            "message": "File uploaded and processed successfully",
            "filename": file.filename,
            "num_chunks": len(chunks),
            "total_characters": len(text)
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/ask/")
async def ask_question(question: Question):
    """Ask a question about uploaded PDF"""
    if pdf_store["index"] is None:
        raise HTTPException(status_code=400, detail="Must upload PDF first")

    try:
        logger.info(f"Received question: {question.question}")

        relevant_chunks = search_similar(question.question, top_k=3)
        if not relevant_chunks:
            raise HTTPException(status_code=404, detail="No relevant information found")

        context = "\n\n".join(relevant_chunks)
        answer = ask_llm(question.question, context)

        return JSONResponse({
            "question": question.question,
            "answer": answer,
            "sources_used": len(relevant_chunks)
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
