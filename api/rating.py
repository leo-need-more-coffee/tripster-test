from api.__auth__ import auth, auth_with_right
from fastapi import APIRouter
from models import User, Article, Rating, db_session
from typing import Annotated, Optional
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Request
from pydantic import BaseModel
from hashlib import sha256

app = APIRouter()
security = HTTPBasic()


class RatingData(BaseModel):
    article_id: int
    user_id: Optional[int]
    rating: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "article_id": 1,
                    "user_id": 1,
                    "rating": True
                }
            ]
        }
    }


@app.get("/articles/{article_id}/ratings")
async def get_ratings(article_id: int):
    ratings = Rating.query.filter_by(article_id=article_id).all()
    return [el.json() for el in ratings]


@app.get("/ratings/{rating_id}")
async def get_rating(rating_id: int):
    rating = Rating.query.filter_by(id=rating_id).first()
    if rating is None:
        return {"error": "No such rating", "code": 404}
    return rating.json()


@app.get("/ratings/{article_id}/{user_id}")
async def get_user_rating(article_id: int, user_id: int):
    article = Article.query.filter_by(id=article_id).first()
    user = User.query.filter_by(id=user_id).first()

    if article is None:
        return {"error": "No such article", "code": 404}
    if user is None:
        return {"error": "No such user", "code": 404}

    rating = Rating.query.filter_by(article_id=article_id, user_id=user_id).first()
    if rating is None:
        return {"error": "No rating", "code": 404}

    print(rating.json())
    return rating.json()


@app.post("/articles/{article_id}/ratings")
@auth
async def create_rating(article_id: int, rd: RatingData, auth_id: Annotated[HTTPBasicCredentials, Depends(security)]):
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        return {"error": "No such article", "code": 404}
    if len(Rating.query.filter_by(article_id=article_id, user_id=auth_id).all()) != 0:
        return {"error": "Rating already exists", "code": 400}
    rating = Rating(article_id=rd.article_id, user_id=auth_id, rating=rd.rating)
    db_session.add(rating)
    db_session.commit()
    return rating.json()


@app.put("/articles/{article_id}/ratings")
@auth_with_right
async def edit_rating(article_id: int, rd: RatingData, auth_id: Annotated[HTTPBasicCredentials, Depends(security)]):
    auth_user = User.query.filter_by(id=auth_id).first()
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        return {"error": "No such article", "code": 404}
    rating = Rating.query.filter_by(article_id=article_id, user_id=auth_user.id).first()
    if rating is None:
        return {"error": "No such rating", "code": 404}
    rating.rating = rd.rating
    db_session.commit()
    return rating.json()


@app.delete("/articles/{article_id}/ratings")
@auth_with_right
async def delete_rating(article_id: int, auth_id: Annotated[HTTPBasicCredentials, Depends(security)]):
    auth_user = User.query.filter_by(id=auth_id).first()
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        return {"error": "No such article", "code": 404}
    rating = Rating.query.filter_by(article_id=article_id, user_id=auth_user.id).first()
    if rating is None:
        return {"error": "No such rating", "code": 404}
    db_session.delete(rating)
    db_session.commit()
    return rating.json()
