from typing import Any, Dict

from .routes import db

likes = db.Table(
    "likes",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column(
        "tweet_id",
        db.Integer,
        db.ForeignKey("tweet.id", ondelete="CASCADE")),
)


class Tweet(db.Model):
    __tablename__ = "tweet"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), default=None)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    media = db.relationship("Media", backref=db.backref("tweet"))
    like = db.relationship(
        "Tweet",
        secondary=likes,
        primaryjoin=(likes.c.tweet_id == id),
        backref=db.backref("likes", passive_deletes=True),
    )

    def to_json(self) -> dict:
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["media_id", "user_id"]
        }

    def __repr__(self):
        return f"Tweet {self.content}"


followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, )
    name = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String, nullable=False)
    followed = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    def to_json(self) -> Dict[str, Any]:
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["api_key"]
        }


class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"{self.filename}"
