import factory
from app.models import (
        Tweet,
        Media,
        User
    )
from app.routes import db


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
    name = factory.Faker('first_name')
    api_key = factory.Faker('last_name')
    # followed = factory.SubFactory(FollowedFactory)


class MediaFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Media
        sqlalchemy_session = db.session

    filename = factory.Faker('user_name')


class TweetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Tweet
        sqlalchemy_session = db.session

    content = factory.Faker('sentence')
    media = factory.SubFactory(MediaFactory)
