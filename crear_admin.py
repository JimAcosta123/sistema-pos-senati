from app import app, db, Usuario

with app.app_context():
    db.create_all() # Crea las tablas vacías

    # Crear usuario administrador
    admin = Usuario(username='admin')
    admin.set_password('1234') # Contraseña sencilla para probar

    db.session.add(admin)
    db.session.commit()

    print("¡Base de datos creada y usuario 'admin' registrado!")