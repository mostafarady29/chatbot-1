from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings

import PyPDF2
import io
from sentence_transformers import SentenceTransformer
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


# Settings loaded from environment (.env locally, Railway env vars in prod)
class Settings(BaseSettings):
    """Application settings"""

    OPENROUTER_API_KEY: str
    ALLOWED_ORIGINS: str = "*"
    ENVIRONMENT: str = "production"

    class Config:
        env_file = ".env"


settings = Settings()

# Initialize FastAPI
app = FastAPI(
    title="RAG PDF Chatbot System",
    version="1.0.0",
    description="AI-powered chatbot with PDF processing and RAG capabilities",
)

# CORS Configuration
allowed_origins = (
    settings.ALLOWED_ORIGINS.split(",")
    if settings.ALLOWED_ORIGINS != "*"
    else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embedding model
logger.info("Loading sentence transformer model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("Model loaded successfully")

# PDF storage in memory
pdf_store = {
    "chunks": [],
    "embeddings": None,
    "index": None,
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
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
    return chunks


def create_embeddings(chunks):
    """Create embeddings for text chunks"""
    embeddings = embedder.encode(chunks)
    return np.array(embeddings).astype("float32")


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

    query_embedding = np.array(embedder.encode([query])).astype("float32")
    _, indices = pdf_store["index"].search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if idx < len(pdf_store["chunks"]):
            results.append(pdf_store["chunks"][idx])
    return results


def ask_llm(question, context):
    """Ask LLM with optional context"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    if context:
        prompt = f"""Based on the following information, answer the question in detail:

Information:

{context}

Question: {question}

Answer:"""
    else:
        prompt = question

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
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
        logger.error(f"Error parsing OpenRouter response: {str(e)}")
        return f"Error parsing response: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Unexpected error: {str(e)}"


@app.get("/")
async def root():
    """API information"""
    return {
        "message": "RAG PDF Chatbot System",
        "version": "1.0.0",
        "pdf_loaded": pdf_store["index"] is not None,
        "endpoints": {
            "upload_pdf": "POST /upload-pdf/",
            "ask_question": "POST /ask/",
            "health": "GET /health",
            "docs": "GET /docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": True,
        "pdf_loaded": pdf_store["index"] is not None,
        "chunks_count": len(pdf_store["chunks"]) if pdf_store["chunks"] else 0,
    }


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    if not file.filename.lower().endswith(".pdf"):
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

        embeddings = create_embeddings(chunks)
        index = create_faiss_index(embeddings)

        pdf_store["chunks"] = chunks
        pdf_store["embeddings"] = embeddings
        pdf_store["index"] = index

        logger.info("PDF processed successfully")

        return JSONResponse(
            {
                "message": "File uploaded and processed successfully",
                "filename": file.filename,
                "num_chunks": len(chunks),
                "total_characters": len(text),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/ask/")
async def ask_question(question: Question):
    """Ask a question with optional PDF context"""
    try:
        logger.info(f"Received question: {question.question}")

        context = ""
        sources_used = 0
        has_context = False

        if pdf_store["index"] is not None:
            relevant_chunks = search_similar(question.question, top_k=3)
            if relevant_chunks:
                context = "\n\n".join(relevant_chunks)
                sources_used = len(relevant_chunks)
                has_context = True

        answer = ask_llm(question.question, context)

        return JSONResponse(
            {
                "question": question.question,
                "answer": answer,
                "sources_used": sources_used,
                "has_context": has_context,
            }
        )
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
