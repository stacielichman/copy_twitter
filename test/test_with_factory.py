from .factories import UserFactory, MediaFactory, TweetFactory
from app.models import User, Tweet, Media, followers, likes


def test_create_user(app, db):
    user = UserFactory(id=3)
    db.session.commit()
    assert user.id is not None
    assert len(db.session.query(User). all()) == 3


def test_create_media(app, db):
    media = MediaFactory()
    db.session.commit()
    assert media.id is not None
    assert len(db.session.query(Media).all()) == 2


def test_create_tweet(app, db):
    tweet = TweetFactory()
    db.session.commit()
    assert tweet.id is not None
    assert tweet.media.id is not None
    assert len(db.session.query(Tweet).all()) == 2


def test_create_follower(app, db):
    UserFactory(id=3)
    UserFactory(id=4)
    db.session.commit()

    follower = followers.insert().values(follower_id=1, followed_id=2)
    db.session.execute(follower)
    db.session.commit()
    assert len(db.session.query(followers).all()) == 1


def test_create_like(app, db):
    UserFactory(id=3)
    TweetFactory()
    db.session.commit()

    like = likes.insert().values(user_id=3, tweet_id=1)
    db.session.execute(like)
    db.session.commit()
    assert len(db.session.query(likes).all()) == 1
