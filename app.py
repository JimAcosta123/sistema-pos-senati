import pandas as pd
from flask import send_file
import io
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import requests
# --- NUEVAS IMPORTACIONES DE SEGURIDAD ---
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# 1. Configuración de Flask
app = Flask(__name__)
# --- FILTROS PERSONALIZADOS (Jinja2) ---
@app.template_filter('moneda')
def formato_moneda(valor):
    """Convierte un número en formato moneda Perú: S/. 10.50"""
    valor = float(valor)
    return "S/. {:,.2f}".format(valor)

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
# Modelo Venta Actualizado para Facturación
class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=obtener_hora_peru)
    total = db.Column(db.Float, default=0.0)
    
    # --- NUEVOS CAMPOS (Lo que pide el profesor) ---
    cliente_nombre = db.Column(db.String(100), nullable=True) # Nombre del cliente
    cliente_dni = db.Column(db.String(20), nullable=True)     # DNI o RUC
    serie = db.Column(db.String(20), nullable=True)           # Ej: F001
    correlativo = db.Column(db.String(20), nullable=True)     # Ej: 000023
    enlace_pdf = db.Column(db.String(200), nullable=True)     # Link a la factura (si dan)
    # -----------------------------------------------

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
    # Lógica de Negocio: Calcular métricas
    if current_user.is_authenticated:
        total_productos = Producto.query.count()
        productos_bajos = Producto.query.filter(Producto.stock < 5).count()
        # Sumar total de ventas (requiere importar func)
        from sqlalchemy import func
        total_ventas_dinero = db.session.query(func.sum(Venta.total)).scalar() or 0
    else:
        # Valores por defecto si no está logueado
        total_productos = 0
        productos_bajos = 0
        total_ventas_dinero = 0

    return render_template('index.html', 
                           total_productos=total_productos, 
                           bajos=productos_bajos, 
                           dinero=total_ventas_dinero)


# --- RUTA DE LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya entró, lo mandamos al inicio
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        # AQUÍ ESTABA EL ERROR: Antes tenías 'nombre', 'precio'...
        # AHORA SOLO PEDIMOS USUARIO Y CLAVE:
        user_form = request.form['username']
        pass_form = request.form['password']

        # Buscamos al usuario
        usuario = Usuario.query.filter_by(username=user_form).first()

        if usuario and usuario.check_password(pass_form):
            login_user(usuario)
            flash(f'Bienvenido {usuario.username}', 'success')
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
            print(f"ALERTA DE SEGURIDAD: Intento de venta sin stock. Prod: {producto.id}")
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
            
            
            
            # --- INTEGRACIÓN FACTURACIÓN (API PROFESOR) ---
            try:
                # 1. Capturamos datos del cliente del HTML
                nueva_venta.cliente_dni = request.form['cliente_dni']
                nueva_venta.cliente_nombre = request.form['cliente_nombre']

                # 2. Enviamos a la API
                # La función nos devuelve el número de factura y el nombre del archivo PDF
                numero_factura, nombre_archivo = enviar_factura_sunat(nueva_venta)

                if numero_factura:
                    # SI LA API RESPONDIÓ BIEN:
                    nueva_venta.serie = "F001"
                    nueva_venta.correlativo = numero_factura
                    # Armamos el link del PDF (basado en sistemas Pro7)
                    nueva_venta.enlace_pdf = f"https://cevicheria.pro7.uio.la/print/document/{nombre_archivo}/a4"
                    
                    flash(f'✅ ¡Venta guardada y Factura {numero_factura} generada!', 'success')
                else:
                    # SI LA API FALLÓ:
                    nueva_venta.serie = "ERROR"
                    flash('⚠️ Venta guardada localmente, pero falló la conexión con la Cevichería.', 'warning')

                # 3. Guardamos estos nuevos datos (serie, correlativo) en la BD
                db.session.commit()

            except Exception as e:
                print(f"Error crítico en facturación: {e}")
            # ----------------------------------------------
            
            
            
            
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


# --- RUTA VER BOLETA INDIVIDUAL ---
@app.route('/boleta/<int:id>')
@login_required
def ver_boleta(id):
    venta = Venta.query.get_or_404(id)
    return render_template('boleta.html', venta=venta)


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


# --- MANEJO DE ERRORES ---
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500


# --- MANEJO DE ERRORES PERSONALIZADO ---
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500

# --- RUTA DE INFORMACIÓN ---
@app.route('/acerca')
def acerca():
    return render_template('acerca.html')


