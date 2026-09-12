from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.lead_crm import LeadCRM
from app.models.inmueble import Inmueble
from datetime import datetime

crm_bp = Blueprint('crm', __name__, url_prefix='/crm')

@crm_bp.route('/nueva_consulta/<int:inmueble_id>', methods=['POST'])
@login_required
def nueva_consulta(inmueble_id):
    """
    Proceso 2.1: Registrar Solicitud.
    El Cliente (antiguo Yogui) envía una consulta sobre una propiedad.
    """
    # Mapeo de roles base: YOGUI = Cliente
    if current_user.rol != 'YOGUI':
        flash("Solo los clientes registrados pueden enviar consultas.", "error")
        return redirect(url_for('inmuebles.catalogo'))

    inmueble = Inmueble.query.get_or_404(inmueble_id)
    mensaje = request.form.get('mensaje', 'Me interesa esta propiedad. Solicito más información.')

    try:
        # Flujo: "Guarda Lead" hacia el Almacén D2 (LeadCRM)
        nuevo_lead = LeadCRM(
            cliente_id=current_user.id,
            agente_id=inmueble.agente_id,
            inmueble_id=inmueble.id,
            historial=f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Cliente: {mensaje}\n"
        )
        db.session.add(nuevo_lead)
        db.session.commit()
        
        flash("Tu consulta ha sido enviada al agente encargado.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al enviar la consulta: {str(e)}", "error")

    return redirect(url_for('inmuebles.catalogo'))

@crm_bp.route('/panel_leads', methods=['GET'])
@login_required
def panel_leads():
    """
    Proceso 2.4: Consultar Historial.
    El Agente Inmobiliario (antiguo Instructor) visualiza sus prospectos.
    """
    # Mapeo de roles base: INSTRUCTOR = Agente Inmobiliario
    if current_user.rol != 'INSTRUCTOR':
        flash("Acceso denegado. Área exclusiva para Agentes.", "error")
        return redirect(url_for('dashboard.inicio'))

    # Flujo: "Extrae registro" desde el Almacén D2
    leads_asignados = LeadCRM.query.filter_by(agente_id=current_user.id).all()
    
    # Renderizamos la vista (las plantillas HTML las crearemos en la siguiente etapa)
    return render_template('crm/panel_leads.html', leads=leads_asignados)