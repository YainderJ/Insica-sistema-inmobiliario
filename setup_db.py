import os
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
        
        # 1. Leer credenciales dinámicas desde las variables de entorno
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        # 2. Validación estricta de seguridad
        if not admin_email or not admin_password:
            print("ERROR FATAL: Faltan credenciales administrativas en el entorno.")
            print("Asegúrate de definir ADMIN_EMAIL y ADMIN_PASSWORD en tu archivo .env")
            exit(1)

        # 3. Verificamos si el usuario ya existe usando el correo dinámico
        admin_existente = Usuario.query.filter_by(email=admin_email).first()
        
        if not admin_existente:
            print(f"Creando usuario Administrador ({admin_email})...")
            
            admin = Usuario(
                nombre='Administrador INSICA',
                email=admin_email,
                rol='Admin',
                telefono='+580000000000'
            )
            
            # Asignar la contraseña de forma segura
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            print("Administrador creado exitosamente.")
            print(f"-> Correo: {admin_email}")
            print("-> Clave: [Protegida por variables de entorno]")
        else:
            print(f"El Administrador principal ({admin_email}) ya existe en el sistema.")

if __name__ == '__main__':
    inicializar_base_datos()