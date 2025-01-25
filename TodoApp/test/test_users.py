from ..routers.users import get_db, get_current_user
from fastapi import status
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# username="devbaoo",
#         email="devbaoo712@email.com",
#         first_name="devbaoo",
#         last_name="dev",
#         hashed_password=bcrypt_context.hash("testpassword"),
#         role="admin",
#         phone_number="(111)-111-1111"

def test_get_user(test_user):
    responses = client.get("/user")
    assert responses.status_code == status.HTTP_200_OK
    assert responses.json()['username'] == 'devbaoo'
    assert responses.json()['email'] == 'devbaoo712@email.com'
    assert responses.json()['first_name'] == 'devbaoo'
    assert responses.json()['last_name'] == 'dev'
    assert responses.json()['role'] == 'admin'
    assert responses.json()['phone_number'] == '(111)-111-1111'

def test_change_password(test_user):
    request_body = {
        "old_password": "testpassword",
        "new_password": "newtestpassword"
    }
    responses = client.patch("/user/change_password", json=request_body)
    assert responses.status_code == status.HTTP_200_OK
    assert responses.json()['message'] == 'Change password succesfull'


def test_change_password_wrong_password(test_user):
    request_body = {
        "old_password": "wrongpassword",
        "new_password": "adads"
    }
    responses = client.patch("/user/change_password", json=request_body)
    assert responses.status_code == status.HTTP_401_UNAUTHORIZED
    assert responses.json()['detail'] == 'Error password'

def test_change_phone_number(test_user):
    responses = client.patch("/user/change_phone_number?phone_number=2222222222")
    assert responses.status_code == status.HTTP_200_OK
    assert responses.json()['message'] == 'Change phone succesfull'