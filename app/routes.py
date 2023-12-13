import logging
import os

from flasgger import Swagger, swag_from
from flask import Flask, redirect, request, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

db = SQLAlchemy()

root_dir = os.path.dirname(os.path.abspath(__file__))

logfile = os.path.join(root_dir, "../logs", "logfile.log")
logging.basicConfig(
    level=logging.DEBUG,
    filename=logfile,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger()


def create_app():
    template_folder = os.path.join(root_dir, "../static")

    UPLOAD_FOLDER = os.path.join(root_dir, "../static")
    ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

    app = Flask(__name__)
    app.static_folder = template_folder
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql+psycopg2://administrator:administrator@localhost"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    db.init_app(app)

    Swagger(app)

    from .models import Media, Tweet, User, followers, likes

    @app.before_request
    def before_request_func():
        # db.drop_all()
        db.create_all()

        query = db.session.query(User).all()
        user_objects = [
            {"id": 1, "name": "Kate", "api_key": "test"},
            {"id": 2, "name": "Tom", "api_key": "test1"},
        ]
        if len(query) == 0:
            db.session.bulk_insert_mappings(User, user_objects)
        else:
            db.session.bulk_update_mappings(User, user_objects)
        db.session.commit()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/")
    def start_page():
        return redirect("http://127.0.0.1:5000/index.html")

    @app.route("/<path:path>")
    def send_static(path):
        return send_from_directory(app.static_folder, path)

    def get_user_id(api_key: str) -> int:
        user_id = (
            db.session.query(User.id)
            .filter(User.api_key == api_key)
            .one_or_none()
        )
        return user_id[0]

    @app.route("/api/tweets", methods=["POST"])
    @swag_from("../spec/post_api_tweets.yml")
    def post_tweet():
        """
        This route posts a tweet
        """
        API_KEY = request.headers["Api-Key"]
        user_id = get_user_id(API_KEY)

        tweet = request.get_json()
        tweet_content = tweet["tweet_data"]
        tweet_media_ids = tweet["tweet_media_ids"]

        if len(tweet_media_ids) != 0:
            tweet_media_ids = tweet_media_ids[0]
        else:
            tweet_media_ids = None

        insert_query = db.insert(Tweet).values(
            user_id=user_id, content=tweet_content, media_id=tweet_media_ids
        )

        result = db.session.execute(insert_query)
        db.session.commit()
        tweet_id = result.inserted_primary_key
        tweet_id = int(tweet_id[0])

        logger.debug("Tweet (ID: %s) was posted.", tweet_id)
        data = {"result": "true", "tweet_id": tweet_id}
        return data, 201

    def allowed_file(filename: str) -> bool:
        return "." in filename and \
               filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

    @app.route("/api/medias", methods=["POST"])
    @swag_from("../spec/post_api_medias.yml")
    def post_media():
        """
        This route posts media
        """
        file = request.files["file"]

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            insert_query = db.insert(Media).values(filename=filename)
            result = db.session.execute(insert_query)
            db.session.commit()

            media_id = result.inserted_primary_key
            media_id = int(media_id[0])

            logger.debug("Media (ID: %s) was posted.", media_id)
            data = {"result": "true", "media_id": media_id}

            return data, 201

    @app.route("/api/tweets/<int:id>", methods=["DELETE"])
    @swag_from("../spec/delete_api_tweets_id.yml")
    def delete_tweet(id: int):
        """
        This route deletes a tweet
        """
        API_KEY = request.headers["Api-Key"]
        user_id = get_user_id(API_KEY)

        delete_query = db.delete(Tweet)\
            .filter(Tweet.user_id == user_id)\
            .returning(Tweet.media_id)\
            .where(Tweet.id == id)
        deleted_row = db.session.execute(delete_query).all()
        db.session.commit()
        if deleted_row:
            if deleted_row[0][0] is not None:
                media_id = deleted_row[0][0]
                filename = (
                    db.session.query(Media.filename)
                    .filter(Media.id == media_id).all()
                )
                filename_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], str(filename[0][0])
                )
                if os.path.isdir(filename_path):
                    os.remove(filename_path)

                delete_media_query = db.delete(Media)\
                    .where(Media.id == media_id)
                db.session.execute(delete_media_query)

        logger.debug("Tweet (ID: %s) was deleted.", id)
        data = {"result": "true"}

        return data, 200

    @app.route("/api/tweets/<int:id>/likes", methods=["POST"])
    @swag_from("../spec/post_api_like_tweet_id.yml")
    def like_tweet(id: int):
        """
        This route likes a tweet
        """
        API_KEY = request.headers["Api-Key"]
        user_id = get_user_id(API_KEY)

        like_query = (
            db.session.query(likes)
            .filter(likes.c.user_id == user_id, likes.c.tweet_id == id)
            .all()
        )

        if len(like_query) == 0:
            insert_query = likes.insert().values(user_id=user_id, tweet_id=id)
            db.session.execute(insert_query)
            db.session.commit()

        logger.debug("Tweet (ID: %s) was liked by User (ID: %s).", id, user_id)
        data = {"result": "true"}

        return data, 201

    @app.route("/api/tweets/<int:id>/likes", methods=["DELETE"])
    @swag_from("../spec/delete_api_tweets_id_likes.yml")
    def remove_like(id: int):
        """
        This route removes a like
        """
        API_KEY = request.headers["Api-Key"]
        user_id = get_user_id(API_KEY)

        like_query = (
            db.session.query(likes)
            .filter(likes.c.user_id == user_id, likes.c.tweet_id == id)
            .all()
        )

        if len(like_query) != 0:
            delete_query = likes.delete().where(
                likes.c.tweet_id == id, likes.c.user_id == user_id
            )
            db.session.execute(delete_query)
            db.session.commit()

        logger.debug(
            "The like of the Tweet (ID: %s) was removed by User %s.",
            id,
            user_id
        )
        data = {"result": "true"}

        return data, 200

    @app.route("/api/users/<int:id>/follow", methods=["POST"])
    @swag_from("../spec/post_api_users_id_follow.yml")
    def follow_user(id):
        """
        This route allows a user to follow another user
        """
        API_KEY = request.headers["Api-Key"]
        user_id = get_user_id(API_KEY)

        followed_query = (
            db.session.query(followers)
            .filter(followers.c.follower_id == user_id,
                    followers.c.followed_id == id)
            .all()
        )

        if len(followed_query) == 0 and user_id != id:
            insert_query = followers.insert().values(
                follower_id=user_id, followed_id=id
            )
            db.session.execute(insert_query)
            db.session.commit()

        logger.debug(
            "User (ID: %s) has followed the User (ID: %s).",
            user_id, id
        )
        data = {"result": "true"}

        return data, 201

    @app.route("/api/users/<int:id>/follow", methods=["DELETE"])
    @swag_from("../spec/delete_api_unfollow_user_id.yml")
    def unfollow_user(id):
        """
        This route allows the user to unfollow another user
        """
        API_KEY = request.headers["Api-Key"]
        user_id = get_user_id(API_KEY)

        followed_query = (
            db.session.query(followers)
            .filter(followers.c.follower_id == user_id,
                    followers.c.followed_id == id)
            .all()
        )

        if len(followed_query) != 0:
            delete_follower_query = followers.delete().where(
                followers.c.follower_id == user_id,
                followers.c.followed_id == user_id
            )

            db.session.execute(delete_follower_query)
            db.session.commit()

        logger.debug(
            "User (ID: %s) has unfollowed the User (ID: %s).",
            user_id, id
        )
        data = {"result": "true"}

        return data, 200

    @app.route("/api/tweets", methods=["GET"])
    @swag_from("../spec/get_api_tweets.yml")
    def get_all_tweets():
        """
        This route receives all tweets
        """
        query = db.session.query(Tweet).all()

        tweet_list = []
        try:
            for q in query:
                tweet_obj = q.to_json()

                user_id, tweet_id = int(q.user_id), int(q.id)
                user_query = db.session.query(User)\
                    .filter(User.id == user_id)\
                    .all()
                like_query = (
                    db.session.query(likes.c.user_id)
                    .filter(likes.c.tweet_id == tweet_id)
                    .all()
                )

                media_query = (
                    db.session.query(Media.filename)
                    .filter(Media.id == q.media_id)
                    .all()
                )
                user_obj = (
                    db.session.query(User)
                    .filter(User.id.in_(
                        like_obj[0] for like_obj in like_query
                        )
                    )
                    .all()
                )

                tweet_obj["author"] = user_query[0].to_json()
                tweet_obj["likes"] = [like.to_json() for like in user_obj]

                if len(media_query) == 0:
                    tweet_obj["attachments"] = None
                else:
                    filename = str(media_query)[3:-4]
                    tweet_obj["attachments"] = [filename]
                tweet_list.append(tweet_obj)

            tweet_list = [tweet for tweet in reversed(tweet_list)]

            logger.debug("All the tweets are being displayed.")
            data = {"result": "true", "tweets": tweet_list}, 200

        except Exception as exc:
            logger.error("The exception %s has occurred", type(exc))
            data = {
                "result": "false",
                "error_type": f"{type(exc).__name__}",
                "error_message": f"{str(exc)}",
            }, 400

        return data

    def get_follower_object(user):
        follower_query = (
            db.session.query(followers.c.follower_id)
            .filter(followers.c.followed_id == user["id"])
            .all()
        )
        follower_obj = (
            db.session.query(User)
            .filter(User.id.in_(follower[0] for follower in follower_query))
            .all()
        )
        user["followers"] = [obj.to_json() for obj in follower_obj]
        return user

    def get_followed_object(user):
        followed_query = db.session.query(followers.c.followed_id).filter(
            followers.c.follower_id == user["id"]
        )
        followed_obj = (
            db.session.query(User)
            .filter(User.id.in_(follower[0] for follower in followed_query))
            .all()
        )
        user["following"] = [obj.to_json() for obj in followed_obj]
        return user

    @app.route("/api/users/me", methods=["GET"])
    @swag_from("../spec/get_api_users_me.yml")
    def get_profile_information():
        """
        This route receives the user's profile information
        """
        API_KEY = request.headers["Api-Key"]
        try:
            user = db.session.query(User)\
                .filter(User.api_key == API_KEY)\
                .one_or_none()

            user_object = user.to_json()

            get_follower_object(user_object)
            get_followed_object(user_object)

            logger.debug("The User (ID: %s) profile is being displayed.", user.id)
            data = {"result": "true", "user": user_object}

            return data, 200

        except (AttributeError, TypeError):
            logger.error("An unauthorized user is trying to log in")
            return "Unauthorized user"

    @app.route("/api/users/<int:id>", methods=["GET"])
    @swag_from("../spec/get_api_users_id.yml")
    def get_profile_of_any_user_by_id(id: int):
        """
        This route receives any user's profile information by their id
        """
        user = db.session.query(User).filter(User.id == id).one_or_none()
        if user:
            user_object = user.to_json()
            get_follower_object(user_object)
            get_followed_object(user_object)

            logger.debug(
                "The User (ID: %s) profile is being displayed.",
                id,
            )
            data = {"result": "true", "user": user_object}

            return data, 200

    return app
