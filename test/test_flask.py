import io

import pytest


def test_media(client) -> None:
    response = client.post("/api/medias", data=dict(file=(io.BytesIO(b"image"), 'test.jpg')))

    assert response.status_code == 201
    assert response.json == {
        "result": "true",
        "media_id": 1
    }


def test_create_tweet(client) -> None:
    resp = client.post("/api/tweets",
                       json={"tweet_data": "text", "tweet_media_ids": [2]},
                       headers={'Api-Key': 'test'})
    assert resp.status_code == 201
    assert resp.json == {"result": "true", "tweet_id": 2}


def test_tweet(client) -> None:
    response = client.get("/api/tweets")
    assert response.status_code == 200
    assert response.json == {
        "result": "true",
        "tweets": [
            {
                "id": 1,
                "content": "text",
                "attachments": ["filename"],
                "author": {
                    "id": 1,
                    "name": "Kate"
                },
                "likes": []
            }
        ]
    }


def test_can_delete_tweet(client) -> None:
    response = client.delete("/api/tweets/1", headers={'Api-Key': 'test'})
    assert response.status_code == 200
    assert response.json == {
        "result": "true"
    }


def test_like(client) -> None:
    response = client.post("/api/tweets/1/likes", headers={'Api-Key': 'test'})
    assert response.status_code == 201
    assert response.json == {
        "result": "true"
    }


def test_can_delete_like(client) -> None:
    resp = client.delete("/api/tweets/1/likes", headers={'Api-Key': 'test'})
    assert resp.status_code == 200
    assert resp.json == {
        "result": "true"
    }


def test_follow(client) -> None:
    resp = client.post("/api/users/1/follow", headers={'Api-Key': 'test'})
    assert resp.status_code == 201
    assert resp.json == {
        "result": "true"
    }


def test_can_unfollow(client) -> None:
    resp = client.delete("/api/users/1/follow", headers={'Api-Key': 'test'})
    assert resp.status_code == 200
    assert resp.json == {
        "result": "true"
    }


def test_user_me(client) -> None:
    resp = client.get("/api/users/me", headers={'Api-Key': 'test'})
    assert resp.status_code == 200
    assert resp.json == {
        "result": "true",
        "user": {
            "followers": [],
            "following": [],
            "id": 1,
            "name": "Kate"
        }
    }


def test_can_get_user_by_id(client) -> None:
    resp = client.get("/api/users/2", headers={'Api-Key': 'test2'})
    assert resp.status_code == 200
    assert resp.json == {
        "result": "true",
        "user": {
            "followers": [],
            "following": [],
            "id": 2,
            "name": "Tom"
        }
    }


def test_app_config(app):
    assert not app.config['DEBUG']
    assert app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == "postgresql+psycopg2://"


def test_static(client):
    page = client.get("/index.html")
    assert page.status_code == 200


@pytest.mark.parametrize("route", ["/api/tweets", "/api/users/me", "/api/users/2"])
def test_route_status(client, route):
    rv = client.get(route, headers={'Api-Key': 'test'})
    assert rv.status_code == 200


@pytest.mark.parametrize("route", ["/api/tweets/1", "/api/tweets/1/likes", "/api/users/2/follow"])
def test_route_status(client, route):
    rv = client.delete(route, headers={'Api-Key': 'test'})
    assert rv.status_code == 200
