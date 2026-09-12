from app import db
from datetime import datetime

class Cita(db.Model):
    """Modelo D3: Gestiona el agendamiento de visitas presenciales."""
    __tablename__ = 'citas'

    id = db.Column(db.Integer, primary_key=True)
    
    # Llaves Foráneas (Corregidas a la arquitectura del repositorio base)
    inmueble_id = db.Column(db.Integer, db.ForeignKey('inmuebles.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Datos de la visita
    fecha_hora = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(50), default='PENDIENTE', nullable=False)
    telefono_contacto = db.Column(db.String(20), nullable=True) # NUEVO CAMPO
    comentarios = db.Column(db.Text, nullable=True) 
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    inmueble = db.relationship('Inmueble', foreign_keys=[inmueble_id])
    cliente = db.relationship('Usuario', foreign_keys=[cliente_id])
    agente = db.relationship('Usuario', foreign_keys=[agente_id])

    def __repr__(self):
        return f'<Cita {self.id} - Inmueble {self.inmueble_id} - Estado: {self.estado}>'