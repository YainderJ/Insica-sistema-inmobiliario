from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.cita import Cita
from app.models.inmueble import Inmueble
from datetime import datetime

citas_bp = Blueprint('citas', __name__, url_prefix='/citas')

@citas_bp.route('/agendar/<int:inmueble_id>', methods=['POST'])
@login_required
def solicitar_agendamiento(inmueble_id):
    """
    Proceso 3.1: Solicitar Agendamiento.
    El Cliente solicita una fecha y hora para visitar la propiedad.
    """
    # Mapeo: YOGUI = Cliente
    if current_user.rol != 'YOGUI': 
        flash("Solo los clientes registrados pueden solicitar citas.", "error")
        return redirect(url_for('inmuebles.catalogo'))

    inmueble = Inmueble.query.get_or_404(inmueble_id)
    fecha_str = request.form.get('fecha_hora') # Formato esperado del input HTML: YYYY-MM-DDTHH:MM
    comentarios = request.form.get('comentarios', '')
    telefono_contacto = request.form.get('telefono_contacto', '') # CAPTURAMOS EL TELÉFONO

    try:
        fecha_hora = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
        
        # Instancia del nuevo registro para el Almacén D3
        nueva_cita = Cita(
            inmueble_id=inmueble.id,
            cliente_id=current_user.id,
            agente_id=inmueble.agente_id,
            fecha_hora=fecha_hora,
            estado='PENDIENTE',
            comentarios=comentarios,
            telefono_contacto=telefono_contacto # GUARDAMOS EL TELÉFONO
        )
        
        # Flujo: "Registra cita (Pendiente)" hacia D3: Citas
        db.session.add(nueva_cita)
        db.session.commit()
        
        flash("Cita solicitada con éxito. Espera la confirmación del agente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al solicitar la cita: {str(e)}", "error")

    return redirect(url_for('inmuebles.catalogo'))

@citas_bp.route('/agenda', methods=['GET'])
@login_required
def consultar_agenda():
    """
    Proceso 3.2: Consultar Agenda.
    El Agente revisa sus solicitudes de visitas.
    """
    # Mapeo: INSTRUCTOR = Agente Inmobiliario
    if current_user.rol != 'INSTRUCTOR':
        flash("Acceso denegado. Área exclusiva para Agentes.", "error")
        return redirect(url_for('dashboard.inicio'))

    # Flujo: "Extrae calendario" desde D3: Citas
    citas_asignadas = Cita.query.filter_by(agente_id=current_user.id).order_by(Cita.fecha_hora.asc()).all()
    
    # Renderizamos la vista (se construirá en la capa de presentación)
    return render_template('citas/agenda.html', citas=citas_asignadas)

# ==========================================
# NUEVA RUTA: PROCESO 3.3 GESTIONAR CITA
# ==========================================
@citas_bp.route('/cambiar_estado/<int:cita_id>/<string:nuevo_estado>', methods=['POST'])
@login_required
def cambiar_estado(cita_id, nuevo_estado):
    """Permite al Agente Inmobiliario Confirmar o Cancelar la cita."""
    if current_user.rol != 'INSTRUCTOR':
        flash("Acceso denegado.", "error")
        return redirect(url_for('dashboard.inicio'))

    cita = Cita.query.get_or_404(cita_id)
    
    # Seguridad: Validar que la cita pertenezca a este agente
    if cita.agente_id != current_user.id:
        flash("No puedes modificar esta cita.", "error")
        return redirect(url_for('citas.consultar_agenda'))

    if nuevo_estado in ['CONFIRMADA', 'CANCELADA']:
        cita.estado = nuevo_estado
        db.session.commit()
        flash(f"La cita ha sido {nuevo_estado.lower()} exitosamente.", "success")
        
    return redirect(url_for('citas.consultar_agenda'))