# --- RUTA DE RESPALDO (BACKUP)
@app.route('/backup_db')
@login_required
def descargar_backup():
    # Agregamos 'instance/' a la ruta
    try:
        return send_file('instance/inventario.db', as_attachment=True, download_name="backup_inventario.sqlite")
    except FileNotFoundError:
        
        return send_file('inventario.db', as_attachment=True, download_name="backup_inventario.sqlite")


# --- FUNCIÓN DE FACTURACIÓN (API PROFESOR) ---
def enviar_factura_sunat(venta_obj):
    url_api = "https://cevicheria.pro7.uio.la/api/documents"
    token = "AzAloyc2q7Fy5aA3mEJdXAd6YP13QAaA11kHgfLwbjwx6KOA5z"

    # LÓGICA DNI/RUC
    dni_cliente = venta_obj.cliente_dni.strip()
    if len(dni_cliente) == 11:
        tipo_doc = "6" 
    elif len(dni_cliente) == 8:
        tipo_doc = "1"
    else:
        tipo_doc = "0"

    items = []
    for d in venta_obj.detalles:
        # Cálculos matemáticos
        # Asumimos que d.precio_unitario ya incluye el IGV (Precio Final)
        precio_final = float(d.precio_unitario)
        valor_unitario = precio_final / 1.18 # Valor sin impuestos
        igv_unitario = precio_final - valor_unitario
        
        items.append({
            "codigo_interno": f"P{d.producto.id}",
            "descripcion": d.producto.nombre,
            "codigo_producto_sunat": "",
            "unidad_de_medida": "NIU", # <--- EL GANADOR
            
            "cantidad": d.cantidad,
            "valor_unitario": round(valor_unitario, 2),
            
            "codigo_tipo_precio": "01", # <--- EL GANADOR
            "precio_unitario": round(precio_final, 2),
            
            "codigo_tipo_afectacion_igv": "10", # <--- EL GANADOR
            
            "total_base_igv": round(valor_unitario * d.cantidad, 2),
            "porcentaje_igv": 18.00,            # <--- EL GANADOR
            "total_igv": round(igv_unitario * d.cantidad, 2),
            "total_impuestos": round(igv_unitario * d.cantidad, 2),
            
            "total_valor_item": round(valor_unitario * d.cantidad, 2), # <--- EL GANADOR
            "total_item": round(precio_final * d.cantidad, 2)          # <--- EL GANADOR
        })

    # Totales Globales
    total_global = float(venta_obj.total)
    subtotal_global = total_global / 1.18
    igv_global = total_global - subtotal_global

    datos = {
        "serie_documento": "F001", 
        "numero_documento": "#", 
        "fecha_de_emision": venta_obj.fecha.strftime('%Y-%m-%d'),
        "hora_de_emision": venta_obj.fecha.strftime('%H:%M:%S'),
        "codigo_tipo_operacion": "0101", 
        "codigo_tipo_documento": "01", 
        "codigo_tipo_moneda": "PEN", 
        "fecha_de_vencimiento": venta_obj.fecha.strftime('%Y-%m-%d'),
        "datos_del_cliente_o_receptor": {
            "codigo_tipo_documento_identidad": tipo_doc,
            "numero_documento": dni_cliente,
            "apellidos_y_nombres_o_razon_social": venta_obj.cliente_nombre,
            "codigo_pais": "PE",
            "ubigeo": "150101",
            "direccion": "Lima, Peru",
            "correo_electronico": "",
            "telefono": ""
        },
        "totales": {
            "total_exportacion": 0.00,
            "total_operaciones_gravadas": round(subtotal_global, 2),
            "total_operaciones_inafectas": 0.00,
            "total_operaciones_exoneradas": 0.00,
            "total_operaciones_gratuitas": 0.00,
            "total_igv": round(igv_global, 2),
            "total_impuestos": round(igv_global, 2),
            "total_valor": round(subtotal_global, 2),
            "total_venta": round(total_global, 2)
        },
        "items": items
    }

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    try:
        print("📡 Enviando Factura Real a Cevichería...")
        r = requests.post(url_api, json=datos, headers=headers)
        print("📩 Respuesta:", r.text) 

        if r.status_code == 200:
            resp_json = r.json()
            if resp_json.get('success'):
                data_doc = resp_json.get('data', {})
                # Devolvemos: Serie-Numero, NombrePDF
                return data_doc.get('number'), data_doc.get('filename')
    except Exception as e:
        print("❌ Error:", e)
    
    return None, None





# Arrancar
if __name__ == '__main__':
    app.run(debug=True)