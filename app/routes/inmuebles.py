import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.inmueble import Inmueble
from app.models.usuario import Usuario

inmuebles_bp = Blueprint('inmuebles', __name__, url_prefix='/inmuebles')

@inmuebles_bp.route('/catalogo', methods=['GET'])
@login_required
def catalogo():
    propiedades = Inmueble.query.all()
    return render_template('inmuebles/catalogo.html', propiedades=propiedades)

@inmuebles_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar_inmueble():
    if current_user.rol != 'INSTRUCTOR':
        flash('No tienes permisos para realizar esta acción.', 'error')
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