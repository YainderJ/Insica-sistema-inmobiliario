from app import db
from datetime import datetime

class Inmueble(db.Model):
    """
    Modelo que representa la entidad Inmueble dentro del Almacén D1.
    Gestiona el inventario de propiedades de la agencia inmobiliaria INSICA.
    """
    __tablename__ = 'inmuebles'

    id = db.Column(db.Integer, primary_key=True)
    
    # ID_Agente: Relación directa con el actor Agente Inmobiliario
    agente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Estructura de datos que viaja con el flujo comercial
    tipo_operacion = db.Column(db.String(50), nullable=False) 
    tipo_inmueble = db.Column(db.String(50), nullable=False)  
    direccion = db.Column(db.String(255), nullable=False)
    precio = db.Column(db.Numeric(12, 2), nullable=False)
    descripcion_general = db.Column(db.Text, nullable=False)
    fotografias = db.Column(db.Text, nullable=True, default='default.png')
    
    # Control de estatus comercial (Requerido por el controlador de Ventas)
    estatus = db.Column(db.String(20), default='Disponible', nullable=False)
    
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación inversa para facilitar consultas desde el usuario
    agente = db.relationship('Usuario', backref=db.backref('inmuebles_captados', lazy=True))

    def __repr__(self):
        return f'<Inmueble {self.id} - {self.tipo_inmueble} en {self.direccion} (Estatus: {self.estatus})>'