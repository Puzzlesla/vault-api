from fastapi import FastAPI
from app.api.routes import auth, users, notes
import app.utils.env_verify import verify_env
from app.utils.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
    )

verify_env()

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)

# Lifespan
@app.on_event("startup")
async def startup_event():
    # Initialize database connection, create tables, etc.
    pass
@app.on_event("shutdown")
async def shutdown_event():
    # Close database connection, cleanup resources, etc.
    pass

# Middleware


#Error handlers
@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )

@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_exception_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"message": str(exc)}
    )

@app.exception_handler(UserNotFoundException)
async def user_not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)}
    )
