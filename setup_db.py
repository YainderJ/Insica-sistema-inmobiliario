from app import create_app, db

# ==========================================
# IMPORTANTE: El orden de importación importa para SQLAlchemy
# ==========================================
# 1. Modelos sin llaves foráneas (Padres)
from app.models.usuario import Usuario
from app.models.inmueble import Inmueble

# 2. Modelos con llaves foráneas (Hijos)
from app.models.venta import Venta
from app.models.lead_crm import LeadCRM
from app.models.cita import Cita

app = create_app()

def inicializar_base_datos():
    with app.app_context():
        print("Iniciando purga de base de datos antigua...")
        db.drop_all()
        
        print("Creando el nuevo esquema relacional INSICA...")
        db.create_all()
        print("¡Base de datos inicializada correctamente sin errores de ForeignKey!")

        # ==========================================
        # SEMBRADO DEL ADMINISTRADOR MAESTRO (Database Seeding)
        # ==========================================
        admin_existente = Usuario.query.filter_by(email='admin@insica.com').first()
        
        if not admin_existente:
            print("Creando usuario Administrador de INSICA...")
            admin = Usuario(
                nombre='Administrador INSICA',
                email='admin@insica.com',
                rol='Admin',
                telefono='+580000000000'
            )
            # Contraseña por defecto para el superusuario
            admin.set_password('AdminInsica2026*')
            
            db.session.add(admin)
            db.session.commit()
            print("Administrador creado exitosamente.")
            print("-> Correo: admin@insica.com")
            print("-> Clave: AdminInsica2026*")
        else:
            print("El Administrador principal ya existe en el sistema.")

if __name__ == '__main__':
    inicializar_base_datos()