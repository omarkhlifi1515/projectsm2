from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import database, models, auth, rag

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ENISO Assistant API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Schemas ──────────────────────────────────────────────────────────────────
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
    log_id: Optional[int] = None

class RatingUpdate(BaseModel):
    rating: int  # -1, 0, or 1

# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "running", "service": "eniso-backend-api-v3", "version": "3.0.0"}

# ─── Auth ─────────────────────────────────────────────────────────────────────
@app.post("/api/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    is_first = db.query(models.User).count() == 0
    hashed = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed, is_admin=is_first)
    db.add(new_user); db.commit(); db.refresh(new_user)
    token = auth.create_access_token(data={"sub": new_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/auth/me")
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "is_admin": current_user.is_admin}

# ─── Chat ─────────────────────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
def chat(request_data: ChatRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    try:
        response_text = rag.generate_rag_response(request_data.message)
        log = models.ChatLog(user_id=current_user.id, message=request_data.message, response=response_text)
        db.add(log); db.commit(); db.refresh(log)
        return ChatResponse(response=response_text, log_id=log.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/chat/{log_id}/rating")
def rate_message(log_id: int, rating: RatingUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    log = db.query(models.ChatLog).filter(models.ChatLog.id == log_id, models.ChatLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    if rating.rating not in (-1, 0, 1):
        raise HTTPException(status_code=400, detail="Rating must be -1, 0, or 1")
    log.rating = rating.rating; db.commit()
    return {"status": "ok", "log_id": log_id, "rating": rating.rating}

# ─── Upload ───────────────────────────────────────────────────────────────────
@app.post("/api/upload")
async def upload_document(files: List[UploadFile] = File(...), current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    total_chunks = 0; filenames = []
    for file in files:
        contents = await file.read()
        chunks = rag.process_and_store_document(contents, file.filename)
        total_chunks += chunks
        filenames.append(file.filename)
        doc = models.Document(filename=file.filename, file_size=len(contents), chunks_added=chunks, uploaded_by=current_user.id)
        db.add(doc)
    db.commit()
    return {"status": "success", "filenames": filenames, "chunks_added": total_chunks}

# ─── Admin: Logs ──────────────────────────────────────────────────────────────
@app.get("/api/logs")
def get_logs(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    logs = db.query(models.ChatLog).order_by(models.ChatLog.timestamp.desc()).limit(500).all()
    user_cache = {}
    result = []
    for log in logs:
        if log.user_id not in user_cache:
            u = db.query(models.User).filter(models.User.id == log.user_id).first()
            user_cache[log.user_id] = u.username if u else f"User#{log.user_id}"
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": user_cache[log.user_id],
            "message": log.message,
            "response": log.response,
            "rating": log.rating,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        })
    return result

# ─── Admin: Users ─────────────────────────────────────────────────────────────
@app.get("/api/admin/users")
def get_users(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    result = []
    for u in users:
        msg_count = db.query(models.ChatLog).filter(models.ChatLog.user_id == u.id).count()
        result.append({"id": u.id, "username": u.username, "is_admin": u.is_admin, "message_count": msg_count})
    return result

@app.patch("/api/admin/users/{user_id}/toggle-admin")
def toggle_admin(user_id: int, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own admin status")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = not user.is_admin; db.commit()
    return {"id": user.id, "username": user.username, "is_admin": user.is_admin}

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(models.ChatLog).filter(models.ChatLog.user_id == user_id).delete()
    db.delete(user); db.commit()
    return {"status": "deleted", "user_id": user_id}

# ─── Admin: Stats ─────────────────────────────────────────────────────────────
@app.get("/api/admin/stats")
def get_stats(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    from sqlalchemy import func as sqlfunc, cast, Date

    total_logs = db.query(models.ChatLog).count()
    total_users = db.query(models.User).count()
    total_docs = db.query(models.Document).count()
    positive_ratings = db.query(models.ChatLog).filter(models.ChatLog.rating == 1).count()
    today = datetime.utcnow().date()
    today_logs = db.query(models.ChatLog).filter(sqlfunc.date(models.ChatLog.timestamp) == today).count()

    # 7-day activity
    daily = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = db.query(models.ChatLog).filter(sqlfunc.date(models.ChatLog.timestamp) == day).count()
        daily.append({"date": day.strftime("%b %d"), "count": count})

    # Top users
    users = db.query(models.User).all()
    top_users = sorted(
        [{"username": u.username, "count": db.query(models.ChatLog).filter(models.ChatLog.user_id == u.id).count()} for u in users],
        key=lambda x: x["count"], reverse=True
    )[:8]

    satisfaction = round((positive_ratings / total_logs * 100) if total_logs else 0, 1)

    return {
        "total_logs": total_logs,
        "total_users": total_users,
        "total_docs": total_docs,
        "today_logs": today_logs,
        "satisfaction": satisfaction,
        "daily_activity": daily,
        "top_users": top_users,
    }

# ─── Admin: Documents ─────────────────────────────────────────────────────────
@app.get("/api/admin/documents")
def get_documents(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    docs = db.query(models.Document).order_by(models.Document.uploaded_at.desc()).all()
    result = []
    for d in docs:
        uploader = db.query(models.User).filter(models.User.id == d.uploaded_by).first()
        result.append({
            "id": d.id,
            "filename": d.filename,
            "file_size": d.file_size,
            "chunks_added": d.chunks_added,
            "uploaded_by": uploader.username if uploader else f"User#{d.uploaded_by}",
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
        })
    return result

@app.delete("/api/admin/documents/{doc_id}")
def delete_document(doc_id: int, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(database.get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc); db.commit()
    return {"status": "deleted", "doc_id": doc_id}
