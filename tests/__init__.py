from fastapi.testclient import TestClient
from api import app
from models import Base, engine
import base64
import pytest

client = TestClient(app)
admin_auth_encoded = base64.b64encode(b"admin:admin").decode("ascii")
user_auth_encoded = base64.b64encode(b"test:test").decode("ascii")
