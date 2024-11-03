import pytest
from fastapi.testclient import TestClient
from app.schemas.schema import PokemonPostPutInputSchema, PokemonPatchInputSchema
from app.tests.conftest import override_get_db


class TestPokemonRoutes:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient, get_auth_token):
        self.client = client
        self.db = override_get_db
        self.token = get_auth_token
        print(self.token)

    def test_add_pokemon_success(self, valid_pokemon_data):
        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.post("/pokemon", json=valid_pokemon_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == valid_pokemon_data["name"]
        # assert data["type_1"] == valid_pokemon_data["type_1"]
        # assert data["total"] == valid_pokemon_data["total"]

    def test_add_pokemon_invalid_data(self, invalid_pokemon_data):
        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.post("/pokemon", json=invalid_pokemon_data, headers=headers)

        assert response.status_code == 422
        assert response.json()["detail"] is not None

    def test_get_pokemon_by_id_success(self, create_pokemon):
        headers = {"Authorization": f"Bearer {self.token}"}

        pokemon = create_pokemon(name="Bulbasaur", type_1="Grass", total=318)

        response = self.client.get(f"/pokemon/{pokemon.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == pokemon.name

    def test_get_pokemon_by_id_not_found(self):
        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.get("/pokemon/99999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Pokemon not found."

    def test_update_pokemon(self, create_pokemon):
        initial_pokemon = create_pokemon(name="Pikachu", type_1="Electric", hp=35, attack=55)

        update_data = {
            "name": "Raichu",
            "type_1": "Electric",
            "total": 200,
            "hp": 60,
            "attack": 12,
            "defense": 12,
            "sp_atk": 12,
            "sp_def": 12,
            "speed": 100,
            "generation": 2,
            "legendary": True
        }

        update_payload = PokemonPostPutInputSchema(**update_data).dict()
        response = self.client.put(
            f"/pokemon/{initial_pokemon.id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 202, f"Expected status code 202 but got {response.status_code}"
        updated_pokemon = response.json()
        assert updated_pokemon["name"] == "Raichu"

    def test_patch_pokemon(self, create_pokemon):
        initial_pokemon = create_pokemon(name="Charmander", type_1="Fire", hp=39, attack=52)
        patch_data = {
            "name": "Raichu",
            "type_1": "Electric",
            "total": 200,
            "hp": 60,
            "attack": 12,
            "defense": 12,
            "sp_atk": 12,
            "sp_def": 12,
            "speed": 200,
            "generation": 2,
            "legendary": True
        }
        patch_payload = PokemonPatchInputSchema(**patch_data).dict()

        response = self.client.patch(
            f"/pokemon/{initial_pokemon.id}",
            json=patch_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 200, f"Expected status code 202 but got {response.status_code}"
        patched_pokemon = response.json()
        assert patched_pokemon["hp"] == 60

    def test_delete_pokemon(self, create_pokemon):
        initial_pokemon = create_pokemon(name="Bulbasaur", type_1="Grass", hp=45, attack=49)

        response = self.client.delete(
            f"/pokemon/{initial_pokemon.id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 200, f"Expected status code 204 but got {response.status_code}"

    def test_delete_not_existing_pokemon(self):
        response = self.client.delete(
            f"/pokemon/19999",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 404
