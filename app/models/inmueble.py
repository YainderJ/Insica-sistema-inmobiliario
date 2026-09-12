from app import db
from datetime import datetime

class Inmueble(db.Model):
    """
    Modelo que representa el Almacén D1: Inmuebles.
    Reemplaza la antigua lógica de 'Shala/Clase' del repositorio base.
    """
    __tablename__ = 'inmuebles'

    id = db.Column(db.Integer, primary_key=True)
    
    # ID_Agente: Relación directa con la tabla 'usuarios' intacta
    agente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Estructura de datos que viaja con el flujo
    tipo_operacion = db.Column(db.String(50), nullable=False) 
    tipo_inmueble = db.Column(db.String(50), nullable=False)  
    direccion = db.Column(db.String(255), nullable=False)
    precio = db.Column(db.Numeric(12, 2), nullable=False)
    descripcion_general = db.Column(db.Text, nullable=False)
    fotografias = db.Column(db.Text, nullable=True) # {Fotografías} almacenadas como cadena JSON
    
    # Control de estatus comercial
    estado = db.Column(db.String(20), default='DISPONIBLE', nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación inversa para facilitar consultas
    agente = db.relationship('Usuario', backref=db.backref('inmuebles_captados', lazy=True))

    def __repr__(self):
        return f'<Inmueble {self.id} - {self.tipo_inmueble}>'