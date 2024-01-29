from api.__auth__ import auth, auth_with_right
from fastapi import APIRouter
from models import User, Article, Rating, db_session
from typing import Annotated, Optional, Union
from fastapi import Depends, Query
from sqlalchemy.sql import functions
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import event, select, text
from fastapi import Request
from pydantic import BaseModel
from sqlalchemy import desc
from hashlib import sha256
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter

app = APIRouter()
security = HTTPBasic()


class ArticleData(BaseModel):
    title: str
    date: int
    content: str
    author_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "test",
                    "date": 123,
                    "content": "test",
                    "author_id": 1
                }
            ]
        }
    }


class ArticleFilters(Filter):
    title: Optional[str] = None
    date: Optional[int] = None
    content: Optional[str] = None
    author_id: Optional[int] = None
    rating: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "test",
                    "date": 123,
                    "content": "test",
                    "author_id": 1,
                    "rating": 1,
                    "order_by": "rating"
                }
            ]
        }
    }

    class Constants(Filter.Constants):
        model = Article
        search_model_fields = ["content", "title"]


@app.get("/articles")
async def get_articles(limit: Optional[int] = 10, order_by: Annotated[Optional[Union[str, list[str]]], Query()] = None, filters: ArticleFilters = FilterDepends(ArticleFilters)):
    query = select(Article, functions.sum(Rating.rating).label("rating")) \
        .join(Rating, Article.id == Rating.article_id, isouter=True) \
        .group_by(Article.id)
    query = filters.filter(query)

    if order_by is not None:
        order_by = list(order_by)
        for column in order_by:
            if column != "rating" and column != "-rating":
                column = text("articles." + column) if column[0] != "-" else desc(text("articles." + column[1:]))
            else:
                column = "rating" if column[0] != "-" else desc("rating")
            print(column)
            query = query.order_by(column)

    query = query.limit(limit)
    articles = db_session.execute(query)
    articles = articles.all()
    articles_list = []

    for article, rating in articles:
        articles_list.append(article.json())
        articles_list[-1].update({"rating": rating})

    return articles_list


@app.get("/articles/{article_id}")
async def get_article(article_id: int):
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        return {"error": "No such article", "code": 404}
    article_json = article.json()
    article_json.update({"rating": article.rating()})
    return article_json


@app.post("/articles")
@auth
async def create_article(ad: ArticleData, auth_id: Annotated[HTTPBasicCredentials, Depends(security)]):
    article = Article(title=ad.title, date=ad.date, content=ad.content, author_id=ad.author_id)
    db_session.add(article)
    db_session.commit()
    return article.json()


@app.put("/articles/{article_id}")
@auth_with_right
async def edit_article(article_id: int, ad: ArticleData, auth_id: Annotated[HTTPBasicCredentials, Depends(security)]):
    auth_user = User.query.filter_by(id=auth_id).first()
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        return {"error": "No such article", "code": 404}
    if auth_user.id != article.author_id:
        return {"error": "No rights to edit article", "code": 401}
    article.title = ad.title
    article.date = ad.date
    article.content = ad.content
    article.author_id = ad.author_id
    db_session.commit()
    return article.json()


@app.delete("/articles/{article_id}")
@auth_with_right
async def delete_article(article_id: int, auth_id: Annotated[HTTPBasicCredentials, Depends(security)]):
    auth_user = User.query.filter_by(id=auth_id).first()
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        return {"error": "No such article", "code": 404}
    if auth_user.id != article.author_id:
        return {"error": "No rights to delete article", "code": 401}
    db_session.delete(article)
    db_session.commit()
    return {"status": "ok"}
