from app import db
from datetime import datetime

class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    inmueble_id = db.Column(db.Integer, db.ForeignKey('inmuebles.id'), nullable=False)
    
    # CORRECCIÓN: Apuntamos exactamente a 'usuario.id' en singular, 
    # respetando el nombre de la tabla que ya tienes en tu base de datos.
    agente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)
    monto_final = db.Column(db.Float, nullable=False)
    porcentaje_comision = db.Column(db.Float, nullable=False, default=5.0)
    comision_agente = db.Column(db.Float, nullable=False)

    # Relaciones
    inmueble = db.relationship('Inmueble', backref=db.backref('venta_asociada', uselist=False))
    agente = db.relationship('Usuario', backref='ventas_cerradas')

    def calcular_comision(self):
        """Calcula automáticamente la comisión del agente."""
        self.comision_agente = (self.monto_final * self.porcentaje_comision) / 100.0
        return self.comision_agente