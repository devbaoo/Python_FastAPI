from ..routers.tasklogs import get_db, get_current_user
from fastapi import status
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_all_tasklogs(test_tasklog):
    responses = client.get("/tasklog")
    assert responses.status_code == status.HTTP_200_OK
    assert responses.json() == [{
        "id": 1,
        "action": "completed",
        'timestamp' : 1677723200,
        'todo_id' : 1,
        'user_id' : 1
    }]

def test_get_one_tasklog(test_tasklog):
    responses = client.get("/tasklog/1")
    assert responses.status_code == status.HTTP_200_OK
    assert responses.json() == {
        "id": 1,
        "action": "completed",
        'timestamp' : 1677723200,
        'todo_id': 1,
        'user_id': 1
    }
