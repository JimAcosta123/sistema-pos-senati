# 🛒 Sistema Mini-POS (Punto de Venta e Inventario)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=for-the-badge&logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

> Proyecto final de carrera para la gestión optimizada de ventas e inventarios en pequeños negocios. Desarrollado con arquitectura MVC y lógica transaccional robusta.

---

## 📋 Características Principales

Este sistema no es un simple CRUD. Incluye lógica de negocio real:

* **🔐 Seguridad Robusta:** Sistema de Login y Autenticación con Hashing de contraseñas (`Werkzeug` + `Flask-Login`). Protege rutas críticas contra accesos no autorizados.
* **📦 Gestión de Inventario Inteligente:**
    * Control de stock en tiempo real.
    * **Paginación de productos** para manejar grandes volúmenes de datos.
    * Buscador dinámico integrado.
    * Validación de integridad referencial (no permite vender si no hay stock).
* **💰 Punto de Venta (POS):**
    * Interfaz rápida para registrar ventas.
    * Cálculo automático de totales.
    * Descuento automático de stock tras cada transacción (ACID compliancy).
* **📊 Reportes y Métricas:**
    * **Dashboard Visual:** Gráficos estadísticos con `Chart.js` para visualizar el estado del stock.
    * **Exportación Empresarial:** Generación de reportes detallados en **Excel** (`Pandas`) para contabilidad.
    * Historial de transacciones con hora local (Zona Horaria Perú).

---

## 🛠️ Stack Tecnológico

| Área | Tecnología | Uso |
| :--- | :--- | :--- |
| **Backend** | Python + Flask | Lógica del servidor y enrutamiento. |
| **Base de Datos** | SQLite + SQLAlchemy | Persistencia de datos y ORM Relacional. |
| **Frontend** | HTML5 + Jinja2 | Motor de plantillas dinámicas. |
| **Estilos** | Bootstrap 5 | Diseño responsivo y componentes UI. |
| **Scripts** | JavaScript + Chart.js | Interactividad y visualización de datos. |
| **Data Science** | Pandas | Procesamiento de datos para reportes Excel. |

---

## 🚀 Instalación y Despliegue

Sigue estos pasos para correr el proyecto en tu entorno local:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/JimAcosta123/sistema-pos-senati.git](https://github.com/JimAcosta123/sistema-pos-senati.git)
    cd sistema-pos-senati
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    source venv/Scripts/activate  # En Windows
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicializar Base de Datos (Seeding):**
    ```bash
    python semilla_productos.py  # Carga 50 productos de prueba
    python crear_admin.py        # Crea el usuario administrador
    ```

5.  **Ejecutar servidor:**
    ```bash
    python app.py
    ```

Visita `http://127.0.0.1:5000` en tu navegador.
* **Usuario:** `admin`
* **Clave:** `1234`

---

## 📷 Capturas de Pantalla

*(Espacio reservado para screenshots del sistema funcionando)*

---

**Desarrollado por:** Jim Acosta - Estudiante de Desarrollo de Software - SENATI.