import pytest
from app import create_app, db
from app.models.inmueble import Inmueble
from app.models.lead_crm import LeadCRM
from app.models.usuario import Usuario

def test_flujo_filtrar_inmuebles(client, init_database):
    """
    Prueba de Integración: Proceso 1.3 Filtrar y Consultar.
    Simula a un Cliente buscando propiedades por un criterio específico
    para validar que el Almacén D1 retorna los datos correctos.
    """
    inmueble_prueba = Inmueble(
        agente_id=1,
        tipo_operacion="Alquiler",
        tipo_inmueble="Apartamento",
        direccion="Avenida 5 de Julio, Maracaibo",
        precio=400.00,
        descripcion_general="Apartamento tipo estudio amoblado.",
        estatus="Disponible"
    )
    db.session.add(inmueble_prueba)
    db.session.commit()

    respuesta = client.get('/inmuebles/catalogo?tipo_inmueble=Apartamento')

    assert respuesta.status_code == 200
    assert b"Apartamento tipo" in respuesta.data


def test_flujo_registrar_solicitud_crm(init_database):
    """
    Prueba de Integración: Proceso 2.1 Registrar Solicitud.
    Valida de forma directa que el flujo de datos del cliente 
    se consolide correctamente en el Almacén D2 (CRM), respetando
    la integridad referencial y las restricciones de seguridad.
    """
    # 1. Creamos al Cliente en la tabla Usuario cumpliendo la restricción NOT NULL
    cliente_prueba = Usuario(
        nombre="Carlos Pérez",
        email="carlos.perez@email.com",
        telefono="0414-1234567",
        rol="Cliente",
        password_hash="hash_seguro_simulado_123"  # <-- Solución: Campo de seguridad obligatorio
    )
    db.session.add(cliente_prueba)
    db.session.commit()

    # 2. Instanciamos el Lead vinculando el ID del cliente recién creado
    nuevo_lead = LeadCRM(
        cliente_id=cliente_prueba.id, # Llave Foránea hacia el Usuario
        agente_id=1,     # Agente a cargo del inmueble
        inmueble_id=1,   # ID de la propiedad consultada
        mensaje_cliente="Deseo agendar una visita para este fin de semana.",
        estatus="Nuevo"
    )
    
    # 3. Ejecutamos el flujo de guardado en base de datos (Almacén D2)
    db.session.add(nuevo_lead)
    db.session.commit()

    # 4. Verificación Crítica: Confirmar que el Lead se guardó y persistió
    lead_guardado = LeadCRM.query.filter_by(cliente_id=cliente_prueba.id).first()
    
    assert lead_guardado is not None
    assert lead_guardado.mensaje_cliente == 'Deseo agendar una visita para este fin de semana.'