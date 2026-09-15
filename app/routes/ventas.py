from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.venta import Venta
from app.models.inmueble import Inmueble

# Nombrado exactamente como 'ventas_bp' para coincidir con app/__init__.py
ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@ventas_bp.route('/procesar_cierre/<int:inmueble_id>', methods=['POST'])
@login_required
def procesar_cierre(inmueble_id):
    # Ampliamos el acceso: Los clientes no pueden cerrar ventas, pero Agentes y Admins sí
    if current_user.rol not in ['Agente', 'Admin']:
        return redirect(url_for('auth.panel'))

    inmueble = Inmueble.query.get_or_404(inmueble_id)
    
    if inmueble.estatus == 'Vendido':
        flash('Esta propiedad ya ha sido vendida anteriormente.', 'error')
        return redirect(url_for('inmuebles.catalogo'))

    monto_ingresado = request.form.get('monto_final', type=float)

    if not monto_ingresado or monto_ingresado <= 0:
        flash('Monto de cierre inválido.', 'error')
        return redirect(url_for('inmuebles.detalle_inmueble', id_inmueble=inmueble.id))

    # Instanciamos utilizando la nomenclatura exacta de tu modelo
    nueva_venta = Venta(
        inmueble_id=inmueble.id,
        agente_id=current_user.id,
        monto_final=monto_ingresado,
        porcentaje_comision=5.0
    )

    # Delegamos la regla de negocio al modelo (Fat Model)
    comision = nueva_venta.calcular_comision()

    # Actualizamos el estatus en el Almacén D1 para ocultarlo del catálogo público
    inmueble.estatus = 'Vendido'

    db.session.add(nueva_venta)
    db.session.commit()

    flash(f'Venta cerrada exitosamente. Comisión generada: ${comision:,.2f}', 'success')
    return redirect(url_for('ventas.mis_ventas'))


@ventas_bp.route('/mis_ventas')
@login_required
def mis_ventas():
    """
    Proceso 4.3: Vista interactiva y reporte financiero.
    Aislamiento de datos: Admin ve el global, Agente ve lo individual.
    """
    # Restringimos el acceso a los Clientes
    if current_user.rol not in ['Agente', 'Admin']:
        return redirect(url_for('auth.panel'))

    # LÓGICA DE CONTROL DE ACCESO BASADO EN ROLES (RBAC)
    if current_user.rol == 'Admin':
        # El Administrador extrae todo el historial del Almacén D4
        ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    else:
        # El Agente solo extrae sus propias transacciones
        ventas = Venta.query.filter_by(agente_id=current_user.id).order_by(Venta.fecha_venta.desc()).all()
    
    # KPIs financieros (Protegidos contra divisiones o sumas nulas si no hay ventas)
    volumen_total = sum(v.monto_final for v in ventas) if ventas else 0.0
    comisiones_acumuladas = sum(v.comision_agente for v in ventas) if ventas else 0.0

    return render_template('ventas/reportes.html', 
                           ventas=ventas, 
                           volumen_total=volumen_total, 
                           comisiones_acumuladas=comisiones_acumuladas)