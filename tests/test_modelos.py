import pytest
from datetime import datetime
from app.models.usuario import Usuario
from app.models.agente import Agente
from app.models.inmueble import Inmueble
from app.models.lead_crm import LeadCRM
from app.models.cita import Cita
from app.models.venta import Venta

# ==============================================================================
# PRUEBAS DEL NÚCLEO DE AUTENTICACIÓN Y ROLES
# ==============================================================================

def test_crear_usuario_cliente():
    """Valida la creación de un perfil de Cliente básico."""
    cliente = Usuario(
        id=1,
        nombre="María Gómez",
        email="maria.cliente@gmail.com",
        telefono="0424-7654321",
        rol="Cliente"
    )
    assert cliente.nombre == "María Gómez"
    assert cliente.rol == "Cliente"

def test_relacion_usuario_agente():
    """Valida la relación 1:1 entre Usuario y el perfil extendido de Agente."""
    usuario_agente = Usuario(
        id=2,
        nombre="Carlos Pérez",
        email="carlos.agente@insica.com",
        rol="Agente"
    )
    perfil_agente = Agente(
        id=usuario_agente.id, # Llave foránea y primaria (Relación 1:1)
        numero_whatsapp="584141234567",
        bio="Agente Senior"
    )
    assert perfil_agente.id == 2
    assert perfil_agente.numero_whatsapp == "584141234567"

# ==============================================================================
# PRUEBAS DEL MÓDULO D1: INVENTARIO DE INMUEBLES (DFD Proceso 1.0)
# ==============================================================================

def test_crear_inmueble_catalogo():
    """Valida el registro de una propiedad asignada a un agente captador."""
    propiedad = Inmueble(
        id=100,
        agente_id=2, # Relación con el Agente Carlos
        tipo_operacion="Venta",
        tipo_inmueble="Casa",
        direccion="Sector Valle Frío, Maracaibo",
        precio=45000.00,
        descripcion_general="Casa amplia de 3 habitaciones.",
        estatus="Disponible"
    )
    assert propiedad.tipo_operacion == "Venta"
    assert propiedad.precio == 45000.00
    assert propiedad.estatus == "Disponible"
    assert propiedad.agente_id == 2

# ==============================================================================
# PRUEBAS DEL MÓDULO D2: CRM E INTERACCIONES (DFD Proceso 2.0)
# ==============================================================================

def test_crear_lead_crm():
    """Valida la triangulación de llaves foráneas al generar una consulta."""
    lead = LeadCRM(
        cliente_id=1,   # María
        agente_id=2,    # Carlos
        inmueble_id=100,# La Casa en Valle Frío
        mensaje_cliente="Me interesa esta propiedad, ¿aceptan financiamiento?",
        estatus="Nuevo"
    )
    assert lead.cliente_id == 1
    assert lead.agente_id == 2
    assert lead.inmueble_id == 100
    assert lead.estatus == "Nuevo"

# ==============================================================================
# PRUEBAS DEL MÓDULO D3: GESTIÓN DE CITAS (DFD Proceso 3.0)
# ==============================================================================

def test_solicitud_cita_fisica():
    """Valida el agendamiento de una visita presencial."""
    fecha_visita = datetime(2026, 10, 15, 14, 30) # 15 de Octubre 2026, 2:30 PM
    cita = Cita(
        inmueble_id=100,
        cliente_id=1,
        agente_id=2,
        fecha_hora=fecha_visita,
        telefono_contacto="0424-7654321",
        estatus="Pendiente"
    )
    assert cita.fecha_hora.year == 2026
    assert cita.estatus == "Pendiente"
    assert cita.inmueble_id == 100

# ==============================================================================
# PRUEBAS DEL MÓDULO D4: VENTAS Y COMISIONES (DFD Proceso 4.0)
# ==============================================================================

def test_calculo_cierre_venta():
    """Valida el cierre de la transacción financiera y cálculo de comisión."""
    # Supongamos que la casa de 45,000 se cerró por 42,000 con 5% de comisión
    monto_cierre = 42000.00
    porcentaje = 5.0
    comision_calculada = (monto_cierre * porcentaje) / 100

    venta = Venta(
        inmueble_id=100,
        agente_id=2,
        monto_final=monto_cierre,
        porcentaje_comision=porcentaje,
        comision_agente=comision_calculada
    )
    
    assert venta.monto_final == 42000.00
    assert venta.comision_agente == 2100.00 # El 5% de 42,000 es 2,100