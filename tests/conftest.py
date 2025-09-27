import os
import pytest

# Ensure database configuration is set before importing the app
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('SESSION_SECRET', 'test-secret')
os.environ.setdefault('FRONTEND_BASE_URL', 'http://testserver')

from main import app, db
from models import Mosque

def _reset_database(db_path: str) -> None:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    with app.app_context():
        db.session.remove()
        db.engine.dispose()
        db.drop_all()
        db.create_all()
        # Seed a sample mosque for access-request tests
        mosque = Mosque(
            name='Test Mosque',
            address='Teststraat 1, Gent',
            phone='+32 9 000 00 00',
            email='test@mosque.be',
        )
        db.session.add(mosque)
        db.session.commit()


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / 'test.sqlite'
    _reset_database(str(db_path))

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()
