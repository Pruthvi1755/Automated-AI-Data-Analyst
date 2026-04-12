import logging
from typing import List, Dict, Any
from core.state import app_state

logger = logging.getLogger("ai_analyst.rag")

# Try importing RAG dependencies gracefully so the app doesn't crash if they're missing
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from PyPDF2 import PdfReader
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("RAG dependencies (faiss, sentence_transformers, PyPDF2) not found. RAG disabled.")

# Lazy load model
_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None and RAG_AVAILABLE:
        try:
            logger.info("Loading sentence-transformers model...")
            _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"Failed to load embed model: {e}")
    return _embed_model

def extract_text_from_pdf(file_content: bytes) -> str:
    if not RAG_AVAILABLE:
        return ""
    import io
    from PyPDF2 import PdfReader
    
    try:
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def build_faiss_index(chunks: List[str]):
    if not RAG_AVAILABLE or not chunks:
        return None
    
    model = get_embed_model()
    if not model:
        return None
        
    embeddings = model.encode(chunks)
    dimension = embeddings.shape[1]
    
    import faiss
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    return index

def process_document(file_content: bytes, filename: str) -> bool:
    if not RAG_AVAILABLE:
        return False
        
    text = extract_text_from_pdf(file_content)
    if not text.strip():
        return False
        
    chunks = chunk_text(text)
    index = build_faiss_index(chunks)
    
    if index:
        state = app_state
        state.rag_chunks = chunks
        state.rag_index = index
        state.rag_doc_name = filename
        return True
    return False

async def query_documents(query: str) -> str:
    if not RAG_AVAILABLE:
        return "Document Q&A is not available. Please install RAG dependencies."
        
    state = app_state
    if not hasattr(state, 'rag_index') or state.rag_index is None:
        return "No document uploaded for Q&A."
        
    model = get_embed_model()
    if not model:
        return "Failed to load embedding model."
        
    q_emb = model.encode([query])
    D, I = state.rag_index.search(np.array(q_emb).astype('float32'), k=3)
    
    relevant_chunks = [state.rag_chunks[i] for i in I[0] if i < len(state.rag_chunks)]
    context = "\n---\n".join(relevant_chunks)
    
    from intelligence.llm_client import _call_ollama
    prompt = f"Answer the user query based ONLY on the following context. If you cannot answer based on context, say so.\nContext:\n{context}\n\nQuery: {query}"
    
    answer = _call_ollama(prompt, temperature=0.3)
    if answer:
        return answer
    
    # Fallback: return matched chunks directly
    return f"Based on the document:\n\n{context}"
