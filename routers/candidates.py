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

