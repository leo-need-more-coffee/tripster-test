from hashlib import sha256
from sqlalchemy import Integer, String, Column, create_engine, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine("sqlite:///database.db")
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def password_hash(password: str) -> str:
    return sha256(password.encode()).hexdigest()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String)
    password_hash = Column(String)

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def all_json():
        return [el.json() for el in User.query.all()]


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer)
    user_id = Column(Integer)
    rating = Column(Integer)

    def json(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "user_id": self.user_id,
            "rating": self.rating,
        }

    def __repr__(self):
        return f"<Rating {self.id}>"

    @staticmethod
    def all_json():
        return [el.json() for el in Rating.query.all()]


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(Integer)
    content = Column(String)
    author_id = Column(Integer)
    '''
    Я оставил rating методом в бд, чтобы аснихронные запросы не конфликтовали.
    '''

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "content": self.content,
            "author_id": self.author_id,
        }

    def __repr__(self):
        return f"<Article {self.title}>"

    @staticmethod
    def all_json():
        return [el.json() for el in Article.query.all()]
