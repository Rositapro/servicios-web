# Guía de Comandos cURL para Pruebas de Servicios Web (Unidad 5)

Esta guía contiene comandos cURL listos para copiar y pegar en tu terminal (PowerShell, Bash o CMD) para probar tanto los endpoints RESTful como los servicios SOAP en los 6 lenguajes.

---

## 1. Pruebas de Servicios RESTful

### A. Autenticación y Obtención de Token Bearer
```bash
curl -X POST http://localhost:8082/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```
*Respuesta esperada:*
```json
{
  "token": "bearer-token-unit5-secret-key-2026",
  "token_type": "Bearer",
  "user": "admin"
}
```

### B. Listar Catálogo de Productos (GET)
Prueba en los diferentes puertos:
- Python: `8082`
- C#: `8085`
- VB.NET: `8086`
- Java: `8081`
- PHP: `8083`
- Ruby: `8084`

```bash
curl -X GET http://localhost:8082/api/products
```

### C. Crear Nuevo Producto (POST - Protegido con Bearer Token)
```bash
curl -X POST http://localhost:8082/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer bearer-token-unit5-secret-key-2026" \
  -d '{
    "code": "PROD006",
    "name": "Memoria RAM DDR5 32GB",
    "category": "Memorias",
    "price": 2400.00,
    "stock": 15
  }'
```

### D. Actualizar Producto Existente (PUT - Protegido)
```bash
curl -X PUT http://localhost:8082/api/products/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer bearer-token-unit5-secret-key-2026" \
  -d '{
    "code": "PROD001",
    "name": "Laptop ThinkPad E14 Gen 5 (Actualizada)",
    "category": "Computación",
    "price": 16500.00,
    "stock": 20
  }'
```

### E. Eliminar Producto (DELETE - Protegido)
```bash
curl -X DELETE http://localhost:8082/api/products/5 \
  -H "Authorization: Bearer bearer-token-unit5-secret-key-2026"
```

### F. Emitir Factura y Descontar Stock (POST - Protegido)
```bash
curl -X POST http://localhost:8082/api/invoices \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer bearer-token-unit5-secret-key-2026" \
  -d '{
    "customerName": "Comercializadora Industrial S.A.",
    "items": [
      { "productCode": "PROD001", "quantity": 2 },
      { "productCode": "PROD002", "quantity": 1 }
    ]
  }'
```

---

## 2. Pruebas de Servicios SOAP 1.1

### A. Descargar y Visualizar el Contrato WSDL
```bash
curl -X GET "http://localhost:8082/ws/FacturacionService?wsdl"
```

### B. Operación `GetProductStock` (Consulta de Inventario con Token SOAP)
```bash
curl -X POST http://localhost:8082/ws/FacturacionService \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H "SOAPAction: http://facturacion.com/services" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>SOAP-SECRET-KEY-2026</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  <soapenv:Body>
    <tns:GetProductStockRequest>
      <tns:ProductCode>PROD001</tns:ProductCode>
    </tns:GetProductStockRequest>
  </soapenv:Body>
</soapenv:Envelope>'
```

### C. Operación `CalculateInvoice` (Simulación de Cálculo con Impuestos)
```bash
curl -X POST http://localhost:8082/ws/FacturacionService \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H "SOAPAction: http://facturacion.com/services" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>SOAP-SECRET-KEY-2026</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  <soapenv:Body>
    <tns:CalculateInvoiceRequest>
      <tns:CustomerName>Constructora del Norte</tns:CustomerName>
      <tns:Items>
        <tns:Item>
          <tns:ProductCode>PROD001</tns:ProductCode>
          <tns:Quantity>2</tns:Quantity>
        </tns:Item>
      </tns:Items>
    </tns:CalculateInvoiceRequest>
  </soapenv:Body>
</soapenv:Envelope>'
```

### D. Operación `ProcessInvoice` (Emisión Formal y Actualización de Stock)
```bash
curl -X POST http://localhost:8082/ws/FacturacionService \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H "SOAPAction: http://facturacion.com/services" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>SOAP-SECRET-KEY-2026</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  <soapenv:Body>
    <tns:ProcessInvoiceRequest>
      <tns:CustomerName>Grupo Comercial del Centro S.A.</tns:CustomerName>
      <tns:Items>
        <tns:Item>
          <tns:ProductCode>PROD003</tns:ProductCode>
          <tns:Quantity>2</tns:Quantity>
        </tns:Item>
      </tns:Items>
    </tns:ProcessInvoiceRequest>
  </soapenv:Body>
</soapenv:Envelope>'
```

### E. Prueba de Seguridad: Token SOAP Inválido (SOAP Fault Esperado)
```bash
curl -X POST http://localhost:8082/ws/FacturacionService \
  -H "Content-Type: text/xml; charset=utf-8" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>TOKEN_ERRONEO</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  <soapenv:Body>
    <tns:GetProductStockRequest>
      <tns:ProductCode>PROD001</tns:ProductCode>
    </tns:GetProductStockRequest>
  </soapenv:Body>
</soapenv:Envelope>'
```
*Respuesta esperada: Código HTTP 401 con elemento `<soapenv:Fault>` y `<faultcode>Client.AuthenticationFailed</faultcode>`.*
