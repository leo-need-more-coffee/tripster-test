from fastapi.testclient import TestClient
from api import app
from models import Base, engine
import base64
from tests import client, admin_auth_encoded, user_auth_encoded
import pytest


def test_prepare_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_user_for_rating():
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


def test_create_article_for_rating():
    data = {"title": "test",
            "date": 123456789,
            "content": "test",
            "author_id": 1}
    response = client.post(
        "/articles",
        json=data,
        headers={"Authorization": f"Basic {user_auth_encoded}"}
    )
    print(response.json())
    assert response.status_code == 200
    assert type(response.json()) is dict
    assert response.json()["title"] == data["title"]
    assert response.json()["content"] == data["content"]
    assert response.json()["author_id"] == data["author_id"]
    assert response.json()["date"] == data["date"]


def test_get_ratings():
    response = client.get("/articles/1/ratings")
    assert response.status_code == 200
    assert type(response.json()) is list


def test_create_rating():
    data = {"article_id": 1,
            "user_id": 1,
            "rating": True}
    response = client.post(
        "/articles/1/ratings",
        json=data,
        headers={"Authorization": f"Basic {user_auth_encoded}"}
    )
    assert response.status_code == 200
    assert type(response.json()) is dict
    assert response.json()["article_id"] == data["article_id"]
    assert response.json()["user_id"] == data["user_id"]
    assert response.json()["rating"] == data["rating"]


def test_get_rating():
    response = client.get("/ratings/1")
    assert response.status_code == 200
    assert type(response.json()) is dict


def test_edit_rating():
    data = {"article_id": 0,
            "user_id": 0,
            "rating": False}
    response = client.put(
        "/articles/1/ratings",
        json=data,
        headers={"Authorization": f"Basic {user_auth_encoded}"}
    )
    assert response.status_code == 200
    assert type(response.json()) is dict
    get_response = client.get("/ratings/1/1")
    print()
    assert get_response.status_code == 200
    assert get_response.json()["rating"] == data["rating"]


def test_delete_rating():
    response = client.delete("/articles/1/ratings", headers={"Authorization": f"Basic {user_auth_encoded}"})
    assert response.status_code == 200
    assert type(response.json()) is dict
    assert "error" not in response.json()
    get_response = client.get("/ratings/1/1")
    assert type(get_response.json()) is dict
    assert get_response.json()['code'] == 404


def test_drop_db():
    Base.metadata.drop_all(bind=engine)