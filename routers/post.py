from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.database import get_db
from models import NoteModel
from schemas import Note

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Эндпоинт для отображения домашней страницы
@router.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db), message: str = ""):
    notes = db.query(NoteModel).all()
    return templates.TemplateResponse(
        "home.html", {"request": request, "notes": notes, "message": message}
    )


# Эндпоинт для создания новой заметки
@router.post("/notes")
def create_note(
    title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)
):
    note = NoteModel(title=title, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return RedirectResponse(url="/?message=Заметка успешно добавлена!", status_code=303)


# Эндпоинт для редактирования заметки с перенаправлением
@router.get("/notes/edit/{note_id}", response_class=HTMLResponse)
@router.put("/notes/{note_id}", response_model=Note)
@router.post("/notes/edit/{note_id}", response_class=HTMLResponse)
async def edit_note(
    note_id: int,
    request: Request,
    title: str = Form(None),
    content: str = Form(None),
    db: Session = Depends(get_db),
):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()

    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    if request.method == "POST":
        # Обработка формы редактирования
        note.title = title
        note.content = content
        db.commit()
        return RedirectResponse(
            url="/?message=Заметка успешно отредактирована!", status_code=303
        )

    # Отображение формы редактирования
    return templates.TemplateResponse(
        "edit_note.html", {"request": request, "note": note}
    )


# Эндпоинт для удаления заметки
@router.delete("/notes/{note_id}", response_model=Note)
@router.post("/notes/delete/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()
    return RedirectResponse(url="/?message=Заметка успешно удалена!", status_code=303)
