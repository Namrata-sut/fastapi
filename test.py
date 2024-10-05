from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, engine

client = TestClient(app)
db = SessionLocal()


# Override the database dependency for testing
def override_get_db():
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[db] = override_get_db


class Test_Pokemon:

    def test_main(self):
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "Server is running"}

    def test_get_pokemon_by_id(self):
        response = client.get("/pokemon/10")
        assert response.status_code == 200
        assert response.json()["detail"] == "Pokemon found.."

    def test_get_pokemon_by_id_not_found(self):
        response = client.get("/pokemon/10009")
        assert response.status_code == 404
        assert response.json()["detail"] == "Pokemon not found.."

    def test_get_pokemon_invalid_id(self):
        response = client.get("/pokemon/invalid_id")
        assert response.status_code == 422

    def test_add_pokemon(self):
        pokemon_data = {
            "id": 0,
            "name": "Test Pokémon",
            "type_1": "Fire",
            "type_2": "Grass",
            "total": 100,
            "hp": 10,
            "attack": 20,
            "defense": 30,
            "sp_atk": 40,
            "sp_def": 50,
            "speed": 30,
            "generation": 1,
            "legendary": False,
        }
        response = client.post("/pokemon", json=pokemon_data)
        assert response.status_code == 201
        assert response.json()["name"] == "Test Pokémon"

    def test_update_pokemon(self):
        updated_data = {
            "id": 4019,
            "name": "Updated Pokémon",
            "type_1": "Water",
            "type_2": None,
            "total": 150,
            "hp": 20,
            "attack": 30,
            "defense": 40,
            "sp_atk": 50,
            "sp_def": 60,
            "speed": 70,
            "generation": 2,
            "legendary": True,
        }

        # Send a PUT request to the endpoint
        response = client.put(f'/pokemon/{updated_data["id"]}', json=updated_data)

        # Assert the response status code is 202
        # assert response.status_code == 202

        # Assert the response data matches the updated data
        assert response.json() == updated_data

    def test_update_non_existing_pokemon(self):
        updated_data = {
            "id": 40190,
            "name": "Updated Pokémon",
            "type_1": "Water",
            "type_2": None,
            "total": 150,
            "hp": 20,
            "attack": 30,
            "defense": 40,
            "sp_atk": 50,
            "sp_def": 60,
            "speed": 70,
            "generation": 2,
            "legendary": True,
        }

        # Send a PUT request to the endpoint
        response = client.put(f'/pokemon/{updated_data["id"]}', json=updated_data)

        assert response.status_code == 404
        assert response.json()["detail"] == f"Pokemon with this id is not exist.."

        # Assert the response data matches the updated data
        # assert response.json() == updated_data

    def test_update_pokemon_patch(self):
        # Partial update data
        pokemon_id = 900
        updated_data = {
            "id": pokemon_id,
            "name": "Test",
            "type_1": "Water",
            "type_2": "Poison",
            "total": 310,
            "hp": 30,
            "attack": 35,
            "defense": 30,
            "sp_atk": 100,
            "sp_def": 35,
            "speed": 80,
            "generation": 1,
            "legendary": False,
        }

        # Send a PATCH request to the endpoint
        response = client.patch(f"/pokemon/{pokemon_id}", json=updated_data)

        # assert response.status_code == 200
        # assert response.json()["detail"] == f"pokemon with id {pokemon_id} updated..."

        # Assert the response data matches the updated data
        assert response.json() == updated_data

    def test_update_nonexistent_pokemon_patch(self):
        # Partial update data
        pokemon_id = 4020
        updated_data = {
            "id": pokemon_id,
            "name": "Test",
            "type_1": "Water",
            "type_2": "Poison",
            "total": 310,
            "hp": 30,
            "attack": 35,
            "defense": 30,
            "sp_atk": 100,
            "sp_def": 35,
            "speed": 80,
            "generation": 1,
            "legendary": False,
        }

        # Send a PATCH request to the endpoint
        response = client.patch(f"/pokemon/{pokemon_id}", json=updated_data)

        # Assert the response status code is 404
        assert response.status_code == 404
        assert response.json()["detail"] == f"pokemon with id {pokemon_id} doesn't exist..."

    def test_delete_pokemon(self):
        pokemon_id = 1601
        # Send a DELETE request to the endpoint
        response = client.delete(f"/pokemon/{pokemon_id}")

        # Assert the response status code is 200
        assert response.status_code == 200
        assert response.json()["detail"] == "Pokemon with this id is deleted successfully.."

    def test_delete_non_existing_pokemon(self):
        pokemon_id = 901
        # Send a DELETE request to the endpoint
        response = client.delete(f"/pokemon/{pokemon_id}")

        # Assert the response status code is 404
        assert response.status_code == 404
        assert (
                response.json()["detail"]
                == "Pokemon with this id is either alreday deleted or not found.."
        )

    def test_delete_pokemon_invalid_id(self):
        pokemon_id = "abc"
        response = client.delete(f"/pokemon/{pokemon_id}")

        assert response.status_code == 400
        assert response.json()["detail"] == "Pokemon ID must be a valid integer."
