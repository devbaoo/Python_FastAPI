from datetime import timedelta, datetime


from fastapi import APIRouter, Depends,Path
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose.constants import ALGORITHMS
from pydantic import BaseModel
from ..models import Users
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from typing import Annotated
from ..database import SessionLocal
from jose import jwt, JWTError


router = APIRouter(
   prefix='/auth',
   tags=['auth']
)


SECRET_KEY = 'fdb9742c6b23843a97a30d674c4f96b3a987f9827ad4690b1e38e5154e61d372'
ALGORITHM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
   email: str
   username: str
   first_name: str
   last_name: str
   password: str
   role: str
   phone_number: str


class Token(BaseModel):
   access_token: str
   token_type: str




def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()




db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username : str, password : str,db):
   user = db.query(Users).filter(Users.username == username).first()
   if not user:
       return False
   if not bcrypt_context.verify(password, user.hashed_password):
       return False
   return user


def create_access_token(username: str, user_id: int,role :str, expires_delta: timedelta):
   encode = {'sub': username, 'id': user_id, 'role' : role}
   expires = datetime.utcnow() + expires_delta
   encode.update({'exp': expires})
   return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token : Annotated[str, Depends(oauth2_bearer)]):
   try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       username: str = payload.get('sub')
       user_id: int = payload.get('id')
       user_role : str = payload.get('role')
       if username is None or user_id is None:
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                               detail='Could not validate user.')
       return {'username': username, 'id' : user_id , 'user_role': user_role}
   except JWTError:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                           detail='Could not validate user.')






@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, new_user: CreateUserRequest):
   user_model = Users(
       email=new_user.email,
       username=new_user.username,
       first_name=new_user.first_name,
       last_name=new_user.last_name,
       hashed_password=bcrypt_context.hash(new_user.password),
       is_active=True,
       role=new_user.role,
       phone_number = new_user.phone_number
   )
   db.add(user_model)
   db.commit()
   db.refresh(user_model)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                db : db_dependency):
   user = authenticate_user(form_data.username, form_data.password, db)
   if not user:
      return 'Fail Auth'
   token = create_access_token(user.username, user.id,user.role , timedelta(minutes=20))
   return {"access_token": token, "token_type": "bearer"}
