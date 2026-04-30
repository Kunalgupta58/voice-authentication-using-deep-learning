import os
import io
import sys
import tempfile
import torch
import torchaudio
import numpy as np

# Monkeypatch for torchaudio >= 2.1.0 compatibility with SpeechBrain
if not hasattr(torchaudio, 'list_audio_backends'):
    torchaudio.list_audio_backends = lambda: ['soundfile']
if not hasattr(torchaudio, 'get_audio_backend'):
    torchaudio.get_audio_backend = lambda: 'soundfile'
if not hasattr(torchaudio, 'set_audio_backend'):
    torchaudio.set_audio_backend = lambda x: None


import time
import random
import logging
from typing import Callable, Any
from pathlib import Path

# Allow running this file directly via `python backend/ml_engine.py`.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging for MLEngine
logger = logging.getLogger(__name__)

# Monkeypatch for torchaudio >= 2.1.0 compatibility with SpeechBrain
if not hasattr(torchaudio, 'list_audio_backends'):
    torchaudio.list_audio_backends = lambda: ['soundfile']

if not hasattr(torchaudio, 'get_audio_backend'):
    torchaudio.get_audio_backend = lambda: 'soundfile'

if not hasattr(torchaudio, 'set_audio_backend'):
    torchaudio.set_audio_backend = lambda x: None

