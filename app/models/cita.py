from app import db
from datetime import datetime

class Cita(db.Model):
    """
    Modelo que representa el Almacén D3: Citas.
    Gestiona las solicitudes de agendamiento entre Clientes y Agentes Inmobiliarios.
    """
    __tablename__ = 'citas'

    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones del Dominio Inmobiliario
    inmueble_id = db.Column(db.Integer, db.ForeignKey('inmuebles.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Datos de la visita y contacto
    fecha_hora = db.Column(db.DateTime, nullable=False)
    telefono_contacto = db.Column(db.String(30), nullable=False)
    comentarios = db.Column(db.Text, nullable=True)
    
    # Control de estatus de la cita (Corregido para coincidir con el Controlador)
    estatus = db.Column(db.String(20), default='Pendiente', nullable=False)
    
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones inversas (ORM)
    inmueble = db.relationship('Inmueble', foreign_keys=[inmueble_id], backref=db.backref('citas_programadas', lazy=True))
    cliente = db.relationship('Usuario', foreign_keys=[cliente_id], backref=db.backref('citas_solicitadas', lazy=True))
    agente = db.relationship('Usuario', foreign_keys=[agente_id], backref=db.backref('citas_asignadas', lazy=True))

    def __repr__(self):
        return f'<Cita {self.id} - Inmueble: {self.inmueble_id} | Estatus: {self.estatus}>'