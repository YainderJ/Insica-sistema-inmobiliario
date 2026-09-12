from app import db
from datetime import datetime

class Venta(db.Model):
    """
    Modelo que representa el Almacén D4: Ventas.
    Registra los cierres de operaciones inmobiliarias y las comisiones.
    """
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    
    # Llaves Foráneas
    inmueble_id = db.Column(db.Integer, db.ForeignKey('inmuebles.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id'), nullable=False)
    
    # Datos financieros del cierre
    monto_cierre = db.Column(db.Numeric(12, 2), nullable=False)
    monto_comision = db.Column(db.Numeric(10, 2), nullable=False) # Comisión calculada para el agente
    
    fecha_cierre = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    inmueble = db.relationship('Inmueble', foreign_keys=[inmueble_id])
    cliente = db.relationship('Usuario', foreign_keys=[cliente_id])
    agente = db.relationship('Agente', foreign_keys=[agente_id])

    def __repr__(self):
        return f'<Venta {self.id} - Monto: {self.monto_cierre}>'