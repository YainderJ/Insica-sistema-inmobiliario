import pytest
from app import create_app, db

@pytest.fixture
def cliente_test(client, init_database):
    """Prueba que la página de inicio cargue correctamente"""
    respuesta = client.get('/')
    assert respuesta.status_code == 200
    assert b"Inmobiliaria INSICA" in respuesta.data # O el título que tengas en tu home

def test_acceso_catalogo_sin_login(client):
    """
    Valida que los clientes puedan ver el catálogo público sin estar registrados,
    accediendo al Almacén D1.
    """
    respuesta = client.get('/inmuebles/catalogo')
    # Validamos que cargue con éxito (código 200)
    assert respuesta.status_code == 200

def test_redireccion_rutas_protegidas(client):
    """
    Valida que las rutas administrativas (como registrar inmueble) 
    estén protegidas para los Agentes Inmobiliarios y redirijan correctamente.
    """
    respuesta = client.get('/inmuebles/registrar')
    
    # 302 es el código HTTP de redirección correcta
    assert respuesta.status_code == 302 
    
    # Aserción corregida: Busca exactamente la ruta '/iniciar-sesion' en la respuesta
    assert b"/iniciar-sesion" in respuesta.data