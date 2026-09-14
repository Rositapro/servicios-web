#!/usr/bin/env python3
"""
Cliente Automatizado de Pruebas Multi-Servicio (RESTful + SOAP)
Ejecuta una batería exhaustiva de pruebas contra los 6 servicios web (Java, Python, PHP, Ruby, C#, VB.NET).
Utiliza únicamente librerías estándar de Python (urllib) para ejecutarse sin requerir dependencias externas.
"""

import urllib.request
import urllib.error
import json
import time
import sys

# Asegurar compatibilidad UTF-8 en terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SERVICES = [
    {"name": "Java (Jakarta REST / JAX-WS)", "lang": "Java", "port": 8081, "type": "Software Libre"},
    {"name": "Python (FastAPI / Spyne)", "lang": "Python", "port": 8082, "type": "Software Libre"},
    {"name": "PHP (Slim / SoapServer)", "lang": "PHP", "port": 8083, "type": "Software Libre"},
    {"name": "Ruby (Sinatra / SOAP)", "lang": "Ruby", "port": 8084, "type": "Software Libre"},
    {"name": "C# (ASP.NET Core / SoapCore)", "lang": "C#", "port": 8085, "type": "Propietario"},
    {"name": "VB.NET (ASP.NET Core / SoapCore)", "lang": "VB.NET", "port": 8086, "type": "Propietario"}
]

REST_TOKEN = "bearer-token-unit5-secret-key-2026"
SOAP_TOKEN = "SOAP-SECRET-KEY-2026"

def http_request(url, method="GET", headers=None, data=None, timeout=5):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        if isinstance(data, str):
            req.data = data.encode("utf-8")
        else:
            req.data = json.dumps(data).encode("utf-8")

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency_ms = int((time.time() - t0) * 1000)
            body = response.read().decode("utf-8")
            return response.status, body, latency_ms
    except urllib.error.HTTPError as e:
        latency_ms = int((time.time() - t0) * 1000)
        body = e.read().decode("utf-8") if e.fp else ""
        return e.code, body, latency_ms
    except Exception as e:
        return 0, str(e), 0

def test_service(service):
    port = service["port"]
    base_url = f"http://localhost:{port}"
    print(f"\n========================================================")
    print(f"🚀 Probando Nodo: {service['name']} en Puerto {port}")
    print(f"   Categoría: {service['type']}")
    print(f"========================================================")

    results = {
        "rest_get": False,
        "rest_auth": False,
        "rest_post": False,
        "rest_invoice": False,
        "soap_wsdl": False,
        "soap_stock": False,
        "soap_calc": False,
        "soap_fault": False,
        "avg_latency": 0
    }
    latencies = []

    # 1. REST: GET /api/products
    status, body, lat = http_request(f"{base_url}/api/products")
    latencies.append(lat)
    if status == 200 and "PROD001" in body:
        results["rest_get"] = True
        print(f"  [PASS] REST GET /api/products -> 200 OK ({lat}ms)")
    else:
        print(f"  [FAIL] REST GET /api/products -> Status {status}")

    # 2. REST: POST /api/auth/login
    status, body, lat = http_request(
        f"{base_url}/api/auth/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        data={"username": "admin", "password": "password123"}
    )
    latencies.append(lat)
    if status == 200 and "token" in body:
        results["rest_auth"] = True
        print(f"  [PASS] REST POST /api/auth/login -> 200 OK (Token generado) ({lat}ms)")
    else:
        print(f"  [FAIL] REST POST /api/auth/login -> Status {status}")

    # 3. REST: POST /api/products (Protegido)
    new_prod_code = f"TEST-{int(time.time()) % 10000}"
    status, body, lat = http_request(
        f"{base_url}/api/products",
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {REST_TOKEN}"},
        data={"code": new_prod_code, "name": "Producto Prueba CLI", "category": "Test", "price": 999.0, "stock": 50}
    )
    latencies.append(lat)
    if status in (200, 201) and new_prod_code in body:
        results["rest_post"] = True
        print(f"  [PASS] REST POST /api/products (Auth Bearer) -> {status} Created ({lat}ms)")
    else:
        print(f"  [FAIL] REST POST /api/products -> Status {status}")

    # 4. REST: POST /api/invoices (Protegido)
    status, body, lat = http_request(
        f"{base_url}/api/invoices",
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {REST_TOKEN}"},
        data={"customerName": "Cliente Auditoria CLI", "items": [{"productCode": "PROD001", "quantity": 1}]}
    )
    latencies.append(lat)
    if status in (200, 201) and ("FAC-" in body or "total" in body.lower()):
        results["rest_invoice"] = True
        print(f"  [PASS] REST POST /api/invoices (Facturación y Stock) -> {status} Created ({lat}ms)")
    else:
        print(f"  [FAIL] REST POST /api/invoices -> Status {status}")

    # 5. SOAP: GET WSDL
    status, body, lat = http_request(f"{base_url}/ws/FacturacionService?wsdl")
    latencies.append(lat)
    if status == 200 and ("<wsdl:definitions" in body or "<definitions" in body):
        results["soap_wsdl"] = True
        print(f"  [PASS] SOAP GET /ws/FacturacionService?wsdl -> 200 OK (WSDL válido) ({lat}ms)")
    else:
        print(f"  [FAIL] SOAP GET WSDL -> Status {status}")

    # 6. SOAP: POST GetProductStock con Header Válido
    soap_stock_req = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>{SOAP_TOKEN}</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  <soapenv:Body>
    <tns:GetProductStockRequest>
      <tns:ProductCode>PROD001</tns:ProductCode>
    </tns:GetProductStockRequest>
  </soapenv:Body>
