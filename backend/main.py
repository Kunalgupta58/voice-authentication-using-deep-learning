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
    preload_model = os.getenv("PRELOAD_MODEL", "1").lower() in {"1", "true", "yes"}
    logger.info("Application startup. PRELOAD_MODEL=%s", preload_model)
    # Using a dedicated DB session for startup
    db = SessionLocal()
    try:
        if not preload_model:
            logger.info("Skipping eager model initialization; model will be lazy-loaded on first request.")
            yield
            logger.info("Shutting down application...")
            return

        # Explicitly initialize ML model with retry logic
        logger.info("Initializing ML engine and loading model...")
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

cors_origins_env = os.getenv("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
allow_all_origins = cors_origins == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    # Credentials cannot be used with wildcard origins; keep standards-compliant defaults.
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect Routers
app.include_router(auth.router)

# --- Admin Endpoints ---

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_ready": ml_engine.is_ready(),
    }

@app.get("/api/admin/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).with_entities(User.id, User.username).all()
    return [{"id": u.id, "username": u.username} for u in users]

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    logger.info(f"Admin deleted user {user.username}")
    return {"status": "success", "message": f"User {user.username} deleted."}

# --- Frontend Serving ---
# Serve built React files from 'dist'
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")

if os.path.exists(frontend_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")
else:
    logger.warning(f"Frontend dist directory not found at {frontend_dir}. Please run 'npm run build'.")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    from fastapi.responses import FileResponse
    # Skip API routes
    if full_path.startswith("api"):
         return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})
    
    # Check if requested file exists in dist
    file_path = os.path.join(frontend_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for React SPA
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return JSONResponse(status_code=404, content={"detail": "Frontend not found. Run npm run build."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
