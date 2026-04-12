import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload_router, analyze_router, misc_router, rag_router

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ai_analyst")

app = FastAPI(title="AI Data Analyst API", version="3.0.0 (Autonomous)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(upload_router, tags=["Upload"])
app.include_router(analyze_router, tags=["Analyze"])
app.include_router(misc_router, tags=["Misc"])
app.include_router(rag_router, prefix="/rag", tags=["RAG"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)