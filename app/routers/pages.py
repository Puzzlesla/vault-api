
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse



router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")

# Page routes for the application  
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(url="/login")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/notes", response_class=HTMLResponse)
def notes_page(request: Request):
    return templates.TemplateResponse("notes.html", {"request": request})
    
@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request):
    return templates.TemplateResponse("password_reset.html", {"request": request})

