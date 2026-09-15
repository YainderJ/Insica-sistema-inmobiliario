import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.inmueble import Inmueble
from app.models.usuario import Usuario

inmuebles_bp = Blueprint('inmuebles', __name__, url_prefix='/inmuebles')

@inmuebles_bp.route('/')
def inicio():
    """
    Ruta raíz (Landing Page pública). 
    Paso 2: Extrae inmuebles disponibles y el directorio de agentes.
    """
    # Extraer los últimos 6 inmuebles disponibles para el escaparate central
    propiedades_destacadas = Inmueble.query.filter_by(estatus='Disponible').order_by(Inmueble.id.desc()).limit(6).all()
    
    # Extraer los usuarios con rol de Agente para la columna derecha
    agentes_directorio = Usuario.query.filter(Usuario.rol.ilike('%agente%')).all()
    
    return render_template('dashboard/inicio.html', propiedades=propiedades_destacadas, agentes=agentes_directorio)

@inmuebles_bp.route('/catalogo')
def catalogo():
    """
    Proceso 1.3: Filtrar y Consultar.
    Renderiza el catálogo aplicando reglas de visibilidad según el rol
    e intercepta los filtros de búsqueda con insensibilidad a mayúsculas/minúsculas.
    """
    # 1. Capturar los parámetros de búsqueda enviados por el método GET
    filtro_operacion = request.args.get('tipo_operacion')
    filtro_inmueble = request.args.get('tipo_inmueble')

    # 2. Establecer la consulta base según los permisos del usuario
    if current_user.is_authenticated and current_user.rol and ('agente' in current_user.rol.lower() or 'admin' in current_user.rol.lower()):
        query_base = Inmueble.query
    else:
        query_base = Inmueble.query.filter_by(estatus='Disponible')

    # 3. Aplicar filtros dinámicos usando ilike() para ignorar mayúsculas/minúsculas
    if filtro_operacion:
        # Los símbolos % aseguran que encuentre la palabra aunque tenga espacios extra
        query_base = query_base.filter(Inmueble.tipo_operacion.ilike(f"%{filtro_operacion}%"))
    
    if filtro_inmueble:
        query_base = query_base.filter(Inmueble.tipo_inmueble.ilike(f"%{filtro_inmueble}%"))

    # 4. Ejecutar la consulta final
    lista_resultados = query_base.order_by(Inmueble.id.desc()).all()
    
    return render_template('inmuebles/catalogo.html', propiedades=lista_resultados)

@inmuebles_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar_inmueble():
    # Bloqueo de seguridad: Solo el Agente Inmobiliario (o Admin) puede captar inmuebles
    if current_user.rol not in ['Agente', 'Admin']:
        flash('No tienes permisos para realizar esta acción. Exclusivo para Agentes.', 'error')
        return redirect(url_for('auth.panel'))

    if request.method == 'POST':
        tipo_operacion = request.form.get('tipo_operacion')
        tipo_inmueble = request.form.get('tipo_inmueble')
        direccion = request.form.get('direccion')
        precio = request.form.get('precio')
        descripcion = request.form.get('descripcion_general')
        
        # PROCESAMIENTO MÚLTIPLE DE FOTOGRAFÍAS
        fotos = request.files.getlist('fotografias')
        nombres_fotos = []
        
        for foto in fotos:
            if foto and foto.filename != '':
                nombre_foto = secure_filename(foto.filename)
                ruta_guardado = os.path.join(current_app.root_path, 'static', 'uploads', nombre_foto)
                foto.save(ruta_guardado)
                nombres_fotos.append(nombre_foto)

        # Unimos los nombres con comas (ej. "foto1.jpg,foto2.jpg")
        fotos_str = ','.join(nombres_fotos) if nombres_fotos else 'default.png'

        # Inserción del nuevo registro en el Almacén D1
        nuevo_inmueble = Inmueble(
            tipo_operacion=tipo_operacion,
            tipo_inmueble=tipo_inmueble,
            direccion=direccion,
            precio=float(precio),
            descripcion_general=descripcion,
            fotografias=fotos_str,
            agente_id=current_user.id
        )

        db.session.add(nuevo_inmueble)
        db.session.commit()
        
        # Mensaje de éxito devuelto al Agente Inmobiliario
        flash('Inmueble publicado con éxito.', 'success')
        return redirect(url_for('inmuebles.catalogo'))

    return render_template('inmuebles/registrar.html')

