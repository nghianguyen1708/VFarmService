# app/main.py
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import SessionLocal, engine
from app.auth import verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
import logging
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.middleware.sessions import SessionMiddleware
from app.config import SECRET_KEY, DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI, HOST
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost",
    "http://localhost:8888",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to manage database sessions
app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)
# Configure SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Configure OAuth for Google
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_params=None,
    access_token_params=None,
    redirect_uri=REDIRECT_URI,
    client_kwargs={
        'scope': 'email profile openid',
        'redirect_url': REDIRECT_URI
    },
    authorize_state=SECRET_KEY
)

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
        content={"message": "Something went wrong", "error": str(exc), "request": str(request)},
    )

@app.get("/debug")
async def debug_session(request: Request):
    session = request.session
    print(session)  # Print session content for debugging
    return {"message": "Session debug information printed"}

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/token")
async def login_for_access_token(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "id": user.id})
    response = JSONResponse(content={"access_token": access_token})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        path="/"
    )
    return response

@app.post("/users/", response_model=schemas.UserCreate)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
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

@app.delete("/chatboxes/{chat_box_id}/", response_model=schemas.ChatBoxDeleteResponse)
def delete_chat_box(chat_box_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if not crud.check_chatbox_ownership(db, user_id=current_user.id, chat_box_id=chat_box_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this chat box")
    return JSONResponse(content={"result": crud.delete_chat_box(db, chat_box_id)})

@app.get("/chatboxes/{chat_box_id}/messages/", response_model=List[schemas.ChatMessage])
def get_chat_history(chat_box_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if not crud.check_chatbox_ownership(db, user_id=current_user.id, chat_box_id=chat_box_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this chat box")
    return crud.get_chat_history(db=db, chat_box_id=chat_box_id)

@app.get("/auth/google")
async def login_with_google(request: Request):
    redirect_uri = request.url_for('google_callback')
    session = request.session
    print(session)  # Print session content for debugging
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    # Complete the OAuth flow
    session = request.session
    print(session)  # Print session content for debugging
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return JSONResponse(content={"error": e.error, "error_description": e.description, "error_uri": e.uri})
    user_info = token["userinfo"]

    user = crud.get_user_by_username(db, username=user_info['email'])
    if not user:
        user_in = schemas.UserCreate(username=user_info['email'], password='sub', email=user_info['email'], full_name=user_info['name'])
        user = crud.create_user(db=db, user=user_in)

    access_token = create_access_token(data={"sub": user.username, "id": user.id})
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60)
    return response

@app.get('/logout')
def logout(request: Request):
    # Clear session data
    request.session.clear()
    # Redirect to home page and clear cookie
    response = RedirectResponse(url='/')
    response.delete_cookie('access_token')
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)