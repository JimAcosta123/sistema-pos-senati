from app import app, db, Producto

# Lista de 50 Productos variados (Bodega Peruana)
lista_productos = [
    # BEBIDAS
    {"nombre": "Coca Cola 3L", "precio": 12.50, "stock": 50},
    {"nombre": "Inca Kola 3L", "precio": 12.50, "stock": 60},
    {"nombre": "Coca Cola 1.5L", "precio": 7.50, "stock": 30},
    {"nombre": "Inca Kola 1.5L", "precio": 7.50, "stock": 35},
    {"nombre": "Agua San Mateo 600ml", "precio": 2.00, "stock": 100},
    {"nombre": "Agua Cielo 1L", "precio": 2.50, "stock": 80},
    {"nombre": "Gatorade Tropical", "precio": 3.50, "stock": 40},
    {"nombre": "Sporade Mandarina", "precio": 2.50, "stock": 45},
    {"nombre": "Cerveza Pilsen 650ml", "precio": 7.00, "stock": 120},
    {"nombre": "Cerveza Cusqueña Trigo", "precio": 8.50, "stock": 60},
    {"nombre": "Volt Energizante", "precio": 2.00, "stock": 150},
    {"nombre": "Frugos Valle Durazno", "precio": 2.50, "stock": 55},
    
    # ABARROTES
    {"nombre": "Arroz Costeño 1kg", "precio": 4.80, "stock": 200},
    {"nombre": "Arroz Faraón 1kg", "precio": 4.50, "stock": 180},
    {"nombre": "Azúcar Rubia Cartavio", "precio": 3.80, "stock": 100},
    {"nombre": "Azúcar Blanca Paramonga", "precio": 4.20, "stock": 80},
    {"nombre": "Aceite Primor 1L", "precio": 11.50, "stock": 60},
    {"nombre": "Aceite Cil 1L", "precio": 10.50, "stock": 50},
    {"nombre": "Fideos Don Vittorio", "precio": 3.20, "stock": 90},
    {"nombre": "Fideos Molitalia", "precio": 3.00, "stock": 85},
    {"nombre": "Atún Florida Trozos", "precio": 6.50, "stock": 70},
    {"nombre": "Atún Real Grated", "precio": 5.00, "stock": 100},
    {"nombre": "Leche Gloria Azul", "precio": 4.20, "stock": 150},
    {"nombre": "Leche Gloria Roja", "precio": 4.20, "stock": 100},
    
    # SNACKS Y GOLOSINAS
    {"nombre": "Galletas Oreo Paq.", "precio": 1.50, "stock": 200},
    {"nombre": "Galletas Soda San Jorge", "precio": 1.00, "stock": 150},
    {"nombre": "Papas Lays Clásicas", "precio": 1.50, "stock": 80},
    {"nombre": "Piqueo Snax", "precio": 2.00, "stock": 70},
    {"nombre": "Chizitos Fiesta", "precio": 1.20, "stock": 90},
    {"nombre": "Chocolate Sublime", "precio": 1.50, "stock": 120},
    {"nombre": "Triángulo D'Onofrio", "precio": 2.00, "stock": 60},
    {"nombre": "Caramelos de Limón (Bolsa)", "precio": 0.20, "stock": 500},
    {"nombre": "Chicle Trident", "precio": 1.00, "stock": 200},
    
    # ASEO Y LIMPIEZA
    {"nombre": "Papel Higiénico Suave (4un)", "precio": 5.50, "stock": 80},
    {"nombre": "Papel Higiénico Elite (2un)", "precio": 3.00, "stock": 60},
    {"nombre": "Detergente Ace 500g", "precio": 5.50, "stock": 50},
    {"nombre": "Detergente Bolívar 500g", "precio": 5.20, "stock": 45},
    {"nombre": "Jabón Bolívar Azul", "precio": 3.50, "stock": 70},
    {"nombre": "Ayudín Pasta", "precio": 2.50, "stock": 60},
    {"nombre": "Lejía Sapolio 1L", "precio": 2.80, "stock": 55},
    {"nombre": "Shampoo H&S", "precio": 18.90, "stock": 25},
    {"nombre": "Shampoo Sedal", "precio": 15.00, "stock": 30},
    {"nombre": "Pasta Dental Kolynos", "precio": 3.50, "stock": 100},
    {"nombre": "Desodorante Rexona", "precio": 8.50, "stock": 40},
    
    # OTROS
    {"nombre": "Pan Bimbo Blanco", "precio": 8.50, "stock": 20},
    {"nombre": "Mantequilla Manty", "precio": 2.50, "stock": 50},
    {"nombre": "Mermelada Gloria", "precio": 3.50, "stock": 40},
    {"nombre": "Yogurt Gloria Fresa 1L", "precio": 7.20, "stock": 35},
    {"nombre": "Huevos Pardos (Kilo)", "precio": 9.00, "stock": 30},
    {"nombre": "Sal Marina Emsal", "precio": 1.50, "stock": 100}
]

print("🚀 Iniciando carga masiva de inventario...")

with app.app_context():
    contador = 0
    for data in lista_productos:
        # Verificar si ya existe para no duplicar
        existe = Producto.query.filter_by(nombre=data["nombre"]).first()
        if not existe:
            nuevo = Producto(
                nombre=data["nombre"], 
                precio=data["precio"], 
                stock=data["stock"]
            )
            db.session.add(nuevo)
            contador += 1
            print(f"✅ Agregado: {data['nombre']}")
        else:
            print(f"⚠️ Ya existe: {data['nombre']}")

    db.session.commit()
    print(f"\n🎉 ¡Proceso terminado! Se agregaron {contador} productos nuevos.")