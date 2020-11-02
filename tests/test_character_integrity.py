"""
Ensure that saving/loading a character doesn't cause any mutation to its data
"""
import pytest
import tempfile
import os
from tabletop_story.__init__ import create_app
from tabletop_story.app import init_app, plugins


@pytest.fixture
def client():
    global app, db, bcrypt, login_manager
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
            yield client
    os.close(db_fd)
    os.unlink(db_path)


def test_character_mutation(client):
    pass
