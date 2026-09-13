from app import db
from datetime import datetime

class LeadCRM(db.Model):
    """
    Modelo que representa el Almacén D2: Clientes (Leads).
    Centraliza las interacciones y consultas de los clientes potenciales 
    hacia los Agentes Inmobiliarios.
    """
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    
    # Llaves foráneas apuntando correctamente al modelo 'Usuario' unificado
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    inmueble_id = db.Column(db.Integer, db.ForeignKey('inmuebles.id'), nullable=False)
    
    # Datos de la interacción (Procesos 2.1 y 2.3)
    mensaje_cliente = db.Column(db.Text, nullable=False)
    respuesta_agente = db.Column(db.Text, nullable=True)
    
    # Control de estatus estandarizado (Nuevo, En Negociación, Descartado)
    estatus = db.Column(db.String(30), default='Nuevo', nullable=False)
    
    # Trazabilidad temporal
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones inversas (ORM) para la navegación ágil en las vistas
    cliente = db.relationship('Usuario', foreign_keys=[cliente_id], backref=db.backref('leads_generados', lazy=True))
    agente = db.relationship('Usuario', foreign_keys=[agente_id], backref=db.backref('leads_recibidos', lazy=True))
    inmueble = db.relationship('Inmueble', backref=db.backref('leads_asociados', lazy=True))

    def __repr__(self):
        return f'<LeadCRM {self.id} - Cliente: {self.cliente_id} | Inmueble: {self.inmueble_id} | Estatus: {self.estatus}>'