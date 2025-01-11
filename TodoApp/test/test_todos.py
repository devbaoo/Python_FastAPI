from ..routers.todos import get_db, get_current_user
from fastapi import status
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user






def test_get_all_authenticated(test_todo):
   responses = client.get("/todo")
   assert responses.status_code == status.HTTP_200_OK
   assert responses.json() == [{'complete': False,
                                'description': 'Learn FastAPI from the basics',
                                'id': 1, 'owner_id': 1, 'priority': 1,
                                'title': 'Learn FastAPI'}]


def test_get_one_authenticated(test_todo):
   responses = client.get("/todo/1")
   assert responses.status_code == status.HTTP_200_OK
   assert responses.json() == {'complete': False,
                                'description': 'Learn FastAPI from the basics',
                                'id': 1, 'owner_id': 1, 'priority': 1,
                                'title': 'Learn FastAPI'}


def test_read_one_authenticated_not_found():
   responses = client.get("/todo/111")
   assert responses.status_code == status.HTTP_404_NOT_FOUND
   assert responses.json() == {'detail': 'NOT FOUND'}


def test_create_todo(test_todo):
   request_body = {
       "title": "Learn FastAPI from the basics",
       "description": "Learn FastAPI from the basics",
       "priority": 1,
       "complete": False,
   }
   responses = client.post("/todo", json= request_body)
   assert responses.status_code == status.HTTP_201_CREATED


   db = TestingSessionLocal()
   model = db.query(Todos).filter(Todos.id == 2).first()
   assert model.title == request_body.get('title')
   assert model.description == request_body.get('description')
   assert model.priority == request_body.get('priority')
   assert model.complete == request_body.get('complete')




def test_update_todo(test_todo):
   request_body = {
       "title": "Learn FastAPI from the advanced",
       "description": "Learn FastAPI from the advanced",
       "priority": 1,
       "complete": False,
   }
   responses = client.put("/todo/1", json = request_body)
   assert responses.status_code == status.HTTP_200_OK


   db = TestingSessionLocal()
   model = db.query(Todos).filter(Todos.id == 1).first()
   assert model.title == request_body.get('title')
   assert model.description == request_body.get('description')
   assert model.priority == request_body.get('priority')
   assert model.complete == request_body.get('complete')


def test_update_not_found(test_todo):
   request_body = {
       "title": "Learn FastAPI from the advanced",
       "description": "Learn FastAPI from the advanced",
       "priority": 1,
       "complete": False,
   }
   responses = client.put("/todo/19009" , json = request_body)
   assert responses.status_code == status.HTTP_404_NOT_FOUND
   assert responses.json() == {'detail': "Todo not found"}


def test_delete(test_todo):
   responses = client.delete("/todo/1")
   assert responses.status_code == status.HTTP_204_NO_CONTENT


   db = TestingSessionLocal()
   model = db.query(Todos).filter(Todos.id == 1).first()
   assert model is None


def test_delete(test_todo):
   responses = client.delete("/todo/1")
   assert responses.status_code == status.HTTP_204_NO_CONTENT
