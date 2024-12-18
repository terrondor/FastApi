from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from database import SessionLocal, NoteModel, Base
from sqlalchemy.orm import Session

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Модель данных для заметки
class Note(BaseModel):
    id: int
    title: str
    content: str


# Эндпоинт для отображения домашней страницы
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db), message: str = ""):
    notes = db.query(NoteModel).all()
    return templates.TemplateResponse(
        "home.html", {"request": request, "notes": notes, "message": message}
    )


# Эндпоинт для создания новой заметки
@app.post("/notes")
def create_note(
    title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)
):
    note = NoteModel(title=title, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return RedirectResponse(url="/?message=Заметка успешно добавлена!", status_code=303)


# Эндпоинт для редактирования заметки
@app.get("/notes/edit/{note_id}", response_class=HTMLResponse)
def edit_note_form(request: Request, note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return templates.TemplateResponse(
        "edit_note.html", {"request": request, "note": note}
    )

# Эндпоинт для редактирования заметки
@app.post("/notes/edit/{note_id}")
def edit_note(note_id: int, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = title
    note.content = content
    db.commit()
    return RedirectResponse(url="/?message=Заметка успешно отредактирована!", status_code=303)

# Эндпоинт для удаления заметки
@app.post("/notes/delete/{note_id}")
def delete_note_redirect(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return RedirectResponse(url="/?message=Заметка успешно удалена!", status_code=303)


# Эндпоинт для редактирования заметки
@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, updated_note: Note, db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.title = updated_note.title
    note.content = updated_note.content
    db.commit()
    db.refresh(note)
    return note

# Эндпоинт для удаления заметки
@app.delete("/notes/{note_id}", response_model=Note)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return note

# Эндпоинт для удаления заметки с перенаправлением
@app.post("/notes/delete/{note_id}")
def delete_note_redirect(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return RedirectResponse(url="/?message=Заметка успешно удалена!", status_code=303)

# Эндпоинт для редактирования заметки с перенаправлением
@app.get("/notes/edit/{note_id}", response_class=HTMLResponse)
def edit_note_form(request: Request, note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return templates.TemplateResponse("edit_note.html", {"request": request, "note": note})

@app.post("/notes/edit/{note_id}")
def edit_note(note_id: int, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.title = title
    note.content = content
    db.commit()
    return RedirectResponse(url="/?message=Заметка успешно отредактирована!", status_code=303)
    
