import pytest
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.app.database.database import Base, get_db
from src.app.main import app

# Set up a test database URL
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:gai3905@localhost/test_pokemon"

# Create a test engine and session for database transactions
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Dependency override for using the test database in the app
def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Apply the dependency override to use the test database
app.dependency_overrides[get_db] = override_get_db


# Fixture to set up and tear down the test database schema before and after tests
@pytest.fixture(scope="module")
def test_db():
    # Create all tables in the test database
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests are completed
    Base.metadata.drop_all(bind=engine)


# Fixture to provide a test client for API requests
@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def user_data():
    return {
        "username": "testuser",
        "password": "password123",
        "role": "user"
    }


@pytest.fixture()
def admin_data():
    return {
        "username": "testuser",
        "password": "password123",
        "role": "admin"
    }


@pytest.fixture()
def create_user(client, test_db, admin_data):
    response = client.post("/auth/user", json=admin_data)
    return response.json()


@pytest.fixture
def get_auth_token(client, create_user, admin_data):
    # username, password, role = login_data
    response = client.post("/auth/token", data={"username": admin_data["username"], "password": admin_data["password"]})
    return response.json().get("access_token")
    # return _get_auth_token


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
        "name": "Pikachu",
        "type_1": "Electric",
        "type_2": None,
        "total": 320,
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "sp_atk": 50,
        # "sp_def": 50,
        "speed": 90,
        "generation": 111,
        "legendary": False
    }


@pytest.fixture(scope="function")
def db() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def create_pokemon(db: Session):
    from src.app.factories.pokemon_factory import PokemonFactory
    PokemonFactory.set_session(db)

    def _create_pokemon(**kwargs):
        pokemon_data = PokemonFactory.create_pokemon(**kwargs)
        return pokemon_data

    return _create_pokemon
