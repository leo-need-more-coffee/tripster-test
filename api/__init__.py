from fastapi import FastAPI, Request
from api.user import app as user_router
from api.article import app as article_router
from api.rating import app as rating_router
from models import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_router)
app.include_router(article_router)
app.include_router(rating_router)