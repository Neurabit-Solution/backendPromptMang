from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.core.database import engine, Base
from app.core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MagicPic Backend", version="1.0.0")

# Allow local frontend dev server to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    # Allow any localhost port for dev tooling
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Normalize validation errors to frontend spec
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_code = "INVALID_REQUEST"
    for err in exc.errors():
        field = ".".join(str(part) for part in err.get("loc", []) if part != "body")
        if "email" in field:
            error_code = "INVALID_EMAIL"
            break
        if "password" in field:
            error_code = "WEAK_PASSWORD"
            break

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": "Invalid request. Please check your input.",
            },
        },
    )

app.include_router(auth.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to MagicPic API"}
