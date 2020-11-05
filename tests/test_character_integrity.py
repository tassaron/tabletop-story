"""
Ensure that saving/loading a character doesn't cause any mutation to its data
"""
import pytest
import tempfile
import os
from tabletop_story.__init__ import create_app
from tabletop_story.app import init_app, plugins
from tabletop_story.models import User, GameCharacter
from dnd_character import Character
from dnd_character.classes import CLASSES


@pytest.fixture
def client():
    global app, db, bcrypt, login_manager
    app = create_app()
    db, migrate, bcrypt, login_manager = plugins
    db_fd, db_path = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite+pysqlite:///" + db_path
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True
    client = app.test_client()
    with app.app_context():
        with client:
            app = init_app(app)
            db.create_all()
            db.session.add(
                User(
                    username="test",
                    email="test@example.com",
                    password="password",
                    is_admin=False,
                )
            )
            db.session.commit()
            yield client
    os.close(db_fd)
    os.unlink(db_path)


def test_character_mutation(client):
    thor = Character(name="thor")
    db_thor = GameCharacter(
        user_id=1,
        name=thor.name,
        data_keys=str(thor.keys()),
        data_vals=str(thor.values()),
    )
    db.session.add(db_thor)
    db.session.commit()
    new_thor = GameCharacter.query.first()
    assert new_thor.as_dict() == dict(thor)


def test_character_mutation_with_class(client):
    thor = Character(name="thor", classs=CLASSES["fighter"])
    db_thor = GameCharacter(
        user_id=1,
        name=thor.name,
        data_keys=str(thor.keys()),
        data_vals=str(thor.values()),
    )
    db.session.add(db_thor)
    db.session.commit()
    new_thor = GameCharacter.query.first()
    assert new_thor.as_dict() == dict(new_thor.character) == dict(thor)


def test_character_mutation_with_experience(client):
    thor = Character(name="thor", experience=255)
    db_thor = GameCharacter(
        user_id=1,
        name=thor.name,
        data_keys=str(thor.keys()),
        data_vals=str(thor.values()),
    )
    db.session.add(db_thor)
    db.session.commit()
    new_thor = GameCharacter.query.first()
    new_thor_character = new_thor.character

    assert (
        thor.experience.to_next_level
        == new_thor_character.experience.to_next_level
        == 45
    )
