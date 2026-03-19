import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

# Internal modules
from backend.database import engine, Base, get_db, SessionLocal
from backend.models import User
from backend.ml_engine import DEVICE, ml_engine
from backend.rate_limiter import limiter
from backend.routers import auth

# Ensure DB tables exist
Base.metadata.create_all(bind=engine)

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup actions
    logger.info("Initializing ML engine and loading model...")
    # Using a dedicated DB session for startup
    db = SessionLocal()
    try:
        # Explicitly initialize ML model with retry logic
        ml_engine.initialize()
        
        if ml_engine.is_ready():
            # Pushes embeddings from DB into RAM via FAISS
            ml_engine.load_all_embeddings(db)
            
            # Warmup the PyTorch graph to prevent first-request lag
            try:
                import torch
                logger.info("Warming up ML model graph...")
                dummy_signal = torch.zeros(1, 16000, device=DEVICE)
                with torch.no_grad():
                    _ = ml_engine.classifier.encode_batch(dummy_signal)
                logger.info("Model warmup complete.")
            except Exception as e:
                logger.warning(f"Could not warmup model: {e}")
        else:
            logger.warning("ML model failed to initialize during startup. It will try lazy-loading later.")
            
    except Exception as e:
         logger.error(f"Error during startup ML/FAISS initialization: {e}")
    finally:
        db.close()
        
    yield
    # Shutdown actions
    logger.info("Shutting down application...")

app = FastAPI(title="Voice Authentication API", lifespan=lifespan)

# Validation Error Logger
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}")
    logger.error(f"Body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

# Rate Limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect Routers
app.include_router(auth.router)

# --- Admin Endpoints ---

@app.get("/api/admin/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).with_entities(User.id, User.username).all()
    return [{"id": u.id, "username": u.username} for u in users]

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Simple delete, FAISS index will resync next restart, or you can implement dynamic remove 
    db.delete(user)
    db.commit()
    logger.info(f"Admin deleted user {user.username}")
    return {"status": "success", "message": f"User {user.username} deleted."}

# --- Frontend Serving ---
# Mount static files correctly
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/dashboard")
def serve_dashboard():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(frontend_dir, "dashboard.html"))

# Startup without uvicorn reload
if __name__ == "__main__":
    import uvicorn
    # Avoiding --reload to prevent duplicate SpeechBrain initialization and Windows multiprocessing conflicts.
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
