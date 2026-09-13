from app import create_app, db

# IMPORTANTE: El orden de importación importa para SQLAlchemy
# 1. Modelos sin llaves foráneas (Padres)
from app.models.usuario import Usuario
from app.models.inmueble import Inmueble

# 2. Modelos con llaves foráneas (Hijos)
from app.models.venta import Venta
from app.models.lead_crm import LeadCRM
from app.models.cita import Cita

app = create_app()

with app.app_context():
    print("Iniciando purga de base de datos antigua...")
    db.drop_all()
    print("Creando el nuevo esquema relacional INSICA...")
    db.create_all()
    print("¡Base de datos inicializada correctamente sin errores de ForeignKey!")