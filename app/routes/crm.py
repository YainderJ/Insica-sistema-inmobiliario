from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from app.models.lead_crm import LeadCRM
from app.models.inmueble import Inmueble
from app import db

crm_bp = Blueprint('crm', __name__, url_prefix='/crm')

# ==========================================
# PROCESO 2.1: REGISTRAR SOLICITUD (LEAD)
# ==========================================
@crm_bp.route('/solicitar_info/<int:inmueble_id>', methods=['POST'])
@login_required
def registrar_solicitud(inmueble_id):
    # Validación: Solo los Clientes pueden generar un Lead de compra/alquiler
    if current_user.rol != 'Cliente':
        flash('Solo los clientes registrados pueden solicitar información comercial.', 'error')
        return redirect(url_for('inmuebles.detalle_inmueble', id_inmueble=inmueble_id))
        
    inmueble = Inmueble.query.get_or_404(inmueble_id)
    
    # Captura del mensaje enviado desde el formulario de la ficha del inmueble
    mensaje = request.form.get('mensaje')
    
    if not mensaje:
        flash('El mensaje de consulta no puede estar vacío.', 'error')
        return redirect(url_for('inmuebles.detalle_inmueble', id_inmueble=inmueble.id))

    # Inserción del nuevo registro en el Almacén D2: Clientes (Leads)
    nuevo_lead = LeadCRM(
        cliente_id=current_user.id,
        agente_id=inmueble.agente_id,
        inmueble_id=inmueble.id,
        mensaje_cliente=mensaje,
        estatus='Nuevo'
    )
    
    db.session.add(nuevo_lead)
    db.session.commit()
    
    # Notificación de éxito para el Cliente
    flash('Tu consulta ha sido enviada con éxito. El agente inmobiliario te contactará pronto.', 'success')
    return redirect(url_for('inmuebles.detalle_inmueble', id_inmueble=inmueble.id))

# ==========================================
# PROCESO 2.4: CONSULTAR HISTORIAL (PANEL CRM)
# ==========================================
@crm_bp.route('/panel_leads')
@login_required
def panel_leads():
    # Validación: Área exclusiva para el equipo corporativo
    if current_user.rol not in ['Agente', 'Admin']:
        flash('Acceso denegado. Área exclusiva para el equipo comercial.', 'error')
        return redirect(url_for('auth.panel'))
        
    # LÓGICA DE CONTROL DE ACCESO (RBAC)
    if current_user.rol == 'Admin':
        # El Administrador extrae TODOS los leads del Almacén D2 (Visión Global)
        leads = LeadCRM.query.order_by(LeadCRM.fecha_registro.desc()).all()
    else:
        # El Agente solo extrae los leads asignados a sus propiedades
        leads = LeadCRM.query.filter_by(agente_id=current_user.id).order_by(LeadCRM.fecha_registro.desc()).all()
        
    return render_template('crm/panel_leads.html', leads=leads)

# ==========================================
# PROCESO 2.3: RESPONDER Y ACTUALIZAR LEAD
# ==========================================
@crm_bp.route('/gestionar_lead/<int:lead_id>', methods=['POST'])
@login_required
def gestionar_lead(lead_id):
    if current_user.rol not in ['Agente', 'Admin']:
        return redirect(url_for('auth.panel'))

    lead = LeadCRM.query.get_or_404(lead_id)
    
    # Seguridad modificada: El Admin puede gestionar cualquier lead, el Agente solo los suyos
    if current_user.rol != 'Admin' and lead.agente_id != current_user.id:
        flash('No tienes autorización para gestionar este contacto.', 'error')
        return redirect(url_for('crm.panel_leads'))

    # Captura de datos del formulario
    nuevo_estatus = request.form.get('estatus')
    respuesta = request.form.get('respuesta_agente')

    # Actualización en el Almacén D2
    if nuevo_estatus in ['Nuevo', 'En Negociación', 'Descartado']:
        lead.estatus = nuevo_estatus
        
    if respuesta:
        lead.respuesta_agente = respuesta

    db.session.commit()
    flash('El estado del prospecto ha sido actualizado exitosamente.', 'success')
    return redirect(url_for('crm.panel_leads'))