import os
from io import BytesIO
from PyPDF2 import PdfReader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import requests
import re

CHROMA_PERSIST_DIR = "./chroma_db_v3"
OPENROUTER_API_KEY = "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"

# Initialize local embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Initialize ChromaDB vector store
vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 15})

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

def call_openrouter(prompt: str) -> str:
    """Calls OpenRouter API natively."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000", # Required by OpenRouter
        "X-Title": "ENISO Assistant", # Optional
    }
    data = {
        "model": "meta-llama/llama-3.1-8b-instruct:free", # Free tier model, no credits needed
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=120)
    response.raise_for_status()
    res_json = response.json()
    return res_json['choices'][0]['message']['content']

def generate_rag_response(user_message: str) -> str:
    """Retrieves context and asks OpenRouter."""
    docs = retriever.invoke(user_message)
    context = "\n\n".join(doc.page_content for doc in docs)
    
    prompt = f"""You are a helpful assistant for ENISO (École Nationale d'Ingénieurs de Sousse).
    Answer the user's question based on the following context. If the answer is not in the context, say you don't know based on the provided documents.

    Context:
    {context}

    Question:
    {user_message}

    Answer:"""
    
    return call_openrouter(prompt)
