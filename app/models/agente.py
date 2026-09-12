from app import db

class Agente(db.Model):
    """
    Modelo que extiende la tabla de usuarios base.
    Representa a los Agentes Inmobiliarios encargados de captar inmuebles y cerrar ventas.
    """
    __tablename__ = 'agentes'

    # Relación 1 a 1 con la tabla usuarios base
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    
    # Datos profesionales específicos del agente
    numero_whatsapp = db.Column(db.String(30), nullable=True) 
    bio = db.Column(db.Text, nullable=True) 
    foto_perfil = db.Column(db.String(255), nullable=True, default='default_agent.png')
    
    # Relación inversa para acceder al usuario desde el agente
    usuario = db.relationship('Usuario', backref=db.backref('perfil_agente', uselist=False))

    def __repr__(self):
        return f'<Agente ID: {self.id} - WhatsApp: {self.numero_whatsapp}>'