from fastapi import FastAPI
from app.api import auth
from app.core.database import engine, Base
from app.core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MagicPic Backend", version="1.0.0")

app.include_router(auth.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to MagicPic API"}
