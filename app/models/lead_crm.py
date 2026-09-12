from app import db
from datetime import datetime

class LeadCRM(db.Model):
    """
    Modelo que representa el Almacén D2: Clientes (Leads).
    Gestiona las consultas e interacciones entre Clientes y Agentes.
    """
    __tablename__ = 'leads_crm'

    id = db.Column(db.Integer, primary_key=True)
    
    # Llaves foráneas que conectan a los actores del flujo
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id'), nullable=False)
    
    # Puede ser nulo si el cliente hace una consulta general a la agencia
    inmueble_id = db.Column(db.Integer, db.ForeignKey('inmuebles.id'), nullable=True) 
    
    # Control del seguimiento comercial
    estado_lead = db.Column(db.String(50), nullable=False, default='NUEVO') # Ej: NUEVO, EN_PROCESO, CERRADO
    historial = db.Column(db.Text, nullable=True) # Notas del agente
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones de SQLAlchemy para facilitar el cruce de datos en las vistas
    cliente = db.relationship('Usuario', foreign_keys=[cliente_id], backref='mis_consultas')
    agente = db.relationship('Agente', foreign_keys=[agente_id], backref='leads_asignados')
    inmueble = db.relationship('Inmueble', foreign_keys=[inmueble_id])

    def __repr__(self):
        return f'<Lead CRM {self.id} - Estatus: {self.estado_lead}>'