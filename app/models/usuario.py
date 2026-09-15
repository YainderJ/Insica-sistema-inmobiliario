from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    # ==========================================
    # NÚCLEO DE AUTENTICACIÓN - INSICA
    # Roles del dominio inmobiliario: Cliente, Agente, Admin
    # ==========================================
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(30))
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Campo abierto y libre de Enums heredados para evitar LookupError
    rol = db.Column(db.String(20), nullable=False, default='Cliente')
    
    # NUEVO CAMPO: Identidad Corporativa (Uso exclusivo para Agentes Inmobiliarios)
    foto_perfil = db.Column(db.String(200), default='default_avatar.png', nullable=True)
    
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # ==========================================
    # NOTA ARQUITECTÓNICA - INSICA
    # ==========================================
    # Se omiten las declaraciones explícitas de db.relationship hacia los 
    # nuevos almacenes (Inmuebles, Leads, Citas, Ventas) para prevenir 
    # el 'InvalidRequestError' durante la inicialización de los Mappers.
    # El flujo de datos se extrae directamente en la Capa de Control (Rutas) 
    # usando filtros explícitos sobre las llaves foráneas.

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.email} - Rol: {self.rol}>"