import os
import tempfile
import pytest
import flask_login
from random import randint
from flask import url_for
from tabletop_story.__init__ import create_app
from tabletop_story.app import init_app, plugins
from tabletop_story.models import User, GameCharacter, GameCampaign
from dnd_character.classes import Fighter


@pytest.fixture
def client():
    global app, db, bcrypt, login_manager, i
    app = create_app()
    db, migrate, bcrypt, login_manager = plugins
    db_fd, db_path = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite+pysqlite:///" + db_path
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True
    app = init_app(app)
    client = app.test_client()
    with app.app_context():
        with client:
            i = 1
            db.create_all()
            add_user()
            add_character(1)
            yield client
    os.close(db_fd)
    os.unlink(db_path)


def login(client, user_id):
    client.post(
        "/account/login",
        data={"email": f"{user_id}@example.com", "password": "password"},
        follow_redirects=True,
    )


def add_user():
    global i
    user = User(
        email=f"{i}@example.com",
        username=f"{i}",
        password="password",
        is_admin=False,
    )
    i += 1
    db.session.add(user)
    db.session.commit()
    assert user.id == i - 1
    return user.id


def add_character(user_id):
    thor = Fighter(name="thor", experience=255, alignment="TN")
    db_thor = GameCharacter(
        user_id=user_id,
        name=thor.name,
        data_keys=str(thor.keys()),
        data_vals=str(thor.values()),
    )
    db.session.add(db_thor)
    db.session.commit()
    return db_thor.id


def add_campaign(user_id, player_id):
    test = GameCampaign(
        name="test", gamemaster=user_id, character1=player_id, active_location=0
    )
    db.session.add(test)
    db.session.commit()
    return test.id


def test_anonymous_can_view_character(client):
    resp = client.get("/character/view/1")
    assert resp.status_code == 200


def test_anonymous_cant_edit_character(client):
    resp = client.get("/character/edit/1")
    assert resp.status_code == 302


def test_user_can_view_character(client):
    login(client, 1)
    resp = client.get("/character/view/1")
    assert resp.status_code == 200


def test_user_can_edit_own_character(client):
    login(client, 1)
    resp = client.get("/character/edit/1")
    assert resp.status_code == 200


def test_user_can_view_foreign_character(client):
    login(client, 1)
    k = add_user()
    add_character(k)
    resp = client.get(f"/character/view/{k}")
    assert resp.status_code == 200


def test_user_cant_edit_foreign_character_without_any_campaigns(client):
    login(client, 1)
    k = add_user()
    add_character(k)
    resp = client.get(f"/character/edit/{k}")
    assert resp.status_code == 403


def test_user_cant_edit_foreign_character_with_campaigns(client):
    login(client, 1)
    k = add_user()
    add_character(k)
    add_campaign(1, 1)
    resp = client.get(f"/character/edit/{k}")
    assert resp.status_code == 403


def test_user_cant_edit_gamemasters_character(client):
    login(client, 1)
    k = add_user()
    add_character(k)
    add_campaign(k, 1)
    resp = client.get(f"/character/edit/{k}")
    assert resp.status_code == 403


def test_gamemaster_can_view_unrelated_character(client):
    login(client, 1)
    add_campaign(1, 1)
    add_user()
    add_character(2)
    resp = client.get(f"/character/view/2")
    assert resp.status_code == 200


def test_gamemaster_cant_edit_unrelated_character(client):
    login(client, 1)
    add_campaign(1, 1)
    add_user()
    add_character(2)
    resp = client.get(f"/character/edit/2")
    assert resp.status_code == 403


def test_gamemaster_can_view_related_character(client):
    login(client, 1)
    add_user()
    add_character(2)
    add_campaign(1, 2)
    resp = client.get(f"/character/view/2")
    assert resp.status_code == 200


def test_gamemaster_can_edit_related_character(client):
    login(client, 1)
    add_user()
    add_character(2)
    add_campaign(1, 2)
    resp = client.get(f"/character/edit/2")
    assert resp.status_code == 200


def test_gamemaster_cant_edit_other_gamemasters_character(client):
    login(client, 1)
    k = add_user()
    add_character(k)
    add_campaign(1, 1)
    add_campaign(k, k)
    resp = client.get(f"/character/edit/{k}")
    assert resp.status_code == 403
