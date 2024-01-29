from functools import wraps
import base64
from hashlib import sha256
from typing import Union
from fastapi import FastAPI, Request
from models import User, Article, Rating, db_session


def check_auth(credentials) -> Union[User, bool, None]:
    username, password = credentials.username, credentials.password
    password_hash = sha256(password.encode()).hexdigest()

    user = User.query.filter_by(username=username).first()

    if user is None:
        return None
    if user.password_hash != password_hash:
        return False

    return user


def auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        credentials = kwargs.get('auth_id')
        if credentials is None:
            return {"error": "No auth credentials", "code": 401}
        auth_user = check_auth(credentials)

        if auth_user is None:
            return {"error": "No such auth user", "code": 401}
        if auth_user is False:
            return {"error": "Wrong auth password", "code": 401}

        kwargs['auth_id'] = auth_user.id
        return await func(*args, **kwargs)
    return wrapper


def auth_with_right(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        credentials = kwargs.get('auth_id')
        if credentials is None:
            return {"error": "No auth credentials", "code": 401}
        auth_user = check_auth(credentials)

        if auth_user is None:
            return {"error": "No such auth user", "code": 401}
        if auth_user is False:
            return {"error": "Wrong auth password", "code": 401}

        user_id = None
        if "user_id" in kwargs:
            user_id = kwargs.get("user_id")
        if "article_id" in kwargs:
            article_id = kwargs.get("article_id")
            article = Article.query.filter_by(id=article_id).first()
            if article is None:
                return {"error": "No such article in auth", "code": 404}
            user_id = article.author_id

        if user_id is None:
            return {"error": "No user id in query", "code": 400}

        if auth_user.id != user_id:
            return {"error": "No rights to edit user", "code": 401}

        kwargs['auth_id'] = auth_user.id
        return await func(*args, **kwargs)
    return wrapper
