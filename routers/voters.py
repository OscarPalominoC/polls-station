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
async def create_voter():pass