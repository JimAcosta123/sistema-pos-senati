import requests
import json
import random

# --- CONFIGURACIÓN ---
url = "https://cevicheria.pro7.uio.la/api/documents"
token = "AzAloyc2q7Fy5aA3mEJdXAd6YP13QAaA11kHgfLwbjwx6KOA5z"

codigo_random = f"TEST-{random.randint(10000, 99999)}"

payload = {
    "serie_documento": "F001",
    "numero_documento": "#",
    "fecha_de_emision": "2025-11-24",
    "hora_de_emision": "10:00:00",
    "codigo_tipo_operacion": "0101",
    "codigo_tipo_documento": "01",
    "codigo_tipo_moneda": "PEN",
    "fecha_de_vencimiento": "2025-11-24",
    "datos_del_cliente_o_receptor": {
        "codigo_tipo_documento_identidad": "6",
        "numero_documento": "20155945860",
        "apellidos_y_nombres_o_razon_social": "SENATI",
        "codigo_pais": "PE",
        "ubigeo": "150101",
        "direccion": "Av. Principal 123",
        "correo_electronico": "demo@gmail.com",
        "telefono": "427-1148"
    },
    "totales": {
        "total_exportacion": 0.00,
        "total_operaciones_gravadas": 100.00,
        "total_operaciones_inafectas": 0.00,
        "total_operaciones_exoneradas": 0.00,
        "total_operaciones_gratuitas": 0.00,
        "total_igv": 18.00,
        "total_impuestos": 18.00,
        "total_valor": 100.00,
        "total_venta": 118.00
    },
    "items": [
        {
            "codigo_interno": codigo_random,
            "descripcion": "Producto Manual Oficial",
            "codigo_producto_sunat": "", # Opcional según manual
            "unidad_de_medida": "NIU",   # <--- EL MANUAL PIDE ESTE NOMBRE EXACTO
            
            "cantidad": 1,
            "valor_unitario": 100.00,
            
            "codigo_tipo_precio": "01",        # <--- SEGÚN MANUAL
            "precio_unitario": 118.00,
            
            "codigo_tipo_afectacion_igv": "10", # <--- SEGÚN MANUAL (Gravado - Operación Onerosa)
            
            "total_base_igv": 100.00,
            "porcentaje_igv": 18.00,            # <--- SEGÚN MANUAL (No percentage_igv)
            "total_igv": 18.00,
            "total_impuestos": 18.00,
            
            "total_valor_item": 100.00,         # <--- SEGÚN MANUAL (No total_value)
            "total_item": 118.00                # <--- SEGÚN MANUAL (No total)
        }
    ]
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

print(f"📡 Enviando prueba MANUAL OFICIAL a Cevichería...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print("\n--- RESPUESTA DEL SERVIDOR ---")
    print(f"Código: {response.status_code}")
    print(f"Cuerpo: {response.text}")
except Exception as e:
    print("Error de conexión:", e)