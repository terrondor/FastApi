from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Модель данных для заметки
class Note(BaseModel):
    id: int
    title: str
    content: str


# Список для хранения заметок
notes_db = []


# Эндпоинт для отображения домашней страницы
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, message: str = ""):
    return templates.TemplateResponse(
        "home.html", {"request": request, "notes": notes_db, "message": message}
    )


# Эндпоинт для получения всех заметок
@app.get("/notes", response_model=List[Note])
def get_notes():
    return notes_db


# Эндпоинт для получения заметки по ID
@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    note = next((note for note in notes_db if note.id == note_id), None)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


# Эндпоинт для создания новой заметки
@app.post("/notes")
def create_note(title: str = Form(...), content: str = Form(...)):
    note_id = len(notes_db) + 1  # Простая генерация ID
    note = Note(id=note_id, title=title, content=content)
    notes_db.append(note)
    # Перенаправление обратно на главную страницу
    return RedirectResponse(url="/?message=Заметка успешно добавлена!", status_code=303)


# Эндпоинт для редактирования заметки
@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, updated_note: Note):
    note_index = next(
        (index for index, note in enumerate(notes_db) if note.id == note_id), None
    )
    if note_index is None:
        raise HTTPException(status_code=404, detail="Note not found")
    notes_db[note_index] = updated_note
    return updated_note


# Эндпоинт для удаления заметки
@app.delete("/notes/{note_id}", response_model=Note)
def delete_note(note_id: int):
    note_index = next(
        (index for index, note in enumerate(notes_db) if note.id == note_id), None
    )
    if note_index is None:
        raise HTTPException(status_code=404, detail="Note not found")
    deleted_note = notes_db.pop(note_index)
    return deleted_note


# Эндпоинт для удаления заметки с перенаправлением
@app.post("/notes/delete/{note_id}")
def delete_note_redirect(note_id: int):
    note_index = next(
        (index for index, note in enumerate(notes_db) if note.id == note_id), None
    )
    if note_index is None:
        raise HTTPException(status_code=404, detail="Note not found")
    deleted_note = notes_db.pop(note_index)
    return RedirectResponse(url="/?message=Заметка успешно удалена!", status_code=303)


# Эндпоинт для редактирования заметки с перенаправлением
@app.get("/notes/edit/{note_id}", response_class=HTMLResponse)
def edit_note_form(request: Request, note_id: int):
    note = next((note for note in notes_db if note.id == note_id), None)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return templates.TemplateResponse(
        "edit_note.html", {"request": request, "note": note}
    )


@app.post("/notes/edit/{note_id}")
def edit_note(note_id: int, title: str = Form(...), content: str = Form(...)):
    note_index = next(
        (index for index, note in enumerate(notes_db) if note.id == note_id), None
    )
    if note_index is None:
        raise HTTPException(status_code=404, detail="Note not found")
    updated_note = Note(id=note_id, title=title, content=content)
    notes_db[note_index] = updated_note
    return RedirectResponse(
        url="/?message=Заметка успешно отредактирована!", status_code=303
    )
