from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.venta import Venta
from app.models.inmueble import Inmueble

ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@ventas_bp.route('/procesar_cierre/<int:inmueble_id>', methods=['GET', 'POST'])
@login_required
def procesar_cierre(inmueble_id):
    """
    Procesos 4.1 y 4.2: Procesar Cierre y Calcular Comisión.
    Reemplaza la antigua lógica de 'pagos' y 'paquetes'.
    """
    # Mapeo de roles base: INSTRUCTOR = Agente Inmobiliario
    if current_user.rol != 'INSTRUCTOR':
        flash("Acceso denegado. Solo los Agentes pueden registrar cierres de ventas.", "error")
        return redirect(url_for('inmuebles.catalogo'))

    inmueble = Inmueble.query.get_or_404(inmueble_id)

    if request.method == 'POST':
        # Flujo: "Ingresa datos del cierre"
        monto_cierre_str = request.form.get('monto_cierre')
        cliente_id = request.form.get('cliente_id') 

        try:
            monto_cierre = float(monto_cierre_str)
            
            # Proceso 4.2: Calcular Comisión (Ej: 5% estándar sobre el monto de cierre)
            monto_comision = monto_cierre * 0.05
            
            # Instancia del nuevo registro para el Almacén D4
            nueva_venta = Venta(
                inmueble_id=inmueble.id,
                cliente_id=cliente_id,
                agente_id=current_user.id,
                monto_cierre=monto_cierre,
                monto_comision=monto_comision
            )
            
            # Actualizamos el estatus del inmueble en el Almacén D1
            inmueble.estado = 'VENDIDO'
            
            # Flujo: "Guarda venta y comisión" hacia D4: Ventas
            db.session.add(nueva_venta)
            db.session.commit()
            
            flash(f"Venta registrada con éxito. Comisión calculada: ${monto_comision:,.2f}", "success")
            return redirect(url_for('ventas.reportes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar el cierre: {str(e)}", "error")

    # Renderizado del formulario (se creará en la capa de vistas)
    return render_template('ventas/procesar_cierre.html', inmueble=inmueble)

@ventas_bp.route('/reportes', methods=['GET'])
@login_required
def reportes():
    """
    Proceso 4.3: Generar Reporte.
    El Agente solicita y visualiza sus métricas financieras.
    """
    if current_user.rol != 'INSTRUCTOR':
        flash("Acceso denegado.", "error")
        return redirect(url_for('dashboard.inicio'))

    # Flujo: "Extrae historial" desde D4: Ventas
    ventas_realizadas = Venta.query.filter_by(agente_id=current_user.id).order_by(Venta.fecha_cierre.desc()).all()
    
    # Cálculo rápido del reporte acumulado
    total_comisiones = sum(v.monto_comision for v in ventas_realizadas)
    total_ventas = sum(v.monto_cierre for v in ventas_realizadas)
    
    # Flujo: "Muestra reporte" al Agente
    return render_template('ventas/reportes.html', 
                           ventas=ventas_realizadas, 
                           total_comisiones=total_comisiones,
                           total_ventas=total_ventas)