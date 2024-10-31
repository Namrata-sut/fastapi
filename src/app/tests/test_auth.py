import os
from faker import Faker

from app.factories.user_factory import UserFactory
from app.models.models import UserRole
from app.tests.conftest import get_auth_token

faker = Faker()
os.environ["SECRET_KEY"] = "ahgpreghe948yp8934yhp9dhye4fw309039ug8rg"


def test_create_user(client, create_user, user_data):
    # Use the create_user fixture from conftest.py
    username, password, role = user_data
    create_user_request = {
        "username": username,
        "password": password,
        "role": role,
    }

    response = client.post("/auth/user", json=create_user_request)
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["username"] == username
    assert response_data["role"] == role


def test_user_login(client, get_auth_token, user_data):
    plain_password = "test_"
    username, password, role = user_data
    # create_user_request = {
    #     "username": username,
    #     "password": password,
    #     "role": role,
    # }
    # user_data = create_user(username=faker.unique.user_name(), plain_password=plain_password, role=UserRole.user)
    # print(f"User created: {user_data.username}, Plain password: {plain_password}, Hashed password: {user_data.hashed_password}")
    auth_token = get_auth_token(username, plain_password, role)

    print(auth_token)
    response = client.post("/auth/token", data={
        "username": username,
        "password": plain_password
    })

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.json()}")

    assert response.status_code == 200
    token_data = response.json()
    assert token_data["access_token"] is not None
    assert token_data["role"] == user_data.role



