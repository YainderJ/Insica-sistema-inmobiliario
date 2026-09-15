from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app.models.cita import Cita
from app.models.inmueble import Inmueble
from app.models.lead_crm import LeadCRM
from app import db

citas_bp = Blueprint('citas', __name__, url_prefix='/citas')

# ==========================================
# VISTA DEL CLIENTE (PANEL DE VISITAS)
# ==========================================
@citas_bp.route('/mis_visitas')
@login_required
def mis_visitas():
    """
    Panel Privado del Cliente.
    Extrae el historial de citas (Almacén D3) y consultas (Almacén D2) del usuario actual.
    """
    # Validamos que el rol corresponda a un Cliente
    if current_user.rol.lower() in ['agente', 'admin']:
        return redirect(url_for('auth.panel'))

    # Extraer las citas agendadas por este cliente (Almacén D3)
    citas_cliente = Cita.query.filter_by(cliente_id=current_user.id).order_by(Cita.id.desc()).all()
    
    # Extraer las consultas o solicitudes de información enviadas (Almacén D2)
    consultas_cliente = LeadCRM.query.filter_by(cliente_id=current_user.id).order_by(LeadCRM.id.desc()).all()

    return render_template('citas/mis_visitas.html', citas=citas_cliente, consultas=consultas_cliente)

# ==========================================
# PROCESO 3.1: SOLICITAR AGENDAMIENTO
# ==========================================
@citas_bp.route('/solicitar/<int:inmueble_id>', methods=['POST'])
@login_required
def solicitar_agendamiento(inmueble_id):
    # Validación: Solo los Clientes pueden solicitar el agendamiento de citas
    if current_user.rol != 'Cliente':
        flash('Solo los clientes registrados pueden solicitar citas.', 'error')
        return redirect(url_for('inmuebles.catalogo'))
        
    inmueble = Inmueble.query.get_or_404(inmueble_id)
    
    fecha_hora_str = request.form.get('fecha_hora')
    telefono = request.form.get('telefono_contacto')
    comentarios = request.form.get('comentarios')
    
    try:
        fecha_hora_obj = datetime.strptime(fecha_hora_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash('Formato de fecha inválido.', 'error')
        return redirect(url_for('inmuebles.detalle_inmueble', id_inmueble=inmueble.id))

    # Inserción en el Almacén D3
    nueva_cita = Cita(
        cliente_id=current_user.id,
        agente_id=inmueble.agente_id,
        inmueble_id=inmueble.id,
        fecha_hora=fecha_hora_obj,
        telefono_contacto=telefono,
        comentarios=comentarios,
        estatus='Pendiente' # Corrección a 'estatus'
    )
    
    db.session.add(nueva_cita)
    db.session.commit()
    
    flash('Solicitud de visita enviada exitosamente. El agente confirmará su disponibilidad pronto.', 'success')
    return redirect(url_for('citas.mis_visitas'))

# ==========================================
# PROCESO 3.2: CONSULTAR AGENDA (AGENTE)
# ==========================================
@citas_bp.route('/agenda')
@login_required
def agenda():
    if current_user.rol not in ['Agente', 'Admin']:
        flash('Acceso denegado. Área exclusiva para Agentes.', 'error')
        return redirect(url_for('auth.panel'))
        
    citas = Cita.query.filter_by(agente_id=current_user.id).order_by(Cita.fecha_hora.asc()).all()
    return render_template('citas/agenda.html', citas=citas)

# ==========================================
# PROCESO 3.3: GESTIONAR CITA
# ==========================================
@citas_bp.route('/cambiar_estatus/<int:cita_id>/<string:nuevo_estatus>', methods=['POST'])
@login_required
def cambiar_estatus(cita_id, nuevo_estatus):
    if current_user.rol not in ['Agente', 'Admin']:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('auth.panel'))

    cita = Cita.query.get_or_404(cita_id)
    
    if cita.agente_id != current_user.id:
        flash('No puedes modificar una cita asignada a otro agente.', 'error')
        return redirect(url_for('citas.agenda'))

    if nuevo_estatus in ['Confirmada', 'Cancelada', 'Reprogramada']:
        cita.estatus = nuevo_estatus
        db.session.commit()
        flash(f'La cita ha sido {nuevo_estatus.lower()} exitosamente.', 'success')
        
    return redirect(url_for('citas.agenda'))