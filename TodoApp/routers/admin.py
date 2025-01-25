from fastapi import APIRouter
from typing import Annotated
from fastapi import HTTPException

from fastapi import  Depends, Path
from sqlalchemy.orm import Session
from starlette import status

from ..models import Todos, Users
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def get_all(user : user_dependency, db : db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).all()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo (user : user_dependency, db : db_dependency, id : int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()

@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users(user : user_dependency, db : db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).all()