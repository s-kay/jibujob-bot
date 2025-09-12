from fastapi import APIRouter, Depends, Request, Form, status, HTTPException, Response
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
async def dashboard_home(request: Request, db: Session = Depends(get_db), current_partner: models.Partner = Depends(auth.get_current_partner)):
    """Serves the main dashboard page, pre-loading it with the partner's data."""
    events = crud.get_events_by_partner(db, partner_id=current_partner.id)
    featured_jobs = crud.get_featured_jobs_by_partner(db, partner_id=current_partner.id)
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "partner_name": current_partner.partner_name,
        "events": events,
        "featured_jobs": featured_jobs
    })

# --- Authentication Endpoints ---

@router.post("/token")
async def login_for_access_token(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Handles the login form submission.
    It verifies credentials and returns a redirect response with a session cookie.
    """
    partner = crud.get_partner_by_username(db, username=username)
    if not partner or not auth.verify_password(password, partner.hashed_password):
        # pass an error message back to the login page
        error_message = "Incorrect username or password. Please try again."
        return templates.TemplateResponse("login.html", {"request": request, "error": error_message})
    
    access_token = auth.create_access_token(data={"sub": partner.username})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, samesite="lax")
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/dashboard/login")
    response.delete_cookie(key="access_token")
    return response

# --- API Endpoints for Data Management ---
@router.post("/api/events")
async def api_create_event(title: str = Form(...), description: str = Form(...), date: str = Form(...), location: str = Form(...), db: Session = Depends(get_db), current_partner: models.Partner = Depends(auth.get_current_partner)):
    event_data = {"title": title, "description": description, "date": date, "location": location}
    crud.create_event(db, event_data=event_data, partner=current_partner)
    return {"status": "success", "message": "Event created!"}

@router.delete("/api/events/{event_id}")
async def api_delete_event(event_id: int, db: Session = Depends(get_db), current_partner: models.Partner = Depends(auth.get_current_partner)):
    success = crud.delete_event(db, event_id=event_id, partner_id=current_partner.id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found or you do not have permission to delete it.")
    return {"status": "success", "message": "Event deleted!"}

@router.post("/api/jobs")
async def api_create_featured_job(title: str = Form(...), keywords: str = Form(...), link: str = Form(...), db: Session = Depends(get_db), current_partner: models.Partner = Depends(auth.get_current_partner)):
    job_data = {"title": title, "keywords": keywords, "link": link}
    crud.create_featured_job(db, job_data=job_data, partner=current_partner)
    return {"status": "success", "message": "Job created!"}

@router.delete("/api/jobs/{job_id}")
async def api_delete_featured_job(job_id: int, db: Session = Depends(get_db), current_partner: models.Partner = Depends(auth.get_current_partner)):
    success = crud.delete_featured_job(db, job_id=job_id, partner_id=current_partner.id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or you do not have permission to delete it.")
    return {"status": "success", "message": "Job deleted!"}
