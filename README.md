# 🛒 Sistema POS & Gestión de Inventario (Python/Flask)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=for-the-badge&logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

> **Proyecto Final de Carrera - SENATI**
> Sistema integral para la administración de ventas, control de stock y facturación en pequeños negocios. Desarrollado bajo arquitectura MVC y estándares de código limpio.

---

## 📋 Descripción del Proyecto

Este software soluciona el problema de la gestión manual en bodegas y tiendas minoristas. Permite digitalizar el inventario, automatizar el cálculo de ventas y generar reportes contables en tiempo real.

A diferencia de un CRUD básico, este sistema implementa **Lógica de Negocio Real**:
* Integridad referencial en base de datos.
* Validaciones de seguridad en backend.
* Auditoría de transacciones.
* Métricas visuales para toma de decisiones.

---

## 🌟 Características Principales

### 🔐 Módulo de Seguridad y Acceso
* **Autenticación Robusta:** Sistema de Login con `Flask-Login`.
* **Protección de Rutas:** Decoradores `@login_required` para bloquear accesos no autorizados.
* **Hashing de Contraseñas:** Encriptación segura con `Werkzeug`.

### 📦 Gestión de Inventario (WMS)
* **CRUD Completo:** Crear, Leer, Editar y Eliminar productos.
* **Búsqueda Inteligente:** Barra de búsqueda dinámica para filtrar productos.
* **Paginación:** Manejo eficiente de grandes volúmenes de datos (10 items por página).
* **Alertas de Stock:** Indicadores visuales automáticos para productos con bajo stock.

### 💰 Punto de Venta (POS)
* **Transacciones Atómicas:** Descuento automático de stock al confirmar una venta.
* **Validación de Integridad:** Bloqueo de ventas si el stock es insuficiente o negativo.
* **Ticket Digital:** Generación de boletas optimizadas para impresión térmica (CSS Print Media).

### 📊 Reportes y Analítica
* **Dashboard Ejecutivo:** Gráficos interactivos con **Chart.js** (Niveles de stock).
* **Exportación de Datos:** Generación de reportes en **Excel (.xlsx)** usando `Pandas` para contabilidad.
* **KPIs en Tiempo Real:** Tarjetas con métricas de ventas totales y productos críticos.

### 🛠️ Utilidades del Sistema
* **Copias de Seguridad:** Botón para descarga directa del backup de la base de datos (`.db`).
* **Manejo de Errores:** Pantallas personalizadas para errores 404 y 500.

---

## 💻 Stack Tecnológico

| Capa | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Backend** | Python + Flask | Núcleo de la aplicación y API interna. |
| **Base de Datos** | SQLite + SQLAlchemy | Persistencia relacional y ORM. |
| **Frontend** | HTML5 + Jinja2 | Motor de plantillas y estructura semántica. |
| **Estilos** | Bootstrap 5 | Diseño responsivo y componentes UI modernos. |
| **Scripting** | JavaScript (Chart.js) | Visualización de datos y gráficos. |
| **Data Science** | Pandas / OpenPyXL | Procesamiento de datos para exportación. |

---

## 🚀 Instalación y Despliegue

Sigue estos pasos para ejecutar el proyecto en tu entorno local:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/JimAcosta123/sistema-pos-senati.git](https://github.com/JimAcosta123/sistema-pos-senati.git)
cd sistema-pos-senati