import pandas as pd
from flask import send_file
import io
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
# --- NUEVAS IMPORTACIONES DE SEGURIDAD ---
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# 1. Configuración de Flask
app = Flask(__name__)

# 2. Configuración de la Base de Datos (SQLite por ahora)
# Esto creará un archivo llamado "inventario.db" en tu carpeta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mi_clave_secreta_senati'

# Inicializamos la DB
db = SQLAlchemy(app)

# --- CONFIGURACIÓN DE LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Si no estás logueado, te manda aquí

# Esta función le dice a Flask cómo buscar al usuario en la BD
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# --- FUNCIÓN PARA LA HORA DE PERÚ ---
def obtener_hora_peru():
    lima = pytz.timezone('America/Lima')
    return datetime.now(lima)

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
    fecha = db.Column(db.DateTime, default=obtener_hora_peru)
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
    
    
    # Tabla 4: Usuarios (Para el Login)
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False) # Nombre único
    password_hash = db.Column(db.String(128)) # Guardaremos la clave encriptada, no en texto plano

    # Función para encriptar la clave
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Función para revisar si la clave es correcta
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

# --- RUTAS ---
@app.route('/')
def home():
    # En lugar de texto, ahora mostramos el archivo HTML
    return render_template('index.html')


# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, lo mandamos al inicio
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        user_form = request.form['username']
        pass_form = request.form['password']

        # Buscamos al usuario en la BD
        usuario = Usuario.query.filter_by(username=user_form).first()

        # Verificamos si existe y si la clave es correcta
        if usuario and usuario.check_password(pass_form):
            login_user(usuario) # <--- AQUÍ INICIA LA SESIÓN (Cookies)
            flash(f'Bienvenido {usuario.username}', 'success')
            
            # Si intentó entrar a una pagina protegida, lo devolvemos ahí
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required # Solo puedes salir si ya entraste
def logout():
    logout_user() # <--- CIERRA LA SESIÓN
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))


# --- RUTA DE INVENTARIO ---
@app.route('/productos', methods=['GET', 'POST'])
@login_required
def gestionar_productos():
    # 1. ESTO SE QUEDA IGUAL (Guardar producto nuevo)
    if request.method == 'POST':
        nombre_form = request.form['nombre']
        precio_form = float(request.form['precio'])
        stock_form = int(request.form['stock'])

        nuevo_producto = Producto(nombre=nombre_form, precio=precio_form, stock=stock_form)
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado correctamente', 'success')
        return redirect(url_for('gestionar_productos'))

    
    page = request.args.get('page', 1, type=int)
    cant_por_pagina = 10 # Mostraremos 10 productos por vez

    query_busqueda = request.args.get('q') # Captura el buscador
    
    if query_busqueda:
        # Filtramos Y paginamos
        pagination = Producto.query.filter(Producto.nombre.contains(query_busqueda)).paginate(page=page, per_page=cant_por_pagina, error_out=False)
    else:
        # Solo paginamos todo
        pagination = Producto.query.paginate(page=page, per_page=cant_por_pagina, error_out=False)
        
    
    return render_template('productos.html', pagination=pagination)


# --- RUTA DE VENTAS ---
@app.route('/vender', methods=['GET', 'POST'])
@login_required
def registrar_venta():
    # Si enviaron el formulario (POST)
    if request.method == 'POST':
        producto_id = int(request.form['producto_id'])
        cantidad = int(request.form['cantidad'])

        # 1. Buscar el producto en la BD
        producto = Producto.query.get_or_404(producto_id)

        # 2. VALIDACIÓN: ¿Hay suficiente stock?
        if cantidad > producto.stock:
            flash(f'Error: No hay suficiente stock. Solo quedan {producto.stock}.', 'danger')
            return redirect(url_for('registrar_venta'))

        # 3. CALCULAR TOTAL
        total_venta = producto.precio * cantidad

        # 4. LOGICA TRANSACCIONAL (Atomocidad)
        try:
            # A. Crear la cabecera de la venta
            nueva_venta = Venta(total=total_venta)
            db.session.add(nueva_venta)
            db.session.commit() # Guardamos para generar el ID de venta

            # B. Crear el detalle
            detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            db.session.add(detalle)

            # C. RESTAR STOCK (Lo más importante)
            producto.stock = producto.stock - cantidad

            # D. Guardar todos los cambios
            db.session.commit()
            
            flash(f'¡Venta exitosa! Total: S/. {total_venta}', 'success')

        except Exception as e:
            db.session.rollback() # Si algo falla, deshacer todo
            flash('Hubo un error al procesar la venta.', 'danger')

        return redirect(url_for('registrar_venta'))

    # Si es GET (Solo ver la página)
    lista_productos = Producto.query.all()
    return render_template('vender.html', productos=lista_productos)


