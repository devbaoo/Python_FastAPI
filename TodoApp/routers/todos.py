from fastapi import APIRouter
from typing import Annotated
from fastapi import HTTPException


from fastapi import  Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status


from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user


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
   return {"detail": "Todo deleted successfully"}
