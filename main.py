from re import template
from fastapi import FastAPI, Depends, status, Form, Request
from fastapi.templating import Jinja2Templates
from typing import Optional

from starlette.responses import HTMLResponse, RedirectResponse

from routers import cities, voters, candidates

import models

from sqlalchemy.orm import Session
from database import SessionLocal, engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.include_router(cities.router)
app.include_router(voters.router)
app.include_router(candidates.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("home.html", {"request": request})

