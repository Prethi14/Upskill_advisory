
## Upskill Advisor

An AI-powered career development platform that analyzes user skills and provides personalized course recommendations to bridge skill gaps for target career roles.

---

## 🚀 Overview

Upskill Advisor helps professionals identify skill gaps and provides tailored learning paths to achieve their career goals. The platform combines resume analysis, AI-powered skill assessment, and intelligent course matching to create personalized development plans.

---

## 🏗️ Architecture

The system consists of four main components:

- **Frontend:** React.js application with resume upload and skill input capabilities
- **Backend:** FastAPI server with MongoDB integration for course data
- **AI Components:** Ollama for local LLM inference, SentenceTransformers for embeddings
- **Database:** MongoDB Atlas with vector search capabilities

<img width="1500" height="1125" alt="svgviewer-png-output" src="https://github.com/user-attachments/assets/d0dd7656-2096-48b0-a389-af54cb63d1c0" />

![user_journey](https://github.com/user-attachments/assets/17291907-5398-44db-b0ef-80ba946b50e0)

---

## 📋 Prerequisites

Ensure you have the following installed:

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- Ollama (for local LLM inference)

---

## 🛠️ Installation & Setup

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-username/upskill-advisor
cd upskill-advisor

# Create virtual environment
python -m venv venv
source venv/bin/activate  

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=upskill_advisor
MONGODB_COLLECTION=courses

# Ollama Configuration
OLLAMA_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_URL=http://localhost:11434

# API Keys (Optional)
HUGGINGFACE_API_KEY=your_hf_key  # Backup for Ollama

# Application Settings
DEBUG=true
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

### 3. Start Ollama Services

```bash
# Start Ollama server (Terminal 1)
ollama serve

# In another terminal, pull required models (Terminal 2)
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

### 4. Database Setup

```bash
# Test MongoDB connection
cd test
python test_mongodb.py

# Test Ollama models
python test_ollama.py

# Seed database with sample courses
python seed.py
```

### 5. Start Backend Server

```bash
# Run FastAPI server
python main.py
# Server will be available at http://localhost:8000
```

### 6. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
# Frontend will be available at http://localhost:3000
```

---

## 📊 Key Features

### 1. Resume Analysis

- **PDF Processing:** Extracts text from uploaded resumes using PyPDF2
- **Skill Detection:** Uses regex patterns to identify technical skills
- **Format Support:** Handles various resume formats and layouts

### 2. AI-Powered Recommendations

- **LLM Integration:** Uses Ollama for local language model inference
- **Vector Similarity:** SentenceTransformers for semantic course matching
- **Skill Gap Analysis:** Compares user skills against role requirements

### 3. Course Database

- **MongoDB Storage:** Scalable document-based course storage
- **Vector Embeddings:** Precomputed embeddings for fast similarity search
- **Rich Metadata:** Course difficulty, duration, prerequisites, outcomes

---

## 🔌 API Endpoints

### Core Endpoints

#### `POST /advise`
Generate personalized learning recommendations

**Request (Form data):**
- `email`: User email address (required)
- `goal_role`: Target career role (required)
- `skills`: Comma-separated list of skills (optional)
- `resume`: PDF file upload (optional)

#### `GET /courses/search`
Search courses with optional AI enhancement

**Parameters:**
- `query`: Search terms (required)
- `limit`: Number of results (default: 5)
- `use_ai`: Enable AI-enhanced search (default: true)

---

## 🤖 AI Components

### Local LLM with Ollama

- **Model:** llama3.2:1b (lightweight, efficient)
- **Use Cases:** Skill gap analysis, recommendation reasoning
- **Fallback:** OpenAI API (optional)

### Embeddings

- **Model:** nomic-embed-text
- **Use Cases:** Semantic course matching, similarity search
- **Storage:** Vector embeddings in MongoDB

---

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
# Test individual components
python test/test_mongodb.py
python test/test_ollama.py
python test/test_skills.py

# Run all tests
python -m pytest test/
```

---

## 🚀 Deployment

### Backend Deployment (FastAPI)

```bash
# Production with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment (React)

```bash
# Build for production

npm run build
```
## 🎯 Conclusion

Upskill Advisor provides a comprehensive, AI-powered solution for career development and skill gap analysis. The platform successfully bridges the gap between current skill sets and target career roles through intelligent course recommendations.

---

## 🚀 Future Enhancements

The platform is designed for extensibility with potential future features:

- **Skill Proficiency Tracking:** Monitor progress over time
- **Learning Path Customization:** Adjust recommendations based on learning pace
- **Career Progress Analytics:** Visualize skill development journey
