AI Document Knowledge Assistant

An AI-powered Document Question Answering System built with Python, FastAPI, RAG, Sentence Transformers, ChromaDB, and Groq LLM.

Features
Upload PDF, TXT, and Markdown documents
Extract and split document text into chunks
Generate embeddings using Sentence Transformers
Store embeddings in ChromaDB
Semantic search with Top-3 relevant chunks
Display retrieved sources and similarity distances
Zero-Shot, Few-Shot, and Role-Based prompting
Generate context-aware answers using Groq LLM
Technologies
Python
FastAPI
Sentence Transformers
ChromaDB
Groq API
HTML, CSS, JavaScript
PyPDF
Project Flow
Upload Documents
      ↓
Text Extraction
      ↓
Text Chunking
      ↓
Embeddings
      ↓
ChromaDB
      ↓
Semantic Search
      ↓
Top 3 Relevant Chunks
      ↓
Prompt Engineering
      ↓
Groq LLM
      ↓
Final Answer
Installation
pip install -r requirements.txt

Create a .env file:

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

Run the application:

python -m uvicorn main:app --reload

Open:

http://127.0.0.1:8000
Prompt Engineering

The project implements three prompting techniques:

Zero-Shot Prompting
Few-Shot Prompting
Role-Based Prompting

These techniques can be compared using the Compare All Techniques option.

Semantic Search vs Keyword Search

Keyword Search looks for exact words or phrases.

Semantic Search uses embeddings to understand the meaning of text and retrieve conceptually similar information, even when the exact keywords are different.
