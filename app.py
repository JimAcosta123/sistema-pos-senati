from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 1. Configuración de Flask
app = Flask(__name__)

# 2. Configuración de la Base de Datos (SQLite por ahora)
# Esto creará un archivo llamado "inventario.db" en tu carpeta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mi_clave_secreta_senati'

# Inicializamos la DB
db = SQLAlchemy(app)

# --- MODELOS (TABLAS DE LA BASE DE DATOS) ---

# Tabla 1: Productos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    # Relación inversa (opcional, para consultas avanzadas)
    detalles = db.relationship('DetalleVenta', backref='producto', lazy=True)

# Tabla 2: Ventas (Cabecera de la boleta)
class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, default=0.0)
    # Relación: Una venta tiene muchos detalles
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True)

# Tabla 3: DetalleVenta (Qué productos se vendieron en cada venta)
class DetalleVenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False) # Precio al momento de la venta

# --- RUTAS ---
@app.route('/')
def home():
    # En lugar de texto, ahora mostramos el archivo HTML
    return render_template('index.html')

# Arrancar
if __name__ == '__main__':
    app.run(debug=True)