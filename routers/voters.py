import sys
sys.path.append("..")

from starlette.responses import RedirectResponse
from starlette import status

from os import stat
from typing import Optional
from fastapi import Depends, HTTPException, status, APIRouter, Request, Form
import models
from database import SessionLocal, engine
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/voters",
    tags=["voters"],
    responses={404: {"description":"Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        

@router.get("/", response_class=HTMLResponse)
async def read_all_voters(request: Request, db: Session = Depends(get_db)):
    voters = db.query(models.Voter).all()
    return templates.TemplateResponse("voter.html", {"request": request, "voters": voters})

@router.get("/create-voter", response_class=HTMLResponse)
async def view_create_voter(request: Request, db: Session = Depends(get_db)):
    cities = db.query(models.Cities).all()
    return templates.TemplateResponse("register-voter.html", {"request": request, "cities": cities})

@router.post("/create-voter", response_class=HTMLResponse)
async def create_voter(
        request: Request, 
        name: str = Form(...), 
        lastname: str = Form(...), 
        document_id: int = Form(...),
        gender: str = Form(...),
        cities_id: int = Form(...),
        db: Session = Depends(get_db)
    ):
    voter_model = models.Voter()
    voter_model.name = name
    voter_model.lastname = lastname
    voter_model.document_id = document_id
    voter_model.gender = gender
    voter_model.cities_id = cities_id
    voter_model.has_voted = False
    
    db.add(voter_model)
    db.commit()
    
    return RedirectResponse(url="/voters", status_code=status.HTTP_302_FOUND)

@router.get("/edit-voter/{voter_id}", response_class=HTMLResponse)
async def view_edit_voter(request: Request, voter_id: int, db: Session = Depends(get_db)):
    cities = db.query(models.Cities).all()
    voter = db.query(models.Voter).filter(models.Voter.id == voter_id).first()
    return templates.TemplateResponse("edit-voter.html", {"request": request, "cities": cities, "voter": voter})


@router.post("/edit-voter/{voter_id}", response_class=HTMLResponse)
async def edit_voter(
        request: Request, 
        voter_id: int,
        name: str = Form(...), 
        lastname: str = Form(...), 
        db: Session = Depends(get_db)
    ):
    voter_model = db.query(models.Voter).filter(models.Voter.id == voter_id).first()
    voter_model.name = name
    voter_model.lastname = lastname
    voter_model.has_voted = False
    
    db.add(voter_model)
    db.commit()
    
    return RedirectResponse(url="/voters", status_code=status.HTTP_302_FOUND)

@router.get("/delete-voter/{voter_id}", response_class=HTMLResponse)
async def delete_voter(request: Request, voter_id: int, db: Session = Depends(get_db)):
    
    voter = db.query(models.Voter).filter(models.Voter.id == voter_id).first()
    if voter is None:
        return RedirectResponse(url="/voters", status_code=status.HTTP_302_FOUND)
    db.query(models.Voter).filter(models.Voter.id == voter_id).delete()
    db.commit()
    
    return RedirectResponse(url="/voters", status_code=status.HTTP_302_FOUND)