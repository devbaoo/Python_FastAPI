from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..database import Base
from fastapi.testclient import TestClient
import pytest
from ..main import app
from ..models import Todos, Users, TaskLogs
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"



engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username" : "devbaoo", 'id' : 1, 'user_role' : 'admin'}

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo =  Todos(
        title="Learn FastAPI",
        description="Learn FastAPI from the basics",
        priority=1,
        complete=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        username="devbaoo",
        email="devbaoo712@email.com",
        first_name="devbaoo",
        last_name="dev",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="(111)-111-1111"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


@pytest.fixture
def test_tasklog():
    tasklog = TaskLogs(
        action="completed",
        timestamp=1677723200,
        todo_id=1,
        user_id=1
    )
    db = TestingSessionLocal()
    db.add(tasklog)
    db.commit()
    yield tasklog
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM task_logs;"))
        connection.commit()

