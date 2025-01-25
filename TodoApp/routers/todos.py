from fastapi import APIRouter
from typing import Annotated
from fastapi import HTTPException

from fastapi import  Depends, Path, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="TodoApp/templates")


router = APIRouter(
    prefix='/todo',
    tags=['todo']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt = 0, lt =6)
    complete: bool

def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response
### Pages

@router.get("/todo-page")
async def render_todo_page(request : Request, db : db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

        return templates.TemplateResponse("todo.html", {"request" : request, "todos" : todos, "user" : user})
    except:
        return redirect_to_login()
@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{id}")
async def render_edit_todo_page(request: Request, id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

    except:
        return redirect_to_login()
## Endpoints


@router.get("", status_code=status.HTTP_200_OK)
async def get_all(user : user_dependency, db:db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_one(user : user_dependency,db:db_dependency, id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    todo_model = (db.query(Todos).filter(Todos.id ==id).
                  filter(Todos.owner_id == user.get('id')).first())
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="NOT FOUND")

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db : db_dependency,
                      new_todo : TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = Todos(
        title=new_todo.title,
        description=new_todo.description,
        priority= new_todo.priority,
        complete=new_todo.complete,
        owner_id = user.get('id')
    )

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_todo(user : user_dependency,db: db_dependency,
                      up_todo: TodoRequest, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = (db.query(Todos).filter(Todos.id == id).
                  filter(Todos.owner_id == user.get('id')).first())
    if todo_model is None:
        raise HTTPException(404, "Todo not found")

    todo_model.title = up_todo.title
    todo_model.description = up_todo.description
    todo_model.priority = up_todo.priority
    todo_model.complete = up_todo.complete

    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_todo(user : user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = (db.query(Todos).filter(Todos.id == id)
                  .filter(Todos.owner_id == user.get('id')).first())
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not found")

    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
