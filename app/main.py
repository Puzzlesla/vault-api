from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from app.routers import pages
from app.db.base import Base
from app.db.session import engine
from app.api.routes import auth, users, notes
from app.utils.env_verify import verify_env
from app.utils.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
    )

verify_env()


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    # Initialize database connection, create tables, etc.
    Base.metadata.create_all(bind=engine)
    
    yield # App runs here
    
    # Shutdown logic
    # Close database connection, cleanup resources, etc.
    pass



app = FastAPI(title="Vault API", lifespan=lifespan)

#Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Page routers (returns HTML templates)
app.include_router(pages.router)
