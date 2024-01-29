from fastapi.testclient import TestClient
from api import app
from models import Base, engine
import base64
from tests import client, admin_auth_encoded, user_auth_encoded
import pytest


def test_prepare_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_user_for_articles_test():
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


def test_user_for_articles():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.status_code == 200
    assert type(response.json()) is dict


def test_get_articles():
    response = client.get("/articles")
    assert response.status_code == 200
    assert type(response.json()) is list


def test_create_article():
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


def test_get_article():
    response = client.get("/articles/1")
    assert response.status_code == 200
    assert type(response.json()) is dict


def test_edit_article():
    data = {"title": "test",
            "date": 123456789,
            "content": "edited",
            "author_id": 1}
    response = client.put(
        "/articles/1",
        json=data,
        headers={"Authorization": f"Basic {user_auth_encoded}"}
    )
    assert response.status_code == 200
    assert type(response.json()) is dict
    get_response = client.get("/articles/1")
    assert get_response.status_code == 200
    print(get_response.json())
    assert get_response.json()["content"] == data["content"]


def test_delete_article():
    response = client.delete("/articles/1", headers={"Authorization": f"Basic {user_auth_encoded}"})
    assert response.status_code == 200
    assert type(response.json()) is dict
    assert "error" not in response.json()
    get_response = client.get("/articles/1")
    assert type(get_response.json()) is dict
    assert get_response.json()['code'] == 404


def test_drop_db():
    Base.metadata.drop_all(bind=engine)