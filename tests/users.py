from fastapi.testclient import TestClient
from api import app
from models import Base, engine
import base64
from tests import client, user_auth_encoded
import pytest


def test_prepare_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert type(response.json()) is list


def test_create_user():
    data = {"username": "test",
                "email": "test@test.com",
                "password": "test"}
    response = client.post(
        "/users",
        json=data,
        headers={"Authorization": f"Basic {user_auth_encoded}"}
    )
    assert response.status_code == 200
    assert type(response.json()) is dict
    assert response.json()["username"] == data["username"]
    assert response.json()["email"] == data["email"]


def test_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert type(response.json()) is dict


def test_edit_user():
    data = {"username": "test",
            "email": "edited@test.com",
            "password": "test"}
    response = client.put(
        "/users/1",
        json=data,
        headers={"Authorization": f"Basic {user_auth_encoded}"}
    )
    assert response.status_code == 200
    assert type(response.json()) is dict
    get_response = client.get("/users/1")
    assert get_response.status_code == 200
    assert get_response.json()["email"] == data["email"]


def test_delete_user():
    response = client.delete("/users/1", headers={"Authorization": f"Basic {user_auth_encoded}"})
    assert response.status_code == 200
    assert type(response.json()) is dict
    get_response = client.get("/users/1")
    assert type(get_response.json()) is dict
    assert get_response.json()['code'] == 404