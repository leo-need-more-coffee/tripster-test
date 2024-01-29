from api.__auth__ import auth, auth_with_right
from fastapi import APIRouter
from typing import Annotated, Optional
from fastapi import Depends
from models import User, Article, Rating, db_session
from fastapi import Request
from hashlib import sha256
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = APIRouter()
security = HTTPBasic()


class UserData(BaseModel):
    username: str
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "test",
                    "email": "test@test.com",
                    "password": "test"
                }
            ]
        }
    }


@app.get("/users")
async def get_users():
    return User.all_json()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return {"error": "No such user", "code": 404}
    return user.json()


@app.post("/users")
async def create_user(ud: UserData):
    user = User.query.filter_by(username=ud.username).first()
    if user is not None:
        return {"error": "User already exists", "code": 400}
    user = User(username=ud.username, email=ud.email, password_hash=sha256(ud.password.encode()).hexdigest())
    db_session.add(user)
    db_session.commit()
    return user.json()


@app.put("/users/{user_id}")
@auth_with_right
async def edit_user(user_id: int, ud: UserData, auth_id: Annotated[HTTPBasicCredentials, Depends(security)]):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return {"error": "No such user", "code": 404}
    if ud.username is not None:
        user.username = ud.username
    if ud.email is not None:
        user.email = ud.email
    if ud.password is not None:
        user.password_hash = sha256(ud.password.encode()).hexdigest()
    db_session.commit()
    return user.json()


@app.delete("/users/{user_id}")
@auth_with_right
async def delete_user(user_id: int, auth_id: Annotated[HTTPBasicCredentials, Depends(security)]):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return {"error": "No such user", "code": 404}
    db_session.delete(user)
    db_session.commit()
    return {"status": "ok"}

