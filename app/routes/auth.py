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
    Centraliza métricas de los 4 módulos operativos para el equipo comercial.
    """
    # Redirección de seguridad si un Cliente intenta acceder escribiendo la URL manual
    if current_user.rol.lower() not in ['agente', 'admin']:
        return redirect(url_for('citas.mis_visitas'))

    # Extracción de Métricas (KPIs)
    # 1. Total en Ventas (Suma de montos finales del Almacén D4)
    total_ventas = db.session.query(func.sum(Venta.monto_final)).scalar() or 0.0
    
    # 2. Inmuebles Disponibles (Conteo del Almacén D1)
    inmuebles_disponibles = Inmueble.query.filter_by(estatus='Disponible').count()
    
    # 3. Leads Nuevos / Activos (Conteo del Almacén D2)
    leads_activos = LeadCRM.query.filter_by(estatus='Nuevo').count()
    
    # 4. Citas Pendientes (Conteo del Almacén D3)
    citas_pendientes = Cita.query.filter_by(estatus='Pendiente').count()

    return render_template('dashboard/panel.html', 
                           total_ventas=total_ventas,
                           inmuebles_disponibles=inmuebles_disponibles,
                           leads_activos=leads_activos,
                           citas_pendientes=citas_pendientes)


@auth_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    """Gestión de perfil base para cualquier rol del sistema inmobiliario."""
    if request.method == "POST":
        current_user.nombre = request.form.get("nombre")
        current_user.telefono = request.form.get("telefono")

        db.session.commit()
        flash("¡Perfil actualizado con éxito!", "success")
        return redirect(url_for("auth.panel"))

    return render_template("users/perfil.html")


@auth_bp.route("/cerrar-sesion")
@login_required
def cerrar_sesion():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.iniciar_sesion"))