</soapenv:Envelope>"""

    status, body, lat = http_request(
        f"{base_url}/ws/FacturacionService",
        method="POST",
        headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "http://facturacion.com/services/GetProductStock"},
        data=soap_stock_req
    )
    latencies.append(lat)
    if status == 200 and "GetProductStockResponse" in body and "ThinkPad" in body:
        results["soap_stock"] = True
        print(f"  [PASS] SOAP POST GetProductStock -> 200 OK (Respuesta XML procesada) ({lat}ms)")
    else:
        print(f"  [FAIL] SOAP POST GetProductStock -> Status {status}")

    # 7. SOAP: POST CalculateInvoice
    soap_calc_req = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>{SOAP_TOKEN}</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  <soapenv:Body>
    <tns:CalculateInvoiceRequest>
      <tns:CustomerName>Prueba CLI</tns:CustomerName>
      <tns:Items>
        <tns:Item>
          <tns:ProductCode>PROD001</tns:ProductCode>
          <tns:Quantity>2</tns:Quantity>
        </tns:Item>
      </tns:Items>
    </tns:CalculateInvoiceRequest>
  </soapenv:Body>
</soapenv:Envelope>"""

    status, body, lat = http_request(
        f"{base_url}/ws/FacturacionService",
        method="POST",
        headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "http://facturacion.com/services/CalculateInvoice"},
        data=soap_calc_req
    )
    latencies.append(lat)
    if status == 200 and "CalculateInvoiceResponse" in body:
        results["soap_calc"] = True
        print(f"  [PASS] SOAP POST CalculateInvoice -> 200 OK (Cálculo XML) ({lat}ms)")
    else:
        print(f"  [FAIL] SOAP POST CalculateInvoice -> Status {status}")

    # 8. SOAP: Seguridad (Token inválido esperando SOAP Fault 401)
    soap_fault_req = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>TOKEN_INVALIDO_TEST</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  <soapenv:Body>
    <tns:GetProductStockRequest>
      <tns:ProductCode>PROD001</tns:ProductCode>
    </tns:GetProductStockRequest>
  </soapenv:Body>
</soapenv:Envelope>"""

    status, body, lat = http_request(
        f"{base_url}/ws/FacturacionService",
        method="POST",
        headers={"Content-Type": "text/xml; charset=utf-8"},
        data=soap_fault_req
    )
    latencies.append(lat)
    if status == 401 and ("Fault" in body or "AuthenticationFailed" in body):
        results["soap_fault"] = True
        print(f"  [PASS] SOAP Seguridad (Token Inválido) -> 401 SOAP Fault Correcto ({lat}ms)")
    else:
        print(f"  [FAIL] SOAP Seguridad (Token Inválido) -> Status {status}")

    valid_lats = [l for l in latencies if l > 0]
    results["avg_latency"] = sum(valid_lats) // len(valid_lats) if valid_lats else 0
    return results

def main():
    print("\n" + "="*70)
    print("INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - UNIDAD 5")
    print("SERVICIOS WEB SOAP & RESTful (6 LENGUAJES)")
    print("="*70)

    summary = []
    for s in SERVICES:
        res = test_service(s)
        total_passed = sum(1 for k, v in res.items() if k != "avg_latency" and v is True)
        summary.append({
            "service": s["name"],
            "lang": s["lang"],
            "port": s["port"],
            "type": s["type"],
            "passed": total_passed,
            "total": 8,
            "avg_latency": res["avg_latency"]
        })

    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS E INTEROPERABILIDAD")
    print("="*80)
    print(f"{'Servicio / Lenguaje':<30} | {'Tipo':<16} | {'Puerto':<6} | {'Pruebas':<8} | {'Latencia':<8} | {'Resultado'}")
    print("-" * 80)

    all_ok = True
    for item in summary:
        status_str = "✅ 100% OK" if item["passed"] == item["total"] else f"⚠️ {item['passed']}/{item['total']}"
        if item["passed"] != item["total"]:
            all_ok = False
        print(f"{item['service']:<30} | {item['type']:<16} | {item['port']:<6} | {item['passed']}/{item['total']:<6} | {item['avg_latency']} ms{' ':<3} | {status_str}")

    print("="*80)
    if all_ok:
        print("🎉 ¡TODOS LOS SERVICIOS SUPERARON EL 100% DE LAS PRUEBAS DE REST Y SOAP!")
    else:
        print("Nota: Si algún servicio falló, verifica que los contenedores estén levantados con 'docker compose up -d'.")

if __name__ == "__main__":
    main()
