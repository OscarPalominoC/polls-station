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
    prefix="/cities",
    tags=["cities"],
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
async def read_cities(request: Request, db: Session = Depends(get_db)):
    cities = db.query(models.Cities).all()
    return templates.TemplateResponse("cities-list.html", {"request": request, "cities": cities})

@router.get("/create-city", response_class=HTMLResponse)
async def view_create_city(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("create-city.html", {"request": request})

@router.post("/create-city", response_class=HTMLResponse)
async def create_city(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...)
):
    city_model = models.Cities()
    city_model.name = name
    
    db.add(city_model)
    db.commit()
    
    return RedirectResponse(url="/cities", status_code=status.HTTP_302_FOUND)

@router.get("/edit-city/{city_id}", response_class=HTMLResponse)
async def view_edit_city(
    request: Request,
    city_id: int,
    db: Session = Depends(get_db)
):
    city = db.query(models.Cities).filter(models.Cities.id == city_id).first()
    if city == None:
        return RedirectResponse(url="/cities", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("edit-city.html", {"request": request, "city": city})

@router.post("/edit-city/{city_id}", response_class=HTMLResponse)
async def edit_city(
    request: Request,
    city_id: int,
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    city = db.query(models.Cities).filter(models.Cities.id == city_id).first()
    city.name = name
    
    db.add(city)
    db.commit()
    
    return RedirectResponse(url="/cities", status_code=status.HTTP_302_FOUND)
    
@router.get("/delete-city/{city_id}", response_class=HTMLResponse)
async def delete_city(request: Request, city_id: int, db: Session = Depends(get_db)):
    city_model = db.query(models.Cities).filter(models.Cities.id == city_id).first()
    if city_model is None:
        return RedirectResponse(url="/cities", status_code=status.HTTP_302_FOUND)
    db.query(models.Cities).filter(models.Cities.id == city_id).delete()
    db.commit()
    
    return RedirectResponse(url=("/cities"), status_code=status.HTTP_302_FOUND)