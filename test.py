from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean

from database import get_db, Base
from main import app

TEST_DATABASE_URL = 'postgresql://postgres:gai3905@localhost/test_pokemon'

# Create an engine and a session for the test database
test_engine = create_engine(TEST_DATABASE_URL, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

client = TestClient(app)


# Override the database dependency for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency in the FastAPI app
app.dependency_overrides[get_db] = override_get_db


def create_all_tables():
    """Setup for the tests: create the database tables."""
    Base.metadata.create_all(bind=test_engine)


def drop_all_tables():
    """Drp for the tests: drop the database tables."""
    Base.metadata.drop_all(bind=test_engine)


def test_route():
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {'message': 'Server is running'}


def test_create_pokemon():
    """Add a sample Pokemon to the database for testing."""
    response = client.post(
        "/pokemon", json={
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
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Pikachu"


def test_read_pokemon_by_existing_id():
    response = client.get("/pokemon/1")
    assert response.status_code == 200
    data = response.json()
    assert data


def test_read_pokemon_by_non_existing_id():
    response = client.get("/pokemon/1000")
    assert response.status_code == 404
    assert response.json() == {"detail": "Pokemon not found."}


def test_update_pokemon():
    """Test updating an existing Pokemon in the database."""

    # Create a sample Pokemon to update
    response_create = client.post(
        "/pokemon", json={
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
    )

    assert response_create.status_code == 201
    pokemon_id = response_create.json()["id"]

    # Update the Pokemon
    updated_data = {
        "name": "Raichu",
        "type_1": "Electric",
        "type_2": None,
        "total": 480,
        "hp": 60,
        "attack": 90,
        "defense": 55,
        "sp_atk": 90,
        "sp_def": 80,
        "speed": 110,
        "generation": 1,
        "legendary": False
    }

    response_update = client.put(f"/pokemon/{pokemon_id}", json=updated_data)

    assert response_update.status_code == 202
    assert response_update.json()["name"] == "Raichu"


def test_update_nonexistent_pokemon():
    """Test updating a non-existent Pokemon, expecting 404 Not Found error."""

    invalid_pokemon_id = 9999

    updated_data = {
        "name": "Raichu",
        "type_1": "Electric",
        "type_2": None,
        "total": 480,
        "hp": 60,
        "attack": 90,
        "defense": 55,
        "sp_atk": 90,
        "sp_def": 80,
        "speed": 110,
        "generation": 1,
        "legendary": False
    }

    # update the Pokemon with an invalid ID
    response = client.put(f"/pokemon/{invalid_pokemon_id}", json=updated_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Pokemon not found."


def test_update_existing_pokemon_patch():
    """Test updating an existing Pokemon should return the updated Pokemon data."""

    pokemon_id = 1
    updated_data = {
        "name": "Pikachu Updated",
        "type_1": "Electric",
        "total": 320,
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "sp_atk": 50,
        "sp_def": 50,
        "speed": 90,
        "generation": 2,
        "legendary": False
    }

    response = client.patch(f"/pokemon/{pokemon_id}", json=updated_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pikachu Updated"
    assert data["type_1"] == "Electric"


def test_update_non_existent_pokemon_patch():
    """Test updating a Pokemon that does not exist should return 404."""

    non_existent_pokemon_id = 9999

    updated_data = {
        "name": "Pikachu patch updated",
        "type_1": "Electric",
        "total": 320,
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "sp_atk": 50,
        "sp_def": 50,
        "speed": 90,
        "generation": 2,
        "legendary": False
    }

    response = client.patch(f"/pokemon/{non_existent_pokemon_id}", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == f"Pokemon with id {non_existent_pokemon_id} doesn't exist."


def test_delete_existing_pokemon():
    """Test deleting an existing Pokemon should return a success message."""

    existing_pokemon_id = 1
    response = client.delete(f"/pokemon/{existing_pokemon_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Pokemon deleted successfully."}


def test_delete_non_existent_pokemon():
    """Test deleting a Pokemon that does not exist should return 404."""

    non_existent_pokemon_id = 9999
    response = client.delete(f"/pokemon/{non_existent_pokemon_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokemon not found."
