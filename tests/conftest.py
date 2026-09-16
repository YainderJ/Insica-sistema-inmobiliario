import os
import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.usuario import Usuario

@pytest.fixture
def app():
    # Usamos una base de datos en memoria para pruebas rápidas y seguras
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'test_secret_insica'

    flask_app = create_app()
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })

    # Levantamos el contexto de la aplicación y creamos las tablas
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        # Limpiamos todo al finalizar los tests
        db.session.remove()
        db.drop_all()

@pytest.fixture
def db_session(app):
    """Provee una sesión de base de datos que hace rollback tras cada test para mantener el aislamiento."""
    yield db.session
    db.session.rollback()

@pytest.fixture
def client(app):
    """Cliente de pruebas para simular peticiones HTTP (GET, POST)."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Ejecutor para comandos CLI de Flask."""
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    """
    Siema la base de datos de pruebas con un superusuario Administrador
    adaptado al dominio corporativo de INSICA.
    """
    usuario_admin = Usuario(
        nombre='Admin Global INSICA',
        email='admin@insica.com',
        password_hash=generate_password_hash('admin123'),
        rol='Admin',
    )
    db.session.add(usuario_admin)
    db.session.commit()
    return db