def with_retry(max_retries: int = 5, base_delay: float = 1.0, jitter: bool = True):
    """Decorator for retrying functions with exponential backoff and jitter."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Check for "503 MODEL_CAPACITY_EXHAUSTED" or similar API failures
                    error_str = str(e).upper()
                    if "503" in error_str or "CAPACITY_EXHAUSTED" in error_str:
                        retries += 1
                        if retries >= max_retries:
                            logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}. Error: {e}")
                            raise
                        
                        delay = base_delay * (2 ** (retries - 1))
                        if jitter:
                            delay += random.uniform(0, 0.1 * delay)
                        
                        logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after {delay:.2f}s. Error: {e}")
                        time.sleep(delay)
                    else:
                        # Non-retryable error
                        raise
            return None
        return wrapper
    return decorator


try:
    from speechbrain.inference import EncoderClassifier
except ImportError:
    from speechbrain.pretrained import EncoderClassifier
try:
    from speechbrain.utils.fetching import LocalStrategy
    HAS_LOCAL_STRATEGY = True
except ImportError:
    HAS_LOCAL_STRATEGY = False

from backend.models import User

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("WARNING: faiss-cpu not installed. Vector search will be disabled.")

# We use CUDA if a supported GPU is installed, otherwise fallback to CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class MLEngine:
    def __init__(self):
        """
        Initializes the MLEngine.
        Note: Model initialization is deferred to `initialize()` or automated via lazy loading.
        """
        self.classifier = None
        self.embedding_dim = 192 # ECAPA-TDNN uses 192 dimensions
        self.index = None
        self.user_ids = [] # Maps faiss index ID to User DB ID
        self.username_map = {} # Maps faiss index ID to username
        
        if FAISS_AVAILABLE:
            # Inner Product index for Cosine Similarity (requires normalized vectors)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            
        logger.info("MLEngine initialized (model not yet loaded).")

    def is_ready(self) -> bool:
        """Checks if the classifier is loaded and ready for use."""
        return self.classifier is not None

    def initialize(self):
        """
        Explicitly loads the model with retry logic.
        Can be called during application startup for pre-loading.
        """
        if self.classifier:
            return

        logger.info("Starting ML model initialization...")
        try:
            self._load_model()
            logger.info("ML model successfully initialized.")
        except Exception as e:
            logger.error(f"Final failure during model initialization: {e}")
            self.classifier = None

    @with_retry(max_retries=5)
    def _load_model(self):
        """Loads SpeechBrain model directly from Hugging Face."""
        # Use runtime cache path (outside source tree) so large model files are not committed.
        model_dir = Path(os.getenv("MODEL_CACHE_DIR", "/tmp/spkrec-ecapa-voxceleb"))
        os.makedirs(model_dir, exist_ok=True)

        run_opts = {"device": DEVICE}

        logger.info(f"Loading SpeechBrain model directly from Hugging Face into {model_dir}...")
        self.classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir=str(model_dir),
            run_opts=run_opts,
        )

        self.classifier.eval()


    def _ensure_initialized(self):
        """Internal helper for lazy initialization upon first use."""
        if not self.classifier:
            logger.info("Lazy-loading ML model on first call...")
            self.initialize()
            if not self.classifier:
                raise RuntimeError("ML model failed to initialize during lazy-load.")
            
    def extract_embedding(self, audio_path: str) -> torch.Tensor:
        """Extracts embedding from file path (Legacy)."""
        self._ensure_initialized()
        from scipy.io import wavfile
        fs, y = wavfile.read(audio_path)
        return self._compute_embedding(fs, y)

    def extract_embedding_bytes(self, wav_bytes: bytes) -> torch.Tensor:
        """Extracts embedding directly from memory bytes."""
        self._ensure_initialized()
        from scipy.io import wavfile
        stream = io.BytesIO(wav_bytes)
        fs, y = wavfile.read(stream)
        return self._compute_embedding(fs, y)

    def _compute_embedding(self, fs, y) -> torch.Tensor:
        self._ensure_initialized()
            
        if y.dtype == np.int16:
            y = y.astype(np.float32) / 32768.0
            
        signal = torch.from_numpy(y).unsqueeze(0).to(DEVICE)
            
        with torch.no_grad():
            embeddings = self.classifier.encode_batch(signal)
            embeddings = embeddings.squeeze()
            
        return embeddings

    def compute_similarity(self, emb1: torch.Tensor, emb2: torch.Tensor) -> float:
        emb1 = emb1.squeeze()
        emb2 = emb2.squeeze()
        emb1_norm = torch.nn.functional.normalize(emb1, p=2, dim=0)
        emb2_norm = torch.nn.functional.normalize(emb2, p=2, dim=0)
        similarity = torch.dot(emb1_norm, emb2_norm)
        return float(similarity.item())
        
    def load_all_embeddings(self, db_session):
        """Loads all user embeddings from the database into the FAISS index."""
        if not FAISS_AVAILABLE or self.index is None:
            # We must set 192 for ECAPA-TDNN if FAISS is missing
            self.embedding_dim = 192 
            return
            
        users = db_session.query(User).all()
        
        if FAISS_AVAILABLE and self.index is not None:
            self.index.reset()
            
        self.user_ids = []
        self.username_map = {}
        self.torch_embeddings_list = []
        
        if not users:
            print("No users found to load into FAISS.")
            return
            
        embeddings_list = []
        for i, u in enumerate(users):
            emb = np.frombuffer(u.embedding, dtype=np.float32)
            
            # FAISS dimension sanity check (prevent crashes from old ResNet 256-dim embeddings)
            if self.embedding_dim is None:
                 if self.index is not None and self.index.d != len(emb):
                     self.index = faiss.IndexFlatIP(len(emb))
                 self.embedding_dim = len(emb)
            
            if len(emb) != self.embedding_dim:
                 print(f"WARNING: User {u.username} has obsolete embedding dimension {len(emb)}. Expecting {self.embedding_dim}. Skipping load.")
                 continue

            emb_norm = emb / np.linalg.norm(emb)
            embeddings_list.append(emb_norm)
            
            self.user_ids.append(u.id)
            self.username_map[i] = u.username
            self.torch_embeddings_list.append(torch.from_numpy(emb_norm))

        if not embeddings_list:
            print("No compatible embeddings found to load into FAISS.")
            return

        # Build vectorized torch tensor for fallback
        self.torch_embeddings = torch.stack(self.torch_embeddings_list).to(DEVICE)
            
        if FAISS_AVAILABLE and self.index is not None:
            embeddings_matrix = np.vstack(embeddings_list).astype('float32')
            self.index.add(embeddings_matrix)
            print(f"Loaded {len(users)} embeddings into FAISS index.")
        else:
            print(f"Loaded {len(users)} embeddings into Vectorized Torch Memory (FAISS not available).")
        
    def add_user_to_index(self, user_id: int, username: str, embedding: torch.Tensor):
        if not FAISS_AVAILABLE or self.index is None:
            return
            
        emb_np = embedding.cpu().numpy()
        emb_norm = emb_np / np.linalg.norm(emb_np)
        emb_matrix = np.array([emb_norm], dtype='float32')
        
        idx = len(self.user_ids)
        
        if FAISS_AVAILABLE and self.index is not None:
            self.index.add(emb_matrix)
            
        if not hasattr(self, 'torch_embeddings_list'):
            self.torch_embeddings_list = []
        
        self.torch_embeddings_list.append(torch.from_numpy(emb_norm))
        # Rebuild tensor (rare operation on registration only, so slightly slow stack is fine)
        self.torch_embeddings = torch.stack(self.torch_embeddings_list).to(DEVICE)
            
        self.user_ids.append(user_id)
        self.username_map[idx] = username
        
    def search_index(self, query_emb: torch.Tensor, top_k: int = 1):
        """Searches FAISS or uses vectorized Torch Fallback for the closest matches."""
        # 1. FAISS Search
        if FAISS_AVAILABLE and self.index is not None and self.index.ntotal > 0:
            emb_np = query_emb.cpu().numpy()
            emb_norm = emb_np / np.linalg.norm(emb_np)
            query_matrix = np.array([emb_norm], dtype='float32')
            
            distances, indices = self.index.search(query_matrix, top_k)
            best_idx = indices[0][0]
            best_score = distances[0][0]
            
            if best_idx != -1:
                return self.username_map[best_idx], float(best_score)
                
        # 2. Vectorized Torch Fallback (If FAISS unavailable but users exist)
        if hasattr(self, 'torch_embeddings') and len(self.torch_embeddings) > 0:
            # L2 Normalize the query
            q_norm = torch.nn.functional.normalize(query_emb.squeeze(), p=2, dim=0)
            
            # Compute similarity against entire DB at once (Matrix Multiplication)
            similarities = torch.matmul(self.torch_embeddings, q_norm)
            best_idx = torch.argmax(similarities).item()
            best_score = similarities[best_idx].item()
            
            return self.username_map[best_idx], best_score
            
        return None, -1.0

ml_engine = MLEngine()
