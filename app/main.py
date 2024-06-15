# app/main.py
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import SessionLocal, engine
from app.auth import verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
import logging
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Application Vfarm startup complete.")
    yield
    # Shutdown event
    logger.info("Application Vfarm shutdown.")

app = FastAPI(lifespan=lifespan)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Something went wrong"},
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Response(content=access_token, headers={"Set-Cookie": f"access_token={access_token}; Path=/; Max-Age={ACCESS_TOKEN_EXPIRE_MINUTES*60}; Secure; HttpOnly"})

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/chatboxes/", response_model=List[schemas.ChatBox])
def get_chatboxes_by_user(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_all_chat_boxes(db=db, user_id=current_user.id)

@app.post("/chatboxes/", response_model=schemas.ChatBox)
def create_chat_box(chat_box: schemas.ChatBoxCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_chat_box(db=db, chat_box=chat_box, user_id=current_user.id)

@app.post("/chatboxes/{chat_box_id}/messages/", response_model=schemas.ChatMessage)
def create_chat_message(chat_box_id: int, chat_message: schemas.ChatMessageCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if not crud.check_chatbox_ownership(db, user_id=current_user.id, chat_box_id=chat_box_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this chat box")
    return crud.create_chat_message(db=db, chat_message=chat_message, chat_box_id=chat_box_id)

@app.get("/chatboxes/{chat_box_id}/messages/", response_model=List[schemas.ChatMessage])
def get_chat_history(chat_box_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if not crud.check_chatbox_ownership(db, user_id=current_user.id, chat_box_id=chat_box_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this chat box")
    return crud.get_chat_history(db=db, chat_box_id=chat_box_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8888)