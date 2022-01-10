import re
from fastapi.param_functions import Query
from starlette import status

from os import stat
from typing import Optional
from fastapi import Depends, HTTPException, status, APIRouter, Request, Form
from starlette.responses import RedirectResponse
import models
from database import SessionLocal, engine
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/candidates",
    tags=["candidates"],
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
async def view_candidates(request: Request, db: Session = Depends(get_db)):
    candidates_db = db.query(models.Candidate).all()
    voters_list = db.query(models.Voter).all()
    cities_list = db.query(models.Cities).all()
    
    candidates = dict()
    candidates_list = []
    for candidate in candidates_db:
        candidates["affiliation"] = candidate.affiliation
        for voter in voters_list:
            if voter.id == candidate.voters_id:
                candidates["id"] = candidate.id
                candidates["name"] = f"{voter.name} {voter.lastname}"
                candidates["gender"] = voter.gender
                for city in cities_list:
                    if city.id == voter.cities_id:
                        candidates["city"] = city.name
                        break
                break
        candidates_list.append(candidates)
    
    return templates.TemplateResponse("candidates-list.html", {"request": request, "candidates": candidates_list})


@router.get("/register", response_class=HTMLResponse)
async def search_voter(request: Request, document_id: Optional[int] = Query(None, alias="document_id"), db: Session = Depends(get_db)):
    if document_id == None:
        return templates.TemplateResponse("register-candidate.html", {"request": request})
    voter = db.query(models.Voter).filter(models.Voter.document_id == document_id).first()
    city = db.query(models.Cities).filter(models.Cities.id == voter.cities_id).first()
    candidates = db.query(models.Candidate).all()
    for candidate in candidates:
        if candidate.id == voter.id:
            msg = "Candidate already registered."
            return templates.TemplateResponse("register-candidate.html", {"request": request, "msg": msg})
    return templates.TemplateResponse("register-candidate.html", {"request": request, "voter": voter, "city": city.name})

@router.post("/register", response_class=HTMLResponse)
async def register_candidate(
    request: Request, 
    voters_document_id: Optional[int] = Query(None, alias="document_id"), 
    affiliation: str = Form(...), 
    db: Session = Depends(get_db)
    ):
    voter = db.query(models.Voter).filter(models.Voter.document_id == voters_document_id).first()
    candidate_model = models.Candidate()
    candidate_model.voters_id = voter.id
    candidate_model.affiliation = affiliation
    candidate_model.is_candidate = True
    
    db.add(candidate_model)
    db.commit()
    
    return RedirectResponse(url="/candidates", status_code=status.HTTP_302_FOUND)

@router.get("/edit/{candidate_id}", response_class=HTMLResponse)
async def view_edit_candidate(request: Request, candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    return templates.TemplateResponse("edit-candidate.html", {"request": request, "candidate": candidate})