from fastapi import APIRouter, Depends, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from app import crud, models, auth
from app.database import get_db

# Create a new router for the dashboard
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# Configure the HTML template directory
templates = Jinja2Templates(directory="templates")

# --- Page Rendering Endpoints ---

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serves the login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, current_partner: models.Partner = Depends(auth.get_current_partner)):
    """
    Serves the main dashboard page.
    This endpoint is protected; it requires a valid partner login.
    """
    # We pass the partner's username to the template to personalize it.
    return templates.TemplateResponse("dashboard.html", {"request": request, "partner_name": current_partner.username})

# --- Authentication Endpoints ---

@router.post("/token")
async def login_for_access_token(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Handles the login form submission.
    It verifies credentials and returns a redirect response with a session cookie.
    """
    partner = crud.get_partner_by_username(db, username=username)
    if not partner or not auth.verify_password(password, partner.hashed_password):
        # In a real app, you would show an error message on the login page.
        # For now, we raise an exception.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = auth.create_access_token(
        data={"sub": partner.username}, expires_delta=access_token_expires
    )
    
    # Redirect to the main dashboard page and set the token in a secure cookie
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.get("/logout")
async def logout():
    """Logs the partner out by clearing the session cookie."""
    response = RedirectResponse(url="/dashboard/login")
    response.delete_cookie(key="access_token")
    return response

# --- API Endpoints for Data Management (Future) ---
# We will build these out next. They will power the interactive parts of the dashboard.

# @router.get("/api/events")
# async def get_events(current_partner: models.Partner = Depends(auth.get_current_partner)):
#     # Logic to fetch events for this partner
#     return {"message": "Event data will be here"}
