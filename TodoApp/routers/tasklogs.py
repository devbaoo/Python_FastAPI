
from fastapi import APIRouter
from typing import Annotated
from fastapi import HTTPException

from fastapi import  Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..models import TaskLogs, Todos
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/tasklog',
    tags=['tasklog']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TaskLogRequest(BaseModel):
    action: str
    timestamp : int
    todo_id : int

class Tasklogupdate(BaseModel):
    action: str = Field(min_length=1, max_length=100)
    timestamp : int = Field(gt = 0)

@router.get("", status_code=status.HTTP_200_OK)
async def get_all(user : user_dependency, db : db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(TaskLogs).filter(TaskLogs.user_id == user.get('id')).all()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tasklog(user : user_dependency,
                          db : db_dependency,
                          new_tasklog : TaskLogRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo = db.query(Todos).filter(Todos.id == new_tasklog.todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404,detail='Todo not found')
    tasklog_model = TaskLogs(
        action=new_tasklog.action,
        timestamp=new_tasklog.timestamp,
        user_id=user.get('id'),
        todo_id= new_tasklog.todo_id
    )
    db.add(tasklog_model)
    db.commit()
    db.refresh(tasklog_model)
    return tasklog_model

@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_tasklog(user : user_dependency,db : db_dependency, update_task_log : Tasklogupdate , id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    tasklog_model = db.query(TaskLogs).filter(TaskLogs.id == id).first()
    if tasklog_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    tasklog_model.action = update_task_log.action
    tasklog_model.timestamp = update_task_log.timestamp
    db.commit()
    db.refresh(tasklog_model)
    return tasklog_model

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_one(user : user_dependency,db : db_dependency, id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    tasklog_model = db.query(TaskLogs).filter(TaskLogs.id == id).first()
    if tasklog_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    return tasklog_model

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tasklog(user : user_dependency, db : db_dependency, id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    tasklog_model = db.query(TaskLogs).filter(TaskLogs.id == id).first()
    if tasklog_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    db.query(TaskLogs).filter(TaskLogs.id == id).delete()
    db.commit()

@router.patch("/change_action/{id}", status_code=status.HTTP_200_OK)
async  def change_action(user : user_dependency, db : db_dependency, id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    tasklog_model = db.query(TaskLogs).filter(TaskLogs.id == id).first()
    if tasklog_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    tasklog_model.action = 'completed'
    db.commit()
    return {"message" : 'Change action succesfull'}
