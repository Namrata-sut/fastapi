import pytest
from starlette.testclient import TestClient

from app.tests.conftest import test_db


class TestAuthRoutes:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient, test_db, admin_data):
        self.client = client
        self.db = test_db
        self.admin_data = admin_data
        # self.token = get_auth_token
        # print(self.token)

    def test_create_user(self):
        # Test creating a new user
        response = self.client.post("/auth/user", json=self.admin_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == self.admin_data["username"]
        assert data["role"] == self.admin_data["role"]
        assert "id" in data

    def test_login_user(self, create_user):
        # Test user login after creation
        login_data = {
            "username": self.admin_data["username"],
            "password": self.admin_data["password"]
        }
        response = self.client.post("/auth/token", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == self.admin_data["role"]

    def test_login_invalid_user(self):
        # Test invalid user login
        invalid_login_data = {
            "username": "invaliduser",
            "password": "invalidpassword"
        }
        response = self.client.post("/auth/token", data=invalid_login_data)
        assert response.status_code == 401
        assert response.json() == {"detail": "Could not validate users"}

    def test_get_auth_token(self, client, get_auth_token):
        # Ensure token is not None
        assert get_auth_token is not None, "Access token should not be None"
