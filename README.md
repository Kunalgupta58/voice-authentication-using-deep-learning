# 🎙 Voice-Based Authentication System Using Deep Learning

![Version](https://img.shields.io/badge/version-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-DeepLearning-orange)
![Status](https://img.shields.io/badge/Status-Academic%20Project-success)

---

## 📌 Project Overview

The **Voice-Based Authentication System Using Deep Learning** is a biometric security solution that authenticates users using their unique voice patterns instead of traditional passwords.

This system:
- Records user voice input
- Extracts MFCC (Mel-Frequency Cepstral Coefficients) features
- Uses Deep Learning (CNN) for speaker verification
- Implements Anti-Spoofing detection to prevent replay attacks
- Provides real-time authentication decision (Accept / Reject)

---

## 🎯 Objectives

- Develop a secure voice-based authentication system
- Eliminate dependency on traditional passwords
- Extract speaker-specific features using MFCC
- Implement Deep Learning for accurate speaker verification
- Prevent spoofing and replay attacks
- Ensure fast and reliable authentication

---

## 🧠 Technologies Used

| Category | Tools |
|----------|--------|
| Programming Language | Python |
| Feature Extraction | Librosa |
| Deep Learning | TensorFlow / Keras |
| Audio Recording | SoundDevice |
| Data Processing | NumPy |
| Model Saving | Joblib |
| Visualization | Matplotlib |

---

## 🏗 System Architecture

### 🔄 Workflow

1. User Enrollment (Voice Registration)
2. Audio Recording
3. Preprocessing (Noise Handling)
4. MFCC Feature Extraction
5. Deep Learning Model Training
6. Voice Verification
7. Anti-Spoofing Check
8. Authentication Result (Access Granted / Denied)

---

## 🔐 Key Features

- 🎙 Voice-Based Authentication
- 📊 MFCC Feature Extraction
- 🧠 CNN Deep Learning Model
- ⚡ Real-Time Verification
- 🛡 Anti-Spoofing Detection
- 👥 Multi-User Support
- 🔒 Secure Access Control

---

## 📂 Project Structure

```
voice_auth_system/
│
├── dataset/
│   ├── user1/
│   ├── user2/
│
├── models/
│   ├── voice_model.h5
│   ├── labels.pkl
│
├── src/
│   ├── preprocess.py
│   ├── feature_extraction.py
│   ├── model.py
│   ├── authentication.py
│   ├── anti_spoofing.py
│
├── app.py
├── requirements.txt
└── README.md
```

---

## ⚙ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/voice-authentication-system.git
cd voice-authentication-system
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶ Running the Project

### Step 1 – Enroll User

```bash
python app.py
```

Select:
```
1. Enroll User
```

Record 5 voice samples for each user.

---

### Step 2 – Train Model

```bash
python
>>> from model import train_model
>>> train_model()
```

Model will be saved in:
```
models/voice_model.h5
models/labels.pkl
```

---

### Step 3 – Login / Authenticate

```bash
python app.py
```

Select:
```
2. Login
```

System will:
- Record new voice sample
- Extract MFCC features
- Run deep learning model
- Perform anti-spoofing check
- Display result

---

## 📊 Success Metrics

- High authentication accuracy
- Low false acceptance rate
- Fast response time
- Reliable spoof detection
- Stable multi-user performance

---

## 🚀 Future Enhancements

- 📱 Mobile App Integration
- 🌐 Cloud Deployment
- 🔐 Multi-Factor Authentication (Voice + Face)
- 🤖 Transformer-Based Speaker Verification
- 🧠 Advanced CNN/RNN Anti-Spoofing Model
- 🌍 Multi-Language Support

---

## 👥 Team Members

| Name | Role |
|------|------|
| Kunal Gupta | Product Lead & System Integration |
| Anu Chaudhary | ML & Feature Extraction |
| Aditya Gupta | Frontend & Preprocessing |

Institute: GLA University  
Course: B.Tech CSE (III Year – IV Sem)  
Project Version: v1.0  
Year: 2025-26  

---

## 📚 References

- Reynolds, D.A. – Automatic Speaker Recognition
- Campbell, J.P. – Speaker Recognition Tutorial
- TensorFlow Documentation
- PyTorch Documentation
- LibROSA Documentation
- IEEE Xplore – Voice Biometrics Research Papers

---

## 📜 License

This project is developed for academic and research purposes only.

---

## ⭐ If you found this project useful

Give it a ⭐ on GitHub!

---
