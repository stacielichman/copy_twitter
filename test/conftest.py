import pytest
from app.models import (
    Tweet,
    Media,
    User
)
from app.routes import create_app, db as _db
from flask import template_rendered


@pytest.fixture
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://"

    with _app.app_context():
        _db.drop_all()
        _db.create_all()
        user1 = User(id=1, name="UserOne", api_key="test")
        user2 = User(id=2, name="UserTwo", api_key="test2")
        media = Media(id=2, filename="filename")
        tweet = Tweet(content="text", media_id=2, user_id=1)

        _db.session.add(user1)
        _db.session.add(user2)
        _db.session.add(media)
        _db.session.add(tweet)
        _db.session.commit()

        yield _app
        _db.session.close()
        _db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
