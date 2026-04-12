import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from rag.document_qa import process_document, query_documents, RAG_AVAILABLE

logger = logging.getLogger("ai_analyst.rag")
router = APIRouter()

class RagQueryRequest(BaseModel):
    query: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF for RAG."""
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=501, detail="RAG dependencies not installed.")
        
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported for Document Q&A.")
        
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB).")
        
    success = process_document(content, file.filename)
    if not success:
        raise HTTPException(400, "Failed to process PDF. It might be empty or unreadable.")
        
    return {"message": "Document processed successfully and ready for Q&A.", "filename": file.filename}

@router.post("/query")
async def query_rag(req: RagQueryRequest):
    """Query uploaded PDF."""
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=501, detail="RAG dependencies not installed.")
        
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")
        
    answer = await query_documents(req.query.strip())
    return {"answer": answer, "query": req.query}
