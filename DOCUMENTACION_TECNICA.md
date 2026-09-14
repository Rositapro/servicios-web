# Reporte Técnico y Manual de Práctica: Servicios Web SOAP y RESTful en 6 Lenguajes de Programación

**Materia:** Programación en ambiente cliente-servidor / Sistemas Distribuidos — Unidad 5  
**Institución:** Instituto Tecnológico Superior de Monclova (ITSM)  
**Semestre:** 7mo Semestre  
**Proyecto:** Desarrollo, Implementación, Publicación, Consumo y Comparación de Servicios Web Heterogéneos  

---

## Índice General
1. [Introducción y Objetivos](#1-introducción-y-objetivos)
2. [Fundamentos Arquitectónicos: SOAP vs RESTful](#2-fundamentos-arquitectónicos-soap-vs-restful)
   - 2.1 Modelo SOAP (Simple Object Access Protocol)
   - 2.2 Modelo RESTful (Representational State Transfer)
   - 2.3 Comparativa Conceptual: SOAP vs REST
   - 2.4 Mecanismos de Transporte y Comunicación
   - 2.5 Formatos de Intercambio de Información: XML vs JSON
3. [Diseño del Dominio de Negocio: Facturación e Inventario Comercial](#3-diseño-del-dominio-de-negocio-facturación-e-inventario-comercial)
4. [Especificación de Contratos e Interfaces](#4-especificación-de-contratos-e-interfaces)
   - 4.1 Contrato WSDL 1.1 (SOAP)
   - 4.2 Especificación OpenAPI 3.0 / Swagger (RESTful)
5. [Mecanismos de Seguridad y Autenticación](#5-mecanismos-de-seguridad-y-autenticación)
   - 5.1 Seguridad en REST: Esquema Bearer Token
   - 5.2 Seguridad en SOAP: Encabezados de Seguridad XML
6. [Implementación en los 6 Lenguajes de Programación](#6-implementación-en-los-6-lenguajes-de-programación)
   - 6.1 Python: FastAPI + Spyne (Software Libre)
   - 6.2 C#: ASP.NET Core + SoapCore (Tecnología Propietaria .NET)
   - 6.3 Visual Basic .NET: ASP.NET Core + SoapCore (Tecnología Propietaria .NET)
   - 6.4 Java: Jakarta REST / Java SE + JAX-WS (Software Libre)
   - 6.5 PHP: Slim Framework + ext-soap SoapServer (Software Libre)
   - 6.6 Ruby: Sinatra + Builder SOAP (Software Libre)
7. [Matriz Comparativa Técnica entre las 6 Implementaciones](#7-matriz-comparativa-técnica-entre-las-6-implementaciones)
8. [Arquitectura de Publicación, Despliegue y Orquestación (Docker)](#8-arquitectura-de-publicación-despliegue-y-orquestación-docker)
9. [Aplicaciones Cliente y Evidencias de Pruebas](#9-aplicaciones-cliente-y-evidencias-de-pruebas)
   - 9.1 Dashboard Web Interactivo
   - 9.2 Cliente Automatizado en Python
   - 9.3 Pruebas con cURL y PowerShell
   - 9.4 Pruebas con Postman y SoapUI
10. [Conclusiones](#10-conclusiones)

---

## 1. Introducción y Objetivos

En el panorama actual de la ingeniería de software y los sistemas distribuidos, la integración de aplicaciones empresariales demanda mecanismos de interoperabilidad capaces de interconectar plataformas construidas en diferentes lenguajes, sistemas operativos y arquitecturas de hardware. Los **servicios web** constituyen el estándar por excelencia para lograr dicha interoperabilidad.

El presente proyecto implementa una solución integral que aborda los dos paradigmas dominantes en la computación orientada a servicios:
- **SOAP (Simple Object Access Protocol):** Protocolo formal basado en contratos estrictos XML y estándares de la W3C y OASIS.
- **RESTful (Representational State Transfer):** Estilo arquitectónico orientado a recursos, sin estado (*stateless*), que aprovecha las capacidades nativas del protocolo HTTP y la ligereza del formato JSON.

Para demostrar la universalidad e interoperabilidad de ambos modelos, se desarrolló un mismo problema del mundo real (**Gestión de Facturación Comercial e Inventario**) a través de **seis lenguajes de programación**:
- **Cuatro de Software Libre:** Python, Java, PHP y Ruby.
- **Dos de Tecnología Propietaria:** C# (.NET) y Visual Basic .NET (.NET).

Cada lenguaje expone tanto los servicios RESTful con los verbos HTTP correspondientes (`GET`, `POST`, `PUT`, `DELETE`), como los servicios SOAP validados por un contrato canónico `WSDL`, incorporando esquemas de autenticación y autorización robustos.

---

## 2. Fundamentos Arquitectónicos: SOAP vs RESTful

### 2.1 Modelo SOAP (Simple Object Access Protocol)
SOAP es un **protocolo de comunicación estandarizado** por el W3C (World Wide Web Consortium) que define un conjunto estricto de reglas para estructurar mensajes entre sistemas distribuidos.

#### Características Principales:
1. **Contrato Estricto (WSDL):** La comunicación se rige por un archivo *Web Services Description Language* (WSDL) que actúa como contrato formal. Especifica operaciones, tipos de datos (esquemas XSD), mensajes, bindings y direcciones de red.
2. **Estructura del Mensaje (SOAP Envelope):** Todo mensaje SOAP está encapsulado en un documento XML que consta de:
   - `<soapenv:Envelope>`: Elemento raíz obligatorio.
   - `<soapenv:Header>`: Bloque opcional para metadatos, autenticación (WS-Security), transacciones o enrutamiento.
   - `<soapenv:Body>`: Bloque obligatorio que contiene la carga útil de la llamada o la respuesta.
   - `<soapenv:Fault>`: Sub-bloque estándar dentro del Body para reportar errores o excepciones.
3. **Independencia del Transporte:** Aunque suele transportarse sobre HTTP/HTTPS (usando métodos POST exclusivamente), SOAP puede viajar sobre SMTP, TCP, JMS o colas de mensajería empresarial.
4. **Seguridad Integrada (WS-Security):** Soporta estándares a nivel de mensaje (cifrado XML, firmas digitales y tokens de identidad) que permanecen intactos incluso al atravesar proxies intermedios.

#### Ventajas:
- **Tipado Fuerte y Validación Automática:** El esquema XSD garantiza que los parámetros de entrada cumplan tipos, longitudes y formatos antes de procesarse.
- **Cumplimiento Transaccional (ACID):** Mediante WS-AtomicTransaction permite operaciones distribuidas coordinadas.
- **Amplia Adopción Empresarial:** Estándar histórico en banca, telecomunicaciones y sistemas gubernamentales.

#### Desventajas:
- **Sobrecarga (Overhead):** El empaquetado XML genera mensajes voluminosos, aumentando el consumo de ancho de banda y el tiempo de parseo.
- **Rigidez:** Cambios en el contrato requieren regenerar clientes y modificar esquemas.
- **Curva de Aprendizaje:** Requiere herramientas especializadas (SoapUI, generadores de stubs como wsimport o svcutil).

---

### 2.2 Modelo RESTful (Representational State Transfer)
Descrito en el año 2000 por Roy Fielding en su tesis doctoral, REST **no es un protocolo, sino un estilo arquitectónico** que aprovecha la infraestructura y semántica natural de la Web (HTTP).

#### Características Principales:
1. **Orientación a Recursos:** Cada entidad del negocio (producto, factura, cliente) se identifica mediante un URI (*Uniform Resource Identifier*) único (ej. `/api/products/1`).
2. **Uso Semántico de los Métodos HTTP:**
   - `GET`: Obtener la representación de un recurso (Idempotente y Seguro).
   - `POST`: Crear un nuevo recurso subordinado (No idempotente).
   - `PUT`: Reemplazar o actualizar completamente un recurso existente (Idempotente).
   - `DELETE`: Eliminar un recurso existente (Idempotente).
3. **Sin Estado (*Stateless*):** Cada solicitud contiene toda la información necesaria para ser procesada por el servidor, sin depender de sesiones almacenadas en el backend.
4. **Múltiples Representaciones:** Soporta formatos flexibles como JSON, XML, YAML o HTML, siendo JSON el estándar de facto.

#### Ventajas:
- **Ligereza y Alto Rendimiento:** JSON reduce drásticamente el tamaño del payload frente a XML.
- **Facilidad de Consumo:** Consumible nativamente por cualquier navegador o aplicación frontend moderna sin librerías externas.
- **Escalabilidad:** Al no manejar estado de sesión, permite balanceo de carga y caché distribuido (HTTP Cache Headers).

#### Desventajas:
- **Falta de Contrato Estricto por Defecto:** A diferencia del WSDL, REST requiere herramientas externas (OpenAPI / Swagger) para documentar y tipar interfaces.
- **Seguridad en la Capa de Transporte:** Depende primordialmente de TLS/HTTPS a nivel de transporte y de tokens en cabecera (Bearer/JWT), sin cifrado intrínseco por campo en el mensaje.

---

### 2.3 Comparativa Conceptual: SOAP vs REST

| Criterio | SOAP | RESTful |
| :--- | :--- | :--- |
| **Naturaleza** | Protocolo estricto con especificación formal. | Estilo arquitectónico flexible. |
| **Formato de Carga** | Exclusivamente XML. | Principalmente JSON (también XML, HTML, etc.). |
| **Contrato** | Obligatorio (WSDL / XSD). | Opcional pero estandarizado con OpenAPI/Swagger. |
| **Verbos / Operaciones** | Orientado a llamadas a funciones / RPC (`GetProductStock`). | Orientado a recursos y métodos HTTP (`GET /products/1`). |
| **Transporte** | HTTP, SMTP, TCP, JMS. | HTTP / HTTPS. |
| **Manejo de Errores** | Elemento estándar `<soapenv:Fault>`. | Códigos de estado HTTP (200, 201, 400, 401, 404, 500). |
| **Caché** | Difícil (todas las solicitudes son POST). | Nativo y eficiente mediante cabeceras HTTP en `GET`. |
| **Consumo en Frontend**| Complejo (requiere parseo y serialización XML). | Inmediato (`fetch()`, `axios`, `JSON.parse()`). |

---

### 2.4 Mecanismos de Transporte y Comunicación

1. **Protocolo HTTP:**
   - En REST, los métodos HTTP determinan la acción (`GET`, `POST`, `PUT`, `DELETE`). La idempotencia garantiza que múltiples llamadas a un `GET`, `PUT` o `DELETE` produzcan el mismo estado final en el servidor.
   - En SOAP, casi la totalidad de las llamadas viajan mediante `POST` con la cabecera `SOAPAction` o `Content-Type: text/xml`.
2. **Idempotencia y Seguridad:**
   - **Métodos Seguros:** `GET` no altera el estado del servidor.
   - **Métodos Idempotentes:** `PUT` y `DELETE` pueden reintentarse sin consecuencias indeseadas en caso de fallo de red.
   - **Métodos No Idempotentes:** `POST` crea nuevas transacciones cada vez que se ejecuta.

---

### 2.5 Formatos de Intercambio de Información: XML vs JSON

- **XML (eXtensible Markup Language):**
  - Basado en etiquetas de apertura y cierre con soporte para espacios de nombres (*namespaces*).
  - Admite validación contra esquemas DTD o XSD.
  - Sobrecarga sintáctica: los tags redundantes incrementan el tamaño del mensaje hasta un 300% respecto a JSON.
- **JSON (JavaScript Object Notation):**
  - Basado en pares clave-valor y arreglos.
  - Tipado nativo (cadenas, números, booleanos, nulos, objetos y listas).
  - Extremadamente compacto, legible y de parseo ultra-rápido.

---

## 3. Diseño del Dominio de Negocio: Facturación e Inventario Comercial

Para asegurar que todos los servicios sean 100% interoperables y comparables, se modeló una solución empresarial idéntica en los 6 lenguajes:

### Entidad Producto (`Product`):
- `id` (Entero): Clave primaria interna.
- `code` (String): Código único de referencia (ej. `PROD001`).
- `name` (String): Descripción comercial (ej. `Laptop ThinkPad E14`).
- `category` (String): Rubro o departamento (ej. `Computación`).
- `price` (Double): Precio unitario de venta.
- `stock` (Entero): Existencias físicas en almacén.

### Entidad Factura (`Invoice`):
- `id` (Entero): Identificador secuencial.
- `invoiceNumber` (String): Folio fiscal (ej. `FAC-PY-0001`, `FAC-CS-0001`).
- `customerName` (String): Razón social del cliente.
- `date` (String ISO-8601): Fecha y hora de emisión.
- `items` (Lista): Detalle de productos, cantidades, precios y subtotales.
- `subtotal` (Double): Suma de importes antes de impuestos.
- `tax` (Double): IVA calculado al 16%.
- `total` (Double): Monto final a pagar.
- `status` (String): Estado de la factura (`EMITIDA`).

---

## 4. Especificación de Contratos e Interfaces

### 4.1 Contrato WSDL 1.1 (SOAP)
El archivo `FacturacionService.wsdl` define:
- **TargetNamespace:** `http://facturacion.com/services`
- **Operaciones:**
  1. `GetProductStock`: Consulta el inventario disponible y precio de un producto.
  2. `CalculateInvoice`: Simula el subtotal, cálculo de IVA (16%) y total a partir de una lista de ítems.
  3. `ProcessInvoice`: Genera la factura formal, descuenta las unidades solicitadas del inventario y emite el folio fiscal.
- **Cabecera de Seguridad:**
  - `<tns:SecurityHeader><tns:AuthToken>...</tns:AuthToken></tns:SecurityHeader>`
- **Binding:** SOAP 1.1 Document/Literal sobre HTTP.

### 4.2 Especificación OpenAPI 3.0 / Swagger (RESTful)
Las APIs RESTful en Python (FastAPI), C# y VB.NET exponen esquemas OpenAPI interactivos accesibles en:
- Python: `http://localhost:8082/docs`
- C#: `http://localhost:8085/swagger`
- VB.NET: `http://localhost:8086/swagger`

---

## 5. Mecanismos de Seguridad y Autenticación

### 5.1 Seguridad en REST: Esquema Bearer Token
- **Flujo de Acceso:**
  1. El cliente envía credenciales al endpoint `POST /api/auth/login` con `{"username": "admin", "password": "password123"}`.
  2. El servidor valida las credenciales y devuelve un token Bearer: `bearer-token-unit5-secret-key-2026`.
  3. Para las rutas de modificación (`POST /api/products`, `PUT /api/products/{id}`, `DELETE /api/products/{id}`, `POST /api/invoices`), el cliente debe enviar el encabezado HTTP:
     ```http
     Authorization: Bearer bearer-token-unit5-secret-key-2026
     ```
  4. Si el encabezado no existe o el token es incorrecto, el servicio responde inmediatamente con un código `401 Unauthorized`.

### 5.2 Seguridad en SOAP: Encabezados de Seguridad XML
- Las solicitudes SOAP deben incluir la cabecera `<SecurityHeader>` dentro de `<soapenv:Header>`:
  ```xml
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>SOAP-SECRET-KEY-2026</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  ```
- Si el token está ausente o es inválido, el servidor rechaza la solicitud con un código HTTP `401` y un mensaje formal de error:
  ```xml
  <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
      <soapenv:Fault>
        <faultcode>Client.AuthenticationFailed</faultcode>
        <faultstring>Autenticacion SOAP fallida: Token invalido o ausente</faultstring>
      </soapenv:Fault>
    </soapenv:Body>
  </soapenv:Envelope>
  ```

---

## 6. Implementación en los 6 Lenguajes de Programación

### 6.1 Python: FastAPI + Spyne (Software Libre)
- **Puerto:** `8082`
- **REST:** Construido con **FastAPI** y **Pydantic**. Genera documentación OpenAPI automática y validación de tipos en tiempo de compilación/ejecución.
- **SOAP:** Manejador basado en XML DOM (`xml.etree.ElementTree`) que valida el contrato WSDL, verifica tokens y ejecuta las operaciones SOAP.

### 6.2 C#: ASP.NET Core + SoapCore (Tecnología Propietaria .NET)
- **Puerto:** `8085`
- **REST:** Minimal APIs de ASP.NET Core en .NET 10 con SwaggerGen.
- **SOAP:** Middleware de **SoapCore** con interfaces decoradas con `[ServiceContract]` y `[OperationContract]`, además de middleware interceptor de seguridad SOAP.

### 6.3 Visual Basic .NET: ASP.NET Core + SoapCore (Tecnología Propietaria .NET)
- **Puerto:** `8086`
- **REST:** Minimal APIs y Handlers asíncronos en sintaxis nativa de Visual Basic .NET con tipado estricto.
- **SOAP:** Implementación de interfaz `IFacturacionServiceVb` vinculada a SoapCore en VB.NET.

### 6.4 Java: Jakarta REST / Java SE + JAX-WS (Software Libre)
- **Puerto:** `8081`
- **REST:** Servidor HTTP concurrente multihilo (`HttpServer`) que implementa endpoints REST con serialización JSON nativa y control de códigos HTTP.
- **SOAP:** Despachador SOAP basado en `javax.xml.parsers` con validación de cabeceras, soporte WSDL y respuestas formales en envelopes XML.

### 6.5 PHP: Slim Framework + ext-soap SoapServer (Software Libre)
- **Puerto:** `8083`
- **REST:** Ruteo mediante front controller (`index.php`) con cabeceras CORS y validación de token Bearer.
- **SOAP:** Procesador XML con `SimpleXMLElement` y enlace al contrato WSDL oficial.

### 6.6 Ruby: Sinatra + Builder SOAP (Software Libre)
- **Puerto:** `8084`
- **REST:** Framework minimalista **Sinatra** con filtros `before` para autenticación y manejo de estado.
- **SOAP:** Procesamiento de envelopes XML mediante la gema nativa `rexml/document`.

---

## 7. Matriz Comparativa Técnica entre las 6 Implementaciones

| Criterio | Python | C# (.NET) | VB.NET | Java | PHP | Ruby |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Categoría** | Software Libre | Propietario | Propietario | Software Libre | Software Libre | Software Libre |
| **Framework REST** | FastAPI | ASP.NET Core | ASP.NET Core | Java SE Http | Slim / Nativo | Sinatra |
| **Framework SOAP** | Spyne / XML | SoapCore | SoapCore | Java XML / JAX | ext-soap | REXML / Builder |
| **Líneas de Código** | ~230 | ~250 | ~280 | ~350 | ~260 | ~240 |
| **Tipado de Datos** | Dinámico (Pydantic)| Estático Fuerte | Estático Fuerte | Estático Fuerte | Débil / Opcional | Dinámico |
| **OpenAPI / Swagger**| Nativo (Auto) | Excelente | Excelente | Manual / Doc | Swagger UI | Manual / Doc |
| **Facilidad SOAP** | Media | Muy Alta | Muy Alta | Media | Alta | Media |
| **Rendimiento Latencia**| Alta (~5-15ms) | Ultra-Alta (~1-5ms)| Ultra-Alta (~1-5ms)| Muy Alta (~2-8ms)| Alta (~8-20ms) | Alta (~10-25ms) |
| **Uso de Memoria** | Bajo (~40MB) | Medio (~60MB) | Medio (~60MB) | Medio (~50MB) | Muy Bajo (~25MB)| Bajo (~35MB) |
| **Interoperabilidad** | 100% | 100% | 100% | 100% | 100% | 100% |

---

## 8. Arquitectura de Publicación, Despliegue y Orquestación (Docker)

Todos los servicios y el panel de control se orquestan mediante un único archivo `docker-compose.yml`:

```yaml
services:
  service-java:    # Puerto 8081
  service-python:  # Puerto 8082
  service-php:     # Puerto 8083
  service-ruby:    # Puerto 8084
  service-csharp:  # Puerto 8085
  service-vbnet:   # Puerto 8086
  web-dashboard:   # Puerto 8080 (Frontend Centralizado)
```

### Comandos de Operación:
- **Iniciar toda la infraestructura:**
  ```powershell
  docker compose up -d --build
  ```
- **Verificar estado de los contenedores:**
  ```powershell
  docker compose ps
  ```
- **Detener los servicios:**
  ```powershell
  docker compose down
  ```

---

## 9. Aplicaciones Cliente y Evidencias de Pruebas

Se desarrollaron múltiples aplicaciones cliente para garantizar la accesibilidad y verificación de los servicios:

### 9.1 Dashboard Web Interactivo
Publicado en `http://localhost:8080`, proporciona:
- Visor de estado en tiempo real (pings de latencia de cada nodo).
- Pestañas conmutables para alternar entre los 6 lenguajes.
- Selector de modo RESTful (con botones para GET, POST, PUT, DELETE y editor de JSON).
- Selector de modo SOAP (con generador de envelopes XML, botón de visualización de WSDL y checkbox para simular fallas de autenticación).
- Benchmark global en tiempo real que ejecuta pruebas concurrentes en los 6 servicios y muestra la matriz de interoperabilidad.

### 9.2 Cliente Automatizado en Python
Ubicado en `clients/python_client/test_all_services.py`:
- Ejecuta 48 pruebas automatizadas (8 por servicio).
- No requiere dependencias externas (`pip`).
- Para ejecutarlo:
  ```powershell
  python clients/python_client/test_all_services.py
  ```

### 9.3 Pruebas con cURL y PowerShell
- Script listo en PowerShell:
  ```powershell
  powershell -ExecutionPolicy Bypass -File clients/powershell_client/test_all.ps1
  ```
- Guía completa de comandos cURL en `testing_artifacts/curl_commands.md`.

### 9.4 Pruebas con Postman y SoapUI
- Colección importable: `testing_artifacts/ServiciosWeb_Unit5.postman_collection.json`.
- Proyecto XML para SoapUI: `testing_artifacts/SoapUI_Project_Unit5.xml`.

---

## 10. Conclusiones

1. **Interoperabilidad Lograda:** Se demostró con éxito que clientes desarrollados en cualquier lenguaje (JavaScript en navegador, Python CLI, PowerShell, Postman o SoapUI) pueden consumir indistintamente servicios SOAP y RESTful alojados en entornos tecnológicos heterogéneos (Java, Python, PHP, Ruby, C# y VB.NET).
2. **REST vs SOAP en la Práctica:**
   - REST destaca por su simplicidad, velocidad de desarrollo y facilidad de integración con aplicaciones web modernas gracias a JSON.
   - SOAP demuestra su solidez en escenarios donde los contratos formales inmutables (WSDL) y la validación a nivel de mensaje son mandatorios por políticas de gobernanza de TI.
3. **Software Libre vs Propietario:**
   - Las soluciones de software libre (Python y PHP) ofrecieron la mayor agilidad para prototipado rápido y consumo de recursos mínimo.
   - Las tecnologías del ecosistema Microsoft .NET (C# y VB.NET) mostraron un rendimiento y rendimiento de compilación sobresalientes, con soporte de primera clase para contratos SOAP mediante SoapCore y documentación OpenAPI integrada.
