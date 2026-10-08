import os
import shutil
import uuid
from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Request,
    HTTPException
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse
)

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq

from rag import RAGSystem
from prompt_engineering import get_prompt


# ==========================================
# LOAD ENVIRONMENT
# ==========================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# ==========================================
# FASTAPI
# ==========================================

app = FastAPI(
    title="AI Document Knowledge Assistant",
    description=(
        "AI-powered Document Question Answering "
        "System using RAG, Embeddings, ChromaDB "
        "and Groq."
    ),
    version="1.0.0"
)


# ==========================================
# STATIC + TEMPLATES
# ==========================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


# ==========================================
# DIRECTORIES
# ==========================================

os.makedirs("uploads", exist_ok=True)


# ==========================================
# RAG SYSTEM
# ==========================================

rag = RAGSystem()


# ==========================================
# GROQ CLIENT
# ==========================================

if GROQ_API_KEY:
    groq_client = Groq(
        api_key=GROQ_API_KEY
    )
else:
    groq_client = None


# ==========================================
# REQUEST MODEL
# ==========================================

class QuestionRequest(BaseModel):
    question: str
    technique: str = "role-based"


# ==========================================
# HOME
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ==========================================
# UPLOAD DOCUMENTS
# ==========================================

@app.post("/upload")
async def upload_documents(
    files: list[UploadFile] = File(...)
):

    allowed_extensions = {
        ".pdf",
        ".txt",
        ".md"
    }

    saved_files = []

    for file in files:

        if not file.filename:
            continue

        extension = os.path.splitext(
            file.filename
        )[1].lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file: "
                    f"{file.filename}. "
                    f"Only PDF, TXT and Markdown "
                    f"files are allowed."
                )
            )

        # Prevent unsafe filenames
        original_name = os.path.basename(
            file.filename
        )

        unique_name = (
            f"{uuid.uuid4().hex}_"
            f"{original_name}"
        )

        file_path = os.path.join(
            "uploads",
            unique_name
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        saved_files.append(
            file_path
        )

    if not saved_files:
        raise HTTPException(
            status_code=400,
            detail="No valid documents were uploaded."
        )

    # Build embeddings and vector database
    result = rag.build_database(
        saved_files
    )

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return JSONResponse(
        content={
            "success": True,
            "message": result["message"],
            "documents": result.get(
                "documents",
                0
            ),
            "chunks": result.get(
                "chunks",
                0
            ),
            "files": [
                os.path.basename(path)
                for path in saved_files
            ]
        }
    )


# ==========================================
# CREATE CONTEXT
# ==========================================

def create_context(retrieved):

    context_parts = []

    for item in retrieved:

        context_parts.append(
            f"Source: {item['source']}\n"
            f"{item['content']}"
        )

    return "\n\n---\n\n".join(
        context_parts
    )


# ==========================================
# GENERATE GROQ ANSWER
# ==========================================

def generate_answer(
    technique,
    question,
    context
):

    if groq_client is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "GROQ_API_KEY is missing. "
                "Please add it to your .env file."
            )
        )

    prompt = get_prompt(
        technique,
        question,
        context
    )

    try:

        completion = (
            groq_client.chat.completions.create(
                model=GROQ_MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI document "
                            "question answering assistant. "
                            "Answer only from the "
                            "provided document context."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.2
            )
        )

        return completion.choices[
            0
        ].message.content

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Groq API error: {str(e)}"
        )


# ==========================================
# ASK QUESTION
# ==========================================

@app.post("/ask")
async def ask_question(
    request: QuestionRequest
):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    allowed_techniques = {
        "zero-shot",
        "few-shot",
        "role-based"
    }

    if request.technique not in allowed_techniques:
        raise HTTPException(
            status_code=400,
            detail="Invalid prompting technique."
        )

    # Semantic search
    retrieved = rag.search(
        question,
        top_k=3
    )

    if not retrieved:
        raise HTTPException(
            status_code=400,
            detail=(
                "Please upload and process "
                "documents first."
            )
        )

    # Create context
    context = create_context(
        retrieved
    )

    # Generate answer
    answer = generate_answer(
        request.technique,
        question,
        context
    )

    return {
        "question": question,
        "technique": request.technique,
        "answer": answer,
        "sources": retrieved
    }


# ==========================================
# PROMPT COMPARISON
# ==========================================

@app.post("/compare")
async def compare_prompts(
    request: QuestionRequest
):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    retrieved = rag.search(
        question,
        top_k=3
    )

    if not retrieved:
        raise HTTPException(
            status_code=400,
            detail="Please upload documents first."
        )

    context = create_context(
        retrieved
    )

    techniques = [
        "zero-shot",
        "few-shot",
        "role-based"
    ]

    results = {}

    for technique in techniques:

        answer = generate_answer(
            technique,
            question,
            context
        )

        results[technique] = answer

    return {
        "question": question,
        "results": results,
        "sources": retrieved
    }


# ==========================================
# FIVE TEST QUESTIONS
# ==========================================

@app.get("/test-questions")
async def test_questions():

    questions = [
        "What is Python?",
        "What is a variable?",
        "What is a list?",
        "What is a function?",
        "What are conditional statements?"
    ]

    return {
        "questions": questions
    }


# ==========================================
# DATABASE STATUS
# ==========================================

@app.get("/status")
async def status():

    return {
        "documents_in_vector_database":
            rag.document_count,

        "chunks_in_vector_database":
            rag.collection.count(),

        "embedding_model":
            "all-MiniLM-L6-v2",

        "vector_database":
            "ChromaDB",

        "llm":
            GROQ_MODEL,

        "supported_formats":
            ["PDF", "TXT", "Markdown"]
    }