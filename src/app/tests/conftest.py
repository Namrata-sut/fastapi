import os

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.app.database.database import get_db
from src.app.factories.user_factory import UserFactory
from src.app.main import app
from src.app.models.models import Base, UserRole, Users

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:gai3905@localhost/test_pokemon"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def set_secret_key():
    os.environ["SECRET_KEY"] = "9ifjp02349ht8934ht438tguj39p048u348938834"


# Create the database tables
# @pytest.fixture(scope="session", autouse=True)
# def setup_database():
#     # Create the test database schema
#     Base.metadata.create_all(bind=engine)
#     yield
#     # Drop all tables after tests are done
#     Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Drop all tables if they already exist
    Base.metadata.drop_all(bind=engine)
    # Create the test database schema
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture(params=[
    ("testuser1323", "testpassword1", UserRole.user),
])
def user_data(request):
    return request.param


@pytest.fixture(params=[
    ("testuser1323", "testpassword2", UserRole.admin)
])
def admin_data(request):
    return request.param


@pytest.fixture
def create_user(db: Session):
    def _create_user(**kwargs):
        UserFactory.set_session(db)
        user_data = UserFactory.create_user(session=db, **kwargs)
        print(f"User created in DB: {user_data}")
        return user_data

    return _create_user


@pytest.fixture
def get_auth_token(client, create_user):
    def _get_auth_token(username, password, role):
        response = client.post("/auth/token", data={"username": username, "password": password, "role": role})
        return response.json().get("access_token")

    return _get_auth_token


@pytest.fixture
def valid_pokemon_data():
    return {
        "name": "Pikachu",
        "type_1": "Electric",
        "type_2": None,
        "total": 320,
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "sp_atk": 50,
        "sp_def": 50,
        "speed": 90,
        "generation": 1,
        "legendary": False
    }


@pytest.fixture
def invalid_pokemon_data():
    return {
        "name": "",  # Invalid name
        "type_1": "Electric",
        "type_2": None,
        "total": 320,
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "sp_atk": 50,
        "sp_def": 50,
        "speed": 90,
        "generation": 1,
        "legendary": False
    }


@pytest.fixture
def create_pokemon(db: Session):
    def _create_pokemon(**kwargs):
        from src.app.factories.pokemon_factory import PokemonFactory
        PokemonFactory.set_session(db)
        pokemon_data = PokemonFactory.create_pokemon(**kwargs)
        return pokemon_data

    return _create_pokemon
