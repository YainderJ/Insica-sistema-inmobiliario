from app import create_app, db

app = create_app()

with app.app_context():
    # Este comando lee tu app/models/__init__.py y crea las tablas que falten
    db.create_all()
    print("¡Base de datos y tablas de INSICA actualizadas con éxito!")