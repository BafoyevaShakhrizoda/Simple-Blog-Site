from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Database jadvalarini yaratish
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=" Blog site with FastAPI ")

# Templates va static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Bosh sahifa - barcha postlar
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).all()
    return templates.TemplateResponse("home.html", {
        "request": request,
        "posts": posts
    })

# Bitta postni ko'rish
@app.get("/post/{post_id}", response_class=HTMLResponse)
def view_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    return templates.TemplateResponse("post.html", {
        "request": request,
        "post": post
    })

# Yangi post yaratish sahifasi
@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

# Yangi post saqlash
@app.post("/create")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_db)
):
    new_post = models.Post(title=title, content=content, author=author)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return RedirectResponse(url="/", status_code=303)

# API endpoint - JSON ko'rinishida
@app.get("/api/posts", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()