@inmuebles_bp.route('/detalle/<int:id_inmueble>', methods=['GET'])
@login_required
def detalle_inmueble(id_inmueble):
    """Proceso 1.4: Genera la Ficha Técnica detallada y extrae al Agente."""
    inmueble = Inmueble.query.get_or_404(id_inmueble)
    
    # Extraemos los datos del Agente Inmobiliario (antiguo Instructor) desde la base de datos
    agente = Usuario.query.get(inmueble.agente_id)
    
    return render_template('inmuebles/detalle.html', inmueble=inmueble, agente=agente)

@inmuebles_bp.route('/eliminar/<int:id_inmueble>', methods=['POST'])
@login_required
def eliminar_inmueble(id_inmueble):
    """Permite al Agente Inmobiliario borrar sus propios inmuebles."""
    inmueble = Inmueble.query.get_or_404(id_inmueble)
    
    # Validación de seguridad: Solo el creador puede borrarlo
    if current_user.id != inmueble.agente_id:
        flash('Acceso denegado: Solo el agente captador puede eliminar este inmueble.', 'error')
        return redirect(url_for('inmuebles.catalogo'))
        
    db.session.delete(inmueble)
    db.session.commit()
    flash('Inmueble eliminado del catálogo exitosamente.', 'success')
    return redirect(url_for('inmuebles.catalogo'))

# ... (Mantén tus rutas de catálogo, registrar, detalle y eliminar intactas arriba) ...

# ... (Mantén tus rutas de catálogo, registrar, detalle y eliminar intactas arriba) ...

@inmuebles_bp.route('/editar/<int:id_inmueble>', methods=['GET', 'POST'])
@login_required
def editar_inmueble(id_inmueble):
    """Permite al Agente modificar los datos y fotografías de un inmueble existente."""
    inmueble = Inmueble.query.get_or_404(id_inmueble)
    
    # Validación de seguridad estricta
    if current_user.id != inmueble.agente_id:
        flash('Acceso denegado: No puedes editar un inmueble que no captaste.', 'error')
        return redirect(url_for('inmuebles.catalogo'))

    if request.method == 'POST':
        # 1. Actualizamos los campos de texto
        inmueble.tipo_operacion = request.form.get('tipo_operacion')
        inmueble.precio = float(request.form.get('precio'))
        inmueble.direccion = request.form.get('direccion')  # Ahora se actualiza la dirección
        inmueble.descripcion_general = request.form.get('descripcion_general')
        
        # 2. Procesamiento de nuevas fotografías (si existen)
        fotos = request.files.getlist('fotografias')
        
        # Verificamos si el usuario seleccionó al menos un archivo válido
        if fotos and fotos[0].filename != '':
            nombres_fotos = []
            for foto in fotos:
                if foto and foto.filename != '':
                    nombre_foto = secure_filename(foto.filename)
                    ruta_guardado = os.path.join(current_app.root_path, 'static', 'uploads', nombre_foto)
                    foto.save(ruta_guardado)
                    nombres_fotos.append(nombre_foto)
            
            # Si se guardaron fotos nuevas con éxito, reemplazamos el registro en la BD
            if nombres_fotos:
                inmueble.fotografias = ','.join(nombres_fotos)
        
        # 3. Guardamos los cambios en el Almacén D1
        db.session.commit()
        flash('Datos del inmueble actualizados correctamente.', 'success')
        return redirect(url_for('inmuebles.detalle_inmueble', id_inmueble=inmueble.id))

    # Si es GET, enviamos los datos actuales a la vista
    return render_template('inmuebles/editar.html', inmueble=inmueble)

# ==========================================
# PÁGINAS INSTITUCIONALES (IDENTIDAD INSICA)
# ==========================================

@inmuebles_bp.route('/nosotros')
def nosotros():
    """Renderiza la página corporativa 'Quiénes Somos'."""
    return render_template('dashboard/nosotros.html')

@inmuebles_bp.route('/contacto')
def contacto():
    """Renderiza la página de información de 'Contacto'."""
    return render_template('dashboard/contacto.html')