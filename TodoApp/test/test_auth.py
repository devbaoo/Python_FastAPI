from fastapi import HTTPException
from ..routers.auth import get_db, get_current_user, create_access_token, authenticate_user, SECRET_KEY, ALGORITHM, create_access_token
from .utils import *
from ..routers.auth import authenticate_user
from jose import jwt
from datetime import timedelta
import pytest

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_auth_user(test_user):
    db = TestingSessionLocal()
    auth_user =  authenticate_user(test_user.username, 'testpassword',db)
    assert auth_user is not None
    assert auth_user.username == test_user.username

    non_existent_user = authenticate_user('WrongUsername', 'testpassword', db)
    assert non_existent_user is False

    wrong_password = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password is False

def test_create_acess_token():
    username = 'testuser'
    user_id = 1
    role = 'admin'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY,
                               algorithms=[ALGORITHM],
                               options={"verify_signature": False})
    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user():
    encode = {'sub' : 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token = token)
    assert user == {'username': 'testuser','id': 1, 'user_role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'
