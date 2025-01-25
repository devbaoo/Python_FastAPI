
from ..routers.admin import get_db, get_current_user
from fastapi import status
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_all_todo(test_todo):
    responses = client.get("/admin/todo")
    assert responses.status_code == status.HTTP_200_OK
    assert responses.json() == [{'complete': False,
                                 'description': 'Learn FastAPI from the basics',
                                 'id': 1, 'owner_id': 1, 'priority': 1,
                                 'title': 'Learn FastAPI'}]

def test_delete_todo(test_todo):
    responses = client.delete('/admin/1')
    assert responses.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_not_found(test_todo):
    responses = client.delete('/admin/todo/1000')
    assert responses.status_code == status.HTTP_404_NOT_FOUND
