# Práctica de Servicios Web SOAP & RESTful (Unidad 5)

Sistema completo de servicios web heterogéneos desarrollados en **6 lenguajes de programación** (4 Software Libre y 2 Propietarios), orientados a un problema real de **Facturación e Inventario Comercial**.

---

## 🌐 Mapa de Puertos y Servicios Publicados

| Servicio | Lenguaje | Tipo | Tecnologías | Puerto Host | Documentación / WSDL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Java** | Java 21/25 | Software Libre | Jakarta REST / JAX-WS | `http://localhost:8081` | `/ws/FacturacionService?wsdl` |
| **Python** | Python 3.12/3.13 | Software Libre | FastAPI & Spyne | `http://localhost:8082` | `/docs` (Swagger) & `?wsdl` |
| **PHP** | PHP 8.2 | Software Libre | Slim & ext-soap | `http://localhost:8083` | `/ws/FacturacionService?wsdl` |
| **Ruby** | Ruby 3.2 | Software Libre | Sinatra & SOAP Server | `http://localhost:8084` | `/ws/FacturacionService?wsdl` |
| **C#** | C# (.NET 10) | Propietario | ASP.NET Core & SoapCore | `http://localhost:8085` | `/swagger` & `?wsdl` |
| **VB.NET** | VB.NET (.NET 10)| Propietario | ASP.NET Core & SoapCore | `http://localhost:8086` | `/swagger` & `?wsdl` |
| **Dashboard**| HTML5 / CSS / JS| Nginx | Cliente Unificado | `http://localhost:8080` | Panel Interactivo Principal |

---

## 🚀 Inicio Rápido (1 solo comando con Docker)

Para compilar y levantar todos los 6 servicios y el dashboard interactivo:

```powershell
docker compose up -d --build
```

Una vez que termine, abre tu navegador en:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 Ejecución de Pruebas

### 1. Cliente Automatizado en Python
Prueba de extremo a extremo (REST y SOAP en los 6 servicios con cálculo de latencias):
```powershell
python clients/python_client/test_all_services.py
```

### 2. Cliente en PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File clients/powershell_client/test_all.ps1
```

### 3. Pruebas con Postman
Importa el archivo en Postman:
- `testing_artifacts/ServiciosWeb_Unit5.postman_collection.json`

### 4. Pruebas con SoapUI
Abre SoapUI y selecciona *Import Project*:
- `testing_artifacts/SoapUI_Project_Unit5.xml`

### 5. Comandos cURL
Revisa la guía de comandos cURL listos para copiar y pegar:
- `testing_artifacts/curl_commands.md`

---

## 🔑 Credenciales y Tokens de Seguridad

- **RESTful:**
  - Login: `POST /api/auth/login` con `{"username": "admin", "password": "password123"}`
  - Token Bearer: `bearer-token-unit5-secret-key-2026`
  - Encabezado: `Authorization: Bearer bearer-token-unit5-secret-key-2026`
- **SOAP:**
  - Token XML: `SOAP-SECRET-KEY-2026`
  - Encabezado XML:
    ```xml
    <soapenv:Header>
      <tns:SecurityHeader>
        <tns:AuthToken>SOAP-SECRET-KEY-2026</tns:AuthToken>
      </tns:SecurityHeader>
    </soapenv:Header>
    ```

---

## 📚 Documentación Técnica Completa
Para el informe académico detallado con fundamentos teóricos, comparativa conceptual, matriz de rendimiento y justificación de arquitectura, consulta:
👉 **[DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md)**
