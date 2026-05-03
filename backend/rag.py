import os
from io import BytesIO
from PyPDF2 import PdfReader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import requests
import re

CHROMA_PERSIST_DIR = "./chroma_db_v3"

# Initialize local embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Initialize ChromaDB vector store
vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 15})

DEFAULT_LLM_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_LLM_MODEL = "qwen/qwen-2.5-72b-instruct"
DEFAULT_LLM_API_KEY = "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"

def process_and_store_document(file_bytes: bytes, filename: str):
    """Parses a PDF or TXT file, splits it into chunks, and stores in ChromaDB."""
    text = ""
    if filename.lower().endswith('.pdf'):
        reader = PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    else:
        text = file_bytes.decode('utf-8', errors='ignore')
        
    # Clean up weird spacing in group names (e.g., 'GTE -2.1' -> 'GTE-2.1')
    text = re.sub(r'([a-zA-Z]+)\s+-\s*(\d)', r'\1-\2', text)
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=500)
    splits = text_splitter.split_text(text)
    
    # Store in ChromaDB
    if splits:
        vectorstore.add_texts(splits, metadatas=[{"source": filename} for _ in splits])
        vectorstore.persist()
    return len(splits)

def _get_setting(db, key: str) -> str:
    try:
        from models import Setting
        row = db.query(Setting).filter(Setting.key == key).first()
        return (row.value if row and row.value is not None else "").strip()
    except Exception:
        return ""

def call_llm(prompt: str, *, db=None) -> str:
    """Calls the configured LLM gateway (admin-configured or env fallback)."""
    api_key = _get_setting(db, "llm_api_key") if db is not None else ""
    base_url = _get_setting(db, "llm_base_url") if db is not None else ""
    model = _get_setting(db, "llm_model") if db is not None else ""

    api_key = api_key or DEFAULT_LLM_API_KEY
    base_url = base_url or DEFAULT_LLM_BASE_URL
    model = model or DEFAULT_LLM_MODEL
    
    if not api_key:
        raise RuntimeError("LLM is not configured. Ask an admin to set an API key in Admin Console → Settings.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    url = base_url.rstrip("/") + "/chat/completions"
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    res_json = response.json()
    return res_json['choices'][0]['message']['content']

def generate_rag_response(user_message: str, *, db=None) -> str:
    """Retrieves context and asks the configured LLM gateway."""
    docs = retriever.invoke(user_message)
    context = "\n\n".join(doc.page_content for doc in docs)
    
    prompt = f"""You are a helpful assistant for ENISO (École Nationale d'Ingénieurs de Sousse).
    Answer the user's question based on the following context. If the answer is not in the context, say you don't know based on the provided documents.

    Context:
    {context}

    Question:
    {user_message}

    Answer:"""
    
    return call_llm(prompt, db=db)