# --- RUTA DE HISTORIAL ---
@app.route('/historial')
@login_required
def ver_historial():
    # Consultamos todas las ventas ordenadas por fecha (descendente)
    # Venta.query.order_by(Venta.fecha.desc()) es SQL traducido a Python
    ventas_realizadas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('historial.html', ventas=ventas_realizadas)


# --- RUTA ELIMINAR PRODUCTO  ---
@app.route('/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    # 1. Buscamos el producto
    producto = Producto.query.get_or_404(id)
    
    try:
        db.session.query(DetalleVenta).filter(DetalleVenta.producto_id == id).delete()
        
        # 2. Ahora sí, borramos el producto
        db.session.delete(producto)
        
        # 3. Guardamos los cambios
        db.session.commit()
        
        flash('Producto y su historial eliminados correctamente.', 'success')
        
    except Exception as e:
        db.session.rollback() # Si falla, deshacemos
        print(f"Error detectado: {e}") # Mira la terminal si sale error
        flash(f'Error al eliminar: {e}', 'danger')

    return redirect(url_for('gestionar_productos'))


# --- RUTA EDITAR PRODUCTO ---
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)

    if request.method == 'POST':
        # Actualizamos los datos con lo que viene del formulario
        producto.nombre = request.form['nombre']
        producto.precio = float(request.form['precio'])
        producto.stock = int(request.form['stock'])

        try:
            db.session.commit()
            flash('Producto actualizado con éxito.', 'success')
            return redirect(url_for('gestionar_productos'))
        except:
            flash('Error al actualizar el producto.', 'danger')
            return redirect(url_for('gestionar_productos'))

    # Si es GET, mostramos el formulario con los datos actuales
    return render_template('editar_producto.html', producto=producto)


# --- RUTA EXPORTAR EXCEL ---
@app.route('/exportar_excel')
@login_required
def exportar_excel():
    # 1. Consultamos todas las ventas
    ventas = Venta.query.all()
    
    # 2. Transformamos los datos a una lista de diccionarios
    datos_lista = []
    for v in ventas:
        datos_lista.append({
            'ID Boleta': v.id,
            'Fecha': v.fecha.strftime('%d/%m/%Y %H:%M'),
            'Total (S/.)': v.total
        })
    
    # 3. Creamos un DataFrame de Pandas (Una tabla virtual)
    df = pd.DataFrame(datos_lista)
    
    # 4. Guardamos en memoria (buffer) en vez de crear un archivo físico
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Ventas')
    
    output.seek(0)
    
    # 5. Enviamos el archivo al navegador
    return send_file(output, download_name="reporte_ventas.xlsx", as_attachment=True)


# --- API PARA EL GRÁFICO (Datos JSON) ---
@app.route('/api/datos_grafico')
@login_required
def datos_grafico():
    # Traemos todos los productos
    productos = Producto.query.all()
    
    # Creamos dos listas vacías
    nombres = []
    stocks = []
    
    # Llenamos las listas con los datos reales
    for p in productos:
        nombres.append(p.nombre)
        stocks.append(p.stock)
        
    # Enviamos los datos en formato JSON (JavaScript Object Notation)
    return jsonify({'nombres': nombres, 'stocks': stocks})


# Arrancar
if __name__ == '__main__':
    app.run(debug=True)