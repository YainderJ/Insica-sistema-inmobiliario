from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from sqlalchemy import func
from app.models.usuario import Usuario
from app.models.inmueble import Inmueble
from app.models.cita import Cita
from app.models.lead_crm import LeadCRM
from app.models.venta import Venta
import os
from werkzeug.utils import secure_filename
from flask import current_app


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol")

        if not nombre or not email or not password or not rol:
            flash("Datos incompletos", "error")
            return redirect(url_for("auth.registro"))

        # Dominio inmobiliario estricto
        roles_validos = ["Cliente", "Agente", "Admin"]
        if rol not in roles_validos:
            flash("Rol inválido", "error")
            return redirect(url_for("auth.registro"))

        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash("El correo electrónico ya está registrado", "error")
            return redirect(url_for("auth.registro"))

        password_hash = generate_password_hash(password)

        usuario = Usuario(
            nombre=nombre,
            email=email,
            password_hash=password_hash,
            rol=rol
        )

        db.session.add(usuario)
        db.session.commit()

        flash("Registro exitoso. Por favor inicia sesión.", "success")
        return redirect(url_for("auth.iniciar_sesion"))

    return render_template("auth/registro.html")


@auth_bp.route("/iniciar-sesion", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password_hash, password):
            login_user(usuario)
            flash(f"¡Bienvenido/a {usuario.nombre}!", "success")
            return redirect(url_for("auth.panel"))

        flash("Credenciales incorrectas", "danger")
        return redirect(url_for("auth.iniciar_sesion"))

    return render_template("auth/iniciar_sesion.html")


@auth_bp.route('/panel')
@login_required
def panel():
    """
    Dashboard Ejecutivo.
    Centraliza métricas de los 4 módulos operativos aislando los datos 
    según el rol (Admin = Global, Agente = Individual).
    """
    # Redirección de seguridad si un Cliente intenta acceder escribiendo la URL manual
    if current_user.rol.lower() not in ['agente', 'admin']:
        return redirect(url_for('citas.mis_visitas'))

    # ==========================================
    # 1. MÉTRICAS GLOBALES (Visión del Administrador)
    # ==========================================
    if current_user.rol == 'Admin':
        total_ventas = db.session.query(func.sum(Venta.monto_final)).scalar() or 0.0
        inmuebles_disponibles = Inmueble.query.filter_by(estatus='Disponible').count()
        leads_activos = LeadCRM.query.filter_by(estatus='Nuevo').count()
        citas_pendientes = Cita.query.filter_by(estatus='Pendiente').count()
        
        titulo_panel = "Resumen Global de la Agencia"

    # ==========================================
    # 2. MÉTRICAS INDIVIDUALES (Visión del Agente Inmobiliario)
    # ==========================================
    else:
        # Filtramos estrictamente por el ID del agente actual (current_user.id)
        
        # Suma de ventas donde el inmueble vinculado pertenece al agente
        total_ventas = db.session.query(func.sum(Venta.monto_final))\
            .join(Inmueble).filter(Inmueble.agente_id == current_user.id).scalar() or 0.0
        
        # Conteo de inmuebles propios disponibles
        inmuebles_disponibles = Inmueble.query.filter_by(estatus='Disponible', agente_id=current_user.id).count()
        
        # Conteo de Leads vinculados a los inmuebles del agente
        leads_activos = LeadCRM.query.join(Inmueble)\
            .filter(Inmueble.agente_id == current_user.id, LeadCRM.estatus == 'Nuevo').count()
        
        # Conteo de Citas vinculadas a los inmuebles del agente
        citas_pendientes = Cita.query.join(Inmueble)\
            .filter(Inmueble.agente_id == current_user.id, Cita.estatus == 'Pendiente').count()
            
        titulo_panel = "Mi Rendimiento Operativo"

    # Renderizamos la vista pasando las variables correspondientes
    return render_template('dashboard/panel.html', 
                           total_ventas=total_ventas,
                           inmuebles_disponibles=inmuebles_disponibles,
                           leads_activos=leads_activos,
                           citas_pendientes=citas_pendientes,
                           titulo_panel=titulo_panel)


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """
    Gestión de la identidad corporativa.
    Exclusivo para Agentes Inmobiliarios y Administradores.
    """
    # BLOQUEO DE SEGURIDAD: Los clientes no tienen perfil corporativo
    if current_user.rol.lower() not in ['agente', 'admin']:
        flash('Acceso denegado. Solo el equipo comercial puede gestionar un perfil público.', 'error')
        return redirect(url_for('citas.mis_visitas'))

    if request.method == 'POST':
        # 1. Actualizar el teléfono
        nuevo_telefono = request.form.get('telefono')
        if nuevo_telefono:
            current_user.telefono = nuevo_telefono
            
        # 2. Procesar la subida de la nueva foto de perfil
        foto = request.files.get('foto_perfil')
        if foto and foto.filename != '':
            nombre_foto = secure_filename(foto.filename)
            # Guardamos la imagen en la carpeta de uploads del sistema
            ruta_guardado = os.path.join(current_app.root_path, 'static', 'uploads', nombre_foto)
            foto.save(ruta_guardado)
            
            # Actualizamos el registro de la BD
            current_user.foto_perfil = nombre_foto
            
        # 3. Confirmar transacción
        db.session.commit()
        flash('Perfil corporativo actualizado con éxito.', 'success')
        return redirect(url_for('auth.perfil'))
        
    return render_template('auth/perfil.html')


@auth_bp.route("/cerrar-sesion")
@login_required
def cerrar_sesion():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.iniciar_sesion"))