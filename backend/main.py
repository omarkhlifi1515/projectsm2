from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from datetime import timedelta
import database, models, auth, rag

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ENISO Assistant API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "running", "service": "eniso-backend-api-v2"}

@app.post("/api/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # If it's the very first user, make them an admin
    is_first_user = db.query(models.User).count() == 0
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password, is_admin=is_first_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = auth.create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me")
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return {"username": current_user.username, "is_admin": current_user.is_admin}

@app.post("/api/upload")
async def upload_document(
    files: List[UploadFile] = File(...),
    current_user: models.User = Depends(auth.require_admin)
):
    """Admin only: Upload multiple documents to the knowledge base."""
    total_chunks = 0
    filenames = []
    for file in files:
        contents = await file.read()
        chunks = rag.process_and_store_document(contents, file.filename)
        total_chunks += chunks
        filenames.append(file.filename)
    return {"status": "success", "filenames": filenames, "chunks_added": total_chunks}

@app.post("/api/chat", response_model=ChatResponse)
def chat(
    request_data: ChatRequest, 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Users only: Chat with the assistant."""
    try:
        response_text = rag.generate_rag_response(request_data.message)
        
        # Store in SQLite
        chat_log = models.ChatLog(
            user_id=current_user.id,
            message=request_data.message,
            response=response_text
        )
        db.add(chat_log)
        db.commit()
        
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
def get_logs(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    """Admin only: Get all chat logs."""
    logs = db.query(models.ChatLog).order_by(models.ChatLog.timestamp.desc()).limit(100).all()
    return logs
