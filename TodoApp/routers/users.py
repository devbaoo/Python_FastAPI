from fastapi import APIRouter
from typing import Annotated
from fastapi import HTTPException
from fastapi import  Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status


from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user, bcrypt_context


router = APIRouter(
   prefix='/user',
   tags=['user']
)


def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class change_password(BaseModel):
   old_password : str
   new_password : str = Field(min_length=3)




@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user : user_dependency, db : db_dependency):
   if user is None:
       raise HTTPException(status_code=401, detail='Authentication Failed')
   user_model = db.query(Users).filter(Users.id == user.get('id')).first()
   return user_model


@router.patch("/change_password", status_code=status.HTTP_200_OK)
async def change_password (user : user_dependency,
                          db : db_dependency, update_password : change_password ):
   if user is None:
       raise HTTPException(status_code=401, detail='Authentication Failed')


   user_model = db.query(Users).filter(Users.id == user.get('id')).first()
   if not bcrypt_context.verify(update_password.old_password, user_model.hashed_password):
       raise HTTPException(status_code=401, detail='Error password')
   user_model.hashed_password = bcrypt_context.hash(update_password.new_password)
   db.add(user_model)
   db.commit()
   return {"message" : 'Change password succesfull'}


@router.patch("/change_phone", status_code=status.HTTP_200_OK)
async def change_phone (user : user_dependency,
                        db : db_dependency, phone_number : str):
   if user is None:
       raise HTTPException(status_code=401, detail='Authentication Failed')
   user_model = db.query(Users).filter(Users.id == user.get('id')).first()
   user_model.phone_number = phone_number
   db.add(user_model)
   db.commit()
   return {"message" : 'Change phone succesfull'}
