# Voice Authentication System

A deep learning-based voice authentication system using MFCC feature extraction and cosine similarity matching.

## System Architecture

```
Clean Audio → Normalize → Trim Silence → MFCC Features → Embedding Vector → Similarity Matching
```

### Pipeline Stages:
1. **Clean**: Load audio at 16kHz sample rate
2. **Normalized**: Scale audio to [-1, 1] range
3. **Trimmed**: Remove silence using energy-based detection
4. **MFCC**: Extract 40 Mel-Frequency Cepstral Coefficients
5. **Embedding Vector**: Convert to fixed-length representation
6. **Verification**: Use cosine similarity with configurable threshold

## Project Structure

```
Voice Authentication/
├── audio_processing.py      # Audio feature extraction
├── embedding.py             # Embedding generation from dataset
├── authentication.py        # Voice verification & similarity matching
├── train.py                 # Generate embeddings from dataset
├── verify.py                # Verify unknown voice samples
├── demo.py                  # Complete workflow demonstration
├── config.py                # Configuration parameters
├── requirements.txt         # Python dependencies
├── create_env.ps1          # PowerShell setup script
├── data/
│   └── kunal/              # Training dataset (audio files)
└── models/                 # Generated embeddings (created during training)
```

## Quick Start

### 1. Setup Environment

Run PowerShell (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\pip.exe install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt
```

Or use the bundled script:

```powershell
./create_env.ps1
```

### 2. Train the System

Generate embeddings from your voice dataset:

```powershell
.\.venv\Scripts\python.exe train.py
```

Expected output:
```
Processing 50 audio files...
✓ sample_001.wav
✓ sample_002.wav
...
Embeddings shape: (50, 40)
Embeddings saved to models/kunal_embeddings.pkl
```

### 3. Verify Voice Samples

Test if a voice sample matches the registered speaker:

```powershell
.\.venv\Scripts\python.exe verify.py data/kunal/sample.wav
```

Output:
```
Verification Result:
  Status: ✓ VERIFIED
  Confidence: 0.8543
  Threshold: 0.7000
```

### 4. Run Demo

See the complete workflow:

```powershell
.\.venv\Scripts\python.exe demo.py
```

## Module Usage

### Audio Processing

```python
from audio_processing import load_and_trim, normalize_audio, extract_mfcc

# Load and process audio
audio, sr = load_and_trim("voice.wav")
audio = normalize_audio(audio)

# Extract MFCC embedding
embedding = extract_mfcc("voice.wav", n_mfcc=40)
# Returns: numpy array of shape (40,)
```

### Generate Embeddings

```python
from embedding import EmbeddingGenerator

generator = EmbeddingGenerator(n_mfcc=40)
embeddings = generator.generate_from_folder("data/kunal")
generator.save_embeddings("models/embeddings.pkl")
```

### Voice Verification

```python
from embedding import EmbeddingGenerator
from authentication import VoiceAuthenticator
import joblib

# Load reference embeddings
data = joblib.load("models/kunal_embeddings.pkl")
embeddings = data['embeddings']

# Create authenticator
authenticator = VoiceAuthenticator(embeddings, threshold=0.7)

# Verify a voice sample
result = authenticator.verify("test_audio.wav", return_scores=True)

if result['verified']:
    print(f"✓ Speaker verified! Confidence: {result['confidence']:.4f}")
else:
    print(f"✗ Speaker not recognized. Confidence: {result['confidence']:.4f}")
```

## Configuration

Edit `config.py` to customize:

```python
SAMPLE_RATE = 16000           # Audio sample rate (Hz)
TOP_DB = 20                   # Silence threshold (dB)
N_MFCC = 40                   # MFCC coefficients
SIMILARITY_THRESHOLD = 0.7    # Verification threshold (0-1)
```

## Requirements

- librosa >= 0.10.1  (Audio processing)
- numpy >= 1.26.4    (Numerical computing)
- scikit-learn >= 1.4.2 (Similarity metrics)
- joblib >= 1.3.2    (Model persistence)
- Python >= 3.10

## Dataset Format

Place training audio files in `data/kunal/` directory:
- Format: WAV files (.wav)
- Sample rate: 16kHz (automatically resampled)
- Duration: 2-10 seconds recommended
- Naming: Any descriptive name (e.g., `sample_001.wav`)

## Performance Tuning

### Threshold Optimization

Lower threshold = Higher sensitivity (more false positives)
Higher threshold = Higher specificity (more false negatives)

```python
# Set custom threshold
authenticator.set_threshold(0.75)

# View statistics to choose optimal threshold
stats = authenticator.calculate_statistics()
print(stats['mean_intra_similarity'])
```

### Recommended Thresholds

Based on similarity analysis:
- **< 0.6**: Very permissive (risky)
- **0.65-0.70**: Balanced (default)
- **0.75-0.80**: Strict (more reliable)
- **> 0.85**: Very strict (requires perfect match)

## Troubleshooting

**Error: "No .wav files found"**
- Ensure audio files are in the correct folder: `data/kunal/`
- Verify files have `.wav` extension

**Error: "Array shape mismatch"**
- All audio files are automatically resampled to 16kHz
- Check audio files are not corrupted

**Low verification confidence**
- Add more training samples (10+ recommended)
- Check if test audio matches training conditions
- Adjust threshold based on statistics

## GPU Support (Optional)

For GPU acceleration with TensorFlow:

```powershell
# Install CUDA 11.8 and cuDNN dependencies
# Then install TensorFlow GPU version:
pip install tensorflow[and-cuda]
```

See [TensorFlow GPU Documentation](https://www.tensorflow.org/install/gpu)

## Notes

- System uses cosine similarity for speaker verification
- MFCC provides robust representation of voice characteristics
- Threshold of 0.7 is empirically derived and can be tuned
- Works best with clean audio (16kHz sample rate)
- Supports single-speaker authentication (not multi-speaker recognition)
