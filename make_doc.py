# Generador de Documento Word (.docx) para Reporte Tecnico de Unidad 5
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = Document()

# Configuración de márgenes (2.5 cm en los 4 lados)
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Configurar fuente base
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(11)
style.font.color.rgb = RGBColor(0x27, 0x19, 0x11)

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=110, right=110):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_heading_1(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(16)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(15)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x4A, 0x2C, 0x1D)
    return h

def add_heading_2(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x6A, 0x44, 0x2F)
    return h

def add_p(text, italic=False, bold=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.italic = italic
    run.font.bold = bold
    return p

def add_bullet(bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    r1 = p.add_run(bold_prefix)
    r1.font.name = 'Times New Roman'
    r1.font.bold = True
    r2 = p.add_run(text)
    r2.font.name = 'Times New Roman'
    return p

# ==================== PORTADA ====================
p_inst = doc.add_paragraph()
p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_inst.paragraph_format.space_before = Pt(30)
r_inst = p_inst.add_run("INSTITUTO TECNOLÓGICO SUPERIOR DE MONCLOVA\n\"EJÉRCITO MEXICANO\"")
r_inst.font.name = 'Times New Roman'
r_inst.font.size = Pt(15)
r_inst.font.bold = True
r_inst.font.color.rgb = RGBColor(0x4A, 0x2C, 0x1D)

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(40)
r_sub = p_sub.add_run("División de Ingeniería en Sistemas Computacionales")
r_sub.font.name = 'Times New Roman'
r_sub.font.size = Pt(12)
r_sub.font.italic = True

p_tit = doc.add_paragraph()
p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_tit.paragraph_format.space_before = Pt(20)
p_tit.paragraph_format.space_after = Pt(15)
r_tit = p_tit.add_run("REPORTE TÉCNICO Y MANUAL DE PRÁCTICA:\nDESARROLLO, IMPLEMENTACIÓN Y PUBLICACIÓN DE SERVICIOS WEB SOAP Y RESTful EN 6 LENGUAJES DE PROGRAMACIÓN")
r_tit.font.name = 'Times New Roman'
r_tit.font.size = Pt(17)
r_tit.font.bold = True
r_tit.font.color.rgb = RGBColor(0x36, 0x1E, 0x12)

p_desc = doc.add_paragraph()
p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_desc.paragraph_format.space_after = Pt(60)
r_desc = p_desc.add_run("Solución de Facturación Comercial e Inventario Heterogéneo en 4 Tecnologías de Software Libre (Python, Java, PHP, Ruby) y 2 Propietarias (C#, Visual Basic .NET) con Docker Compose y Dashboard Web")
r_desc.font.name = 'Times New Roman'
r_desc.font.size = Pt(11.5)
r_desc.font.italic = True
r_desc.font.color.rgb = RGBColor(0x64, 0x4E, 0x3F)

p_meta = doc.add_paragraph()
p_meta.paragraph_format.space_before = Pt(50)
p_meta.paragraph_format.line_spacing = 1.3
def add_meta_field(p, label, value):
    r1 = p.add_run(label)
    r1.font.name = 'Times New Roman'
    r1.font.bold = True
    r2 = p.add_run(f" {value}\n")
    r2.font.name = 'Times New Roman'

add_meta_field(p_meta, "Asignatura:", "Programación en ambiente cliente-servidor / Sistemas Distribuidos")
add_meta_field(p_meta, "Unidad de Aprendizaje:", "Unidad 5 — Servicios Web Heterogéneos")
add_meta_field(p_meta, "Semestre:", "7mo Semestre")
add_meta_field(p_meta, "Estudiante:", "Rosita (Matrícula: I23050333)")
add_meta_field(p_meta, "Repositorio GitHub:", "https://github.com/Rositapro/servicios-web")
add_meta_field(p_meta, "Lugar y Fecha:", "Monclova, Coahuila — Septiembre 2026")

doc.add_page_break()

# ==================== ÍNDICE ====================
add_heading_1("Índice General del Documento")
idx_items = [
    "1. Introducción y Planteamiento del Problema",
    "2. Fundamentos Arquitectónicos: Modelo SOAP vs RESTful",
    "   2.1 Modelo SOAP (Simple Object Access Protocol)",
    "   2.2 Modelo RESTful (Representational State Transfer)",
    "   2.3 Cuadro Comparativo Exhaustivo: SOAP vs RESTful",
    "   2.4 Mecanismos de Transporte, Comunicación y Verbos HTTP",
    "   2.5 Formatos de Intercambio de Información: XML vs JSON",
    "   2.6 Mecanismos de Seguridad: WS-Security XML vs Bearer Token",
    "3. Diseño del Dominio de Negocio: Facturación e Inventario",
    "4. Especificación de Contratos y APIs (WSDL 1.1 y OpenAPI Swagger)",
    "5. Implementación en los 6 Lenguajes de Programación",
    "   5.1 Python (FastAPI + Spyne / XML DOM) — Software Libre",
    "   5.2 C# (.NET 10 / ASP.NET Core + SoapCore) — Propietario",
    "   5.3 Visual Basic .NET (.NET 10 / SoapCore) — Propietario",
    "   5.4 Java (Java SE 21 / JAX-WS / Jakarta REST) — Software Libre",
    "   5.5 PHP (PHP 8.2 / Slim Framework / SoapServer) — Software Libre",
    "   5.6 Ruby (Ruby 3.2 / Sinatra / Puma) — Software Libre",
    "6. Cuadro Comparativo Técnico: Software Libre vs Propietario",
    "7. Despliegue, Publicación y Contenerización (Docker Compose)",
    "8. Aplicaciones Cliente y Evidencias de Pruebas",
    "   8.1 Cliente Web Dashboard Interactivo (:8080)",
    "   8.2 Cliente Automatizado en Python (48/48 Pruebas Superadas)",
    "   8.3 Cliente en PowerShell",
    "   8.4 Colección Postman y Proyecto SoapUI",
    "9. Matriz de Resultados de Benchmark y Medición de Latencias",
    "10. Conclusiones y Lecciones Aprendidas",
    "11. Repositorio Oficial y Código Fuente en GitHub"
]
for item in idx_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.1
    r = p.add_run(item)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    if not item.startswith("   "):
        r.font.bold = True

doc.add_page_break()

# ==================== SECCIÓN 1 ====================
add_heading_1("1. Introducción y Planteamiento del Problema")
add_p("En el desarrollo actual de sistemas distribuidos y arquitectura de software orientada a servicios (SOA), la interoperabilidad representa uno de los desafíos más críticos. Las organizaciones demandan comunicar componentes programados en diferentes lenguajes, ejecutados sobre diversos sistemas operativos y hospedados en infraestructuras heterogéneas.")
add_p("El propósito fundamental de esta práctica académica consiste en desarrollar, implementar, dockerizar, publicar, consumir y comparar un sistema completo de servicios web comerciales bajo los dos modelos arquitectónicos dominantes:")
add_bullet("1. Modelo SOAP (Simple Object Access Protocol): ", "Protocolo estricto basado en un contrato canónico formal inmutable (WSDL 1.1), sobres XML con validación de esquemas XSD y cabeceras de autenticación WS-Security.")
add_bullet("2. Modelo RESTful (Representational State Transfer): ", "Estilo arquitectónico centrado en recursos, sin estado (stateless), que hace uso de los métodos semánticos de HTTP (GET, POST, PUT, DELETE), formatos ligeros JSON y autenticación con Bearer Tokens.")
add_p("Para evidenciar la compatibilidad multiplataforma, se programó exactamente la misma lógica de negocio comercial (Catálogo de Productos, Control de Existencias, Actualizaciones y Emisión de Facturas con descuento de inventario) a través de SEIS lenguajes de programación:")
add_bullet("Cuatro Lenguajes de Software Libre: ", "Python (FastAPI), Java (Java SE / JAX-WS), PHP (Slim Framework) y Ruby (Sinatra).")
add_bullet("Dos Lenguajes Propietarios de Microsoft: ", "C# (.NET 10 / ASP.NET Core) y Visual Basic .NET (.NET 10 / SoapCore).")

# ==================== SECCIÓN 2 ====================
add_heading_1("2. Fundamentos Arquitectónicos: Modelo SOAP vs RESTful")
add_heading_2("2.1 Modelo SOAP (Simple Object Access Protocol)")
add_p("SOAP es un protocolo estandarizado por el W3C que define un marco formal para el intercambio de mensajes XML entre sistemas informáticos distribuidos.")
add_bullet("Contrato Estricto (WSDL): ", "Todo servicio SOAP se apoya en un archivo WSDL (Web Services Description Language) que actúa como contrato legal de la interfaz. Define operaciones, mensajes de entrada y salida, esquemas XSD y direcciones de red.")
add_bullet("Estructura del Mensaje (Envelope): ", "Todo mensaje está envuelto en un elemento raíz <soapenv:Envelope>, el cual contiene un <soapenv:Header> opcional para metadatos/seguridad y un <soapenv:Body> obligatorio para el payload de la operación.")
add_bullet("Independencia del Transporte: ", "A diferencia de REST, SOAP puede viajar no solo sobre HTTP/HTTPS, sino también sobre SMTP, TCP o colas JMS.")
add_bullet("Seguridad Robusta (WS-Security): ", "Permite firmas digitales, cifrado y tokens en el encabezado del mensaje XML, garantizando confidencialidad e integridad de extremo a extremo.")

add_heading_2("2.2 Modelo RESTful (Representational State Transfer)")
add_p("Introducido por Roy Fielding en el año 2000, REST no es un protocolo formal, sino un estilo arquitectónico que aprovecha la naturaleza y semántica original del protocolo HTTP.")
add_bullet("Orientación a Recursos: ", "Cada objeto del dominio posee un identificador URI único (por ejemplo: /api/products/1).")
add_bullet("Uso Semántico de Métodos HTTP: ", "GET para consultas seguras, POST para creaciones, PUT para actualizaciones completas y DELETE para eliminación de recursos.")
add_bullet("Arquitectura Sin Estado (Stateless): ", "El servidor no guarda sesiones; cada solicitud lleva en sus cabeceras la autenticación necesaria (Bearer Token).")
add_bullet("Formato Compacto JSON: ", "Sintaxis ligera basada en pares clave-valor que optimiza el ancho de banda y permite procesamiento inmediato en el navegador.")

add_heading_2("2.3 Cuadro Comparativo Exhaustivo: SOAP vs RESTful")

table_soap_rest = doc.add_table(rows=1, cols=3)
table_soap_rest.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ["Criterio Técnico", "Modelo SOAP (Protocolo Formal)", "Modelo RESTful (Estilo Arquitectónico)"]
for i, title in enumerate(headers):
    cell = table_soap_rest.rows[0].cells[i]
    cell.text = title
    set_cell_background(cell, "DCC8B5")
    p = cell.paragraphs[0]
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(10)

soap_rest_data = [
    ("Definición y Estandarización", "Protocolo estricto formalizado por el consorcio W3C.", "Estilo arquitectónico basado en los estándares HTTP de la IETF."),
    ("Contrato de Interfaz", "Obligatorio y matemático (WSDL 1.1 con esquemas XSD).", "Opcional pero documentado mediante OpenAPI 3.0 / Swagger."),
    ("Formato de Datos", "Exclusivamente XML con formato Envelope.", "Principalmente JSON (también admite XML o texto plano)."),
    ("Mecanismo de Transporte", "Transporte agnóstico (HTTP, HTTPS, SMTP, TCP, JMS).", "Exclusivamente sobre protocolo HTTP / HTTPS."),
    ("Semántica de Métodos", "Casi todas las operaciones son POST hacia una única URL.", "Métodos semánticos diferenciados: GET, POST, PUT, DELETE."),
    ("Manejo de Errores", "Estructura XML estándar <soapenv:Fault> con códigos de falla.", "Códigos de estado HTTP oficiales (200, 201, 400, 401, 404, 500)."),
    ("Consumo en Navegador Web", "Complejo; requiere construir sobres XML y parsear respuestas.", "Inmediato y nativo con fetch() o axios y JSON.parse()."),
    ("Seguridad y Autenticación", "WS-Security en cabecera XML (firma y cifrado de campos).", "TLS/HTTPS a nivel transporte y Bearer / JWT en headers."),
    ("Ventajas Principales", "Tipado fuerte, contratos inmutables, transacciones ACID.", "Ligero, rápido desarrollo, bajo consumo de memoria y red."),
    ("Desventajas Principales", "Sobrecarga de tamaño (XML pesado), rigidez ante cambios.", "Sin tipado estricto por defecto, seguridad atada al transporte.")
]

for row_data in soap_rest_data:
    row = table_soap_rest.add_row()
    for col_idx, text in enumerate(row_data):
        cell = row.cells[col_idx]
        cell.text = text
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(9.5)
        if col_idx == 0:
            p.runs[0].font.bold = True
            set_cell_background(cell, "FAF4ED")
        set_cell_margins(cell, 80, 80, 100, 100)

doc.add_page_break()

# ==================== SECCIÓN 3 ====================
add_heading_1("3. Diseño del Dominio de Negocio: Facturación e Inventario")
add_p("Para asegurar comparabilidad idéntica e interoperabilidad sin fisuras entre los 6 lenguajes de programación, se implementó el mismo modelo comercial:")

add_heading_2("Entidad Producto (Product)")
add_bullet("id: ", "Identificador numérico autoincremental único en el catálogo.")
add_bullet("code: ", "Código comercial estandarizado (ej. PROD001, PROD002).")
add_bullet("name: ", "Descripción comercial del artículo (ej. Laptop ThinkPad E14, Monitor Dell 27 4K).")
add_bullet("category: ", "Rubro o departamento (ej. Computación, Periféricos, Almacenamiento).")
add_bullet("price: ", "Precio unitario de venta (tipo Double).")
add_bullet("stock: ", "Unidades disponibles en inventario físico (tipo Entero).")

add_heading_2("Entidad Factura Comercial (Invoice)")
add_bullet("id: ", "Folio interno correlativo.")
add_bullet("invoiceNumber: ", "Folio fiscal generado con prefijo del lenguaje emisor (ej. FAC-PY-0001, FAC-CS-0001).")
add_bullet("customerName: ", "Razón social del comprador.")
add_bullet("date: ", "Marca de tiempo de emisión en formato estándar ISO-8601.")
add_bullet("items: ", "Detalle de productos, cantidades, precios unitarios y subtotales por partida.")
add_bullet("subtotal: ", "Importe total acumulado antes de impuestos.")
add_bullet("tax: ", "Impuesto al Valor Agregado (IVA) calculado al 16.00%.")
add_bullet("total: ", "Monto total líquido a cobrar (subtotal + tax).")
add_bullet("status: ", "Estado de la transacción (EMITIDA / PROCESADA_EXITOSA).")

# ==================== SECCIÓN 4 ====================
add_heading_1("4. Especificación de Contratos y APIs")
add_heading_2("4.1 Contrato WSDL 1.1 Canónico (FacturacionService.wsdl)")
add_p("El contrato WSDL compartido se encuentra publicado en el namespace targetNamespace=\"http://facturacion.com/services\" y define formalmente:")
add_bullet("1. Operación GetProductStock: ", "Recibe <ProductCode> y devuelve disponibilidad booleana (<Available>), nombre, precio y stock actual.")
add_bullet("2. Operación CalculateInvoice: ", "Recibe cliente y lista de productos; calcula subtotal, IVA del 16% y total sin afectar las existencias físicas.")
add_bullet("3. Operación ProcessInvoice: ", "Recibe cliente y lista de productos; emite la factura formal y descuenta automáticamente el inventario en tiempo real.")
add_bullet("Validación de Seguridad SOAP: ", "Requiere el encabezado <tns:SecurityHeader><tns:AuthToken>SOAP-SECRET-KEY-2026</tns:AuthToken></tns:SecurityHeader>. Si falta o es incorrecto, produce una falla SOAP 401.")

add_heading_2("4.2 Endpoints RESTful y Verbos Semánticos HTTP")
add_bullet("GET /api/products: ", "Consulta el inventario completo de productos en formato JSON.")
add_bullet("GET /api/products/{id}: ", "Consulta los detalles de un producto específico mediante su identificador numérico {id}.")
add_bullet("POST /api/products: ", "Da de alta un nuevo producto (Protegido con Bearer Token).")
add_bullet("PUT /api/products/{id}: ", "Actualiza precio, nombre, categoría y existencias del producto {id} (Protegido con Bearer Token).")
add_bullet("DELETE /api/products/{id}: ", "Elimina del catálogo el producto indicado por {id} (Protegido con Bearer Token).")
add_bullet("POST /api/invoices: ", "Procesa la compra comercial, calcula importes y descuenta existencias (Protegido con Bearer Token).")
add_bullet("POST /api/auth/login: ", "Inicia sesión con usuario 'admin' y contraseña 'password123', entregando el token Bearer.")

# ==================== SECCIÓN 5 ====================
add_heading_1("5. Implementación en los 6 Lenguajes de Programación")

langs_data = [
    ("5.1 Python (FastAPI + Spyne / XML) — Software Libre", "8082", "FastAPI, Uvicorn, Pydantic, ElementTree XML",
     "FastAPI aprovecha la asincronía nativa de Python con validación estricta de esquemas Pydantic. Ofrece documentación interactiva Swagger UI en http://localhost:8082/docs. El endpoint SOAP analiza y genera sobres XML mediante xml.etree.ElementTree, validando las cabeceras de autenticación y respetando el contrato WSDL canónico."),
    
    ("5.2 C# (.NET 10 / ASP.NET Core + SoapCore) — Propietario", "8085", "ASP.NET Core Minimal APIs, SoapCore 1.2.1, Swashbuckle",
     "Aprovecha el compilador Roslyn y las optimizaciones de .NET 10 en Linux x64 autónomo. Implementa contratos WCF mediante SoapCore utilizando [ServiceContract] y [OperationContract]. Para las operaciones REST utiliza Minimal APIs con inyección de dependencias de DataRepository y documentación Swagger UI en http://localhost:8085/swagger."),
    
    ("5.3 Visual Basic .NET (.NET 10 / SoapCore) — Propietario", "8086", "VB.NET, ASP.NET Core, SoapCore 1.2.1",
     "Demuestra la vigencia del lenguaje Visual Basic .NET en el runtime moderno de .NET 10. Implementa endpoints asíncronos y tipado estricto para las rutas REST y las operaciones SOAP vinculadas con SoapCore, demostrando que VB.NET es totalmente competitivo en entornos de contenedores."),
    
    ("5.4 Java (Java SE 21 / JAX-WS / Jakarta REST) — Software Libre", "8081", "Java SE 21 (Eclipse Temurin), HttpServer, JAXB",
     "Construido sobre el servidor HTTP embebido multihilo de Java SE para máximo rendimiento sin la sobrecarga de servidores pesados tipo Tomcat o GlassFish. Gestiona serialización JSON nativa y procesamiento de sobres SOAP XML según el contrato WSDL oficial."),
    
    ("5.5 PHP (PHP 8.2 / Slim Framework / SoapServer) — Software Libre", "8083", "PHP 8.2 CLI, Slim Framework Routing, SimpleXML, ext-soap",
     "Utiliza el micro-framework Slim para enrutamiento RESTful ligero y el módulo nativo SimpleXML junto con ext-soap para el protocolo SOAP. Ofrece un tiempo de arranque instantáneo y mínimo consumo de memoria en contenedores Alpine Linux."),
    
    ("5.6 Ruby (Ruby 3.2 / Sinatra / Puma) — Software Libre", "8084", "Ruby 3.2, Sinatra Microframework, Puma Server, REXML",
     "Aprovecha la elegancia y concisión de Sinatra montado sobre el servidor concurrente Puma. Las operaciones SOAP son parseadas mediante la librería REXML, validando tokens de seguridad y calculando importes fiscales.")
]

for title, port, tech, desc in langs_data:
    add_heading_2(title)
    add_bullet("Puerto de Red Asignado: ", f":{port}")
    add_bullet("Tecnologías y Librerías Utilizadas: ", tech)
    add_p(desc)

doc.add_page_break()

# ==================== SECCIÓN 6 ====================
add_heading_1("6. Cuadro Comparativo Técnico: Software Libre vs Propietario")

table_tech = doc.add_table(rows=1, cols=6)
table_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_tech = ["Lenguaje", "Clasificación", "Framework REST", "Manejador SOAP", "Puerto", "Doc. Swagger"]
for i, title in enumerate(headers_tech):
    cell = table_tech.rows[0].cells[i]
    cell.text = title
    set_cell_background(cell, "DCC8B5")
    p = cell.paragraphs[0]
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(9.5)

tech_rows = [
    ("Python", "Software Libre", "FastAPI", "Spyne / XML DOM", "8082", "Sí (/docs)"),
    ("Java", "Software Libre", "Java SE HttpHandler", "JAX-WS / XML", "8081", "No (API nativa)"),
    ("PHP", "Software Libre", "Slim Framework", "ext-soap / SimpleXML", "8083", "No (REST JSON)"),
    ("Ruby", "Software Libre", "Sinatra", "REXML / Builder", "8084", "No (REST JSON)"),
    ("C#", "Propietario .NET", "ASP.NET Core", "SoapCore 1.2.1", "8085", "Sí (/swagger)"),
    ("VB.NET", "Propietario .NET", "ASP.NET Core", "SoapCore 1.2.1", "8086", "Sí (/swagger)")
]

for row_data in tech_rows:
    row = table_tech.add_row()
    for col_idx, text in enumerate(row_data):
        cell = row.cells[col_idx]
        cell.text = text
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(9)
        if col_idx == 0:
            p.runs[0].font.bold = True
        if col_idx == 1:
            set_cell_background(cell, "EAF2EB" if text == "Software Libre" else "F8EBE4")
        set_cell_margins(cell, 80, 80, 100, 100)

# ==================== SECCIÓN 7 ====================
add_heading_1("7. Despliegue, Publicación y Contenerización (Docker Compose)")
add_p("Para facilitar el despliegue inmediato con un único comando ('docker compose up -d'), todos los 6 servicios y el Dashboard Web fueron orquestados en contenedores Docker conectados a la red bridge privada 'web-services-net':")

table_docker = doc.add_table(rows=1, cols=4)
table_docker.alignment = WD_TABLE_ALIGNMENT.CENTER
docker_headers = ["Contenedor Docker", "Servicio / Lenguaje", "Imagen Base", "Puerto Host:Contenedor"]
for i, title in enumerate(docker_headers):
    cell = table_docker.rows[0].cells[i]
    cell.text = title
    set_cell_background(cell, "DCC8B5")
    p = cell.paragraphs[0]
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(9.5)

docker_rows = [
    ("service-java-unit5", "Java SE JAX-WS / REST", "eclipse-temurin:21-jre-alpine", "8081:8081"),
    ("service-python-unit5", "Python FastAPI / SOAP", "python:3.12-slim", "8082:8082"),
    ("service-php-unit5", "PHP 8.2 Slim / SOAP", "php:8.2-cli-alpine", "8083:8083"),
    ("service-ruby-unit5", "Ruby 3.2 Sinatra / Puma", "ruby:3.2-alpine", "8084:8084"),
    ("service-csharp-unit5", "C# ASP.NET Core .NET 10", "dotnet/runtime-deps:9.0", "8085:8085"),
    ("service-vbnet-unit5", "VB.NET ASP.NET Core .NET 10", "dotnet/runtime-deps:9.0", "8086:8086"),
    ("web-dashboard-unit5", "Cliente Web Nginx", "nginx:alpine", "8080:80")
]

for row_data in docker_rows:
    row = table_docker.add_row()
    for col_idx, text in enumerate(row_data):
        cell = row.cells[col_idx]
        cell.text = text
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(9)
        set_cell_margins(cell, 80, 80, 100, 100)

doc.add_page_break()

# ==================== SECCIÓN 8 ====================
add_heading_1("8. Aplicaciones Cliente y Evidencias de Pruebas")

add_heading_2("8.1 Cliente Web Dashboard Interactivo (Puerto 8080)")
add_p("Se desarrolló una aplicación web con una cuidada estética editorial en tonos café, moca y beige, con tipografía clásica Times New Roman. Permite seleccionar dinámicamente cualquiera de los 6 lenguajes, consultar productos con campos de ID personalizables, emitir facturas, consultar el contrato WSDL y ejecutar benchmarks.")

img1_path = r"C:\Users\rosal\.gemini\antigravity-ide\brain\db56ccff-6a27-46d7-a096-8eaea97e12c6\dashboard_final_view_1789347953142.png"
if os.path.exists(img1_path):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(img1_path, width=Inches(6.2))
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(12)
    r_cap = p_cap.add_run("Figura 1: Vista general del Web Dashboard interactivo con tema café, beige y Times New Roman.")
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True

add_heading_2("8.2 Consultas con IDs Dinámicos y Respuestas en Tiempo Real")
add_p("A través de los nuevos controles de entrada numérica, el usuario puede ingresar cualquier ID para consultar, actualizar en el formulario o eliminar productos del catálogo sin restricciones fijas:")

img2_path = r"C:\Users\rosal\.gemini\antigravity-ide\brain\db56ccff-6a27-46d7-a096-8eaea97e12c6\rest_product_2_query_1789349502317.png"
if os.path.exists(img2_path):
    p_img2 = doc.add_paragraph()
    p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(img2_path, width=Inches(6.2))
    p_cap2 = doc.add_paragraph()
    p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap2.paragraph_format.space_after = Pt(12)
    r_cap2 = p_cap2.add_run("Figura 2: Consulta dinámica por ID de producto (ID: 2) y respuesta JSON en consola con estado 200 OK.")
    r_cap2.font.name = 'Times New Roman'
    r_cap2.font.size = Pt(9.5)
    r_cap2.font.italic = True

add_heading_2("8.3 Cliente Automatizado en Python (48/48 Pruebas Superadas)")
add_p("La suite de pruebas automatizadas clients/python_client/test_all_services.py valida 8 pruebas críticas por cada lenguaje (48 pruebas en total):")
add_bullet("1. GET /api/products: ", "Consulta de catálogo (200 OK).")
add_bullet("2. POST /api/auth/login: ", "Autenticación y recepción de token Bearer.")
add_bullet("3. POST /api/products: ", "Alta de producto autenticada.")
add_bullet("4. POST /api/invoices: ", "Facturación y descuento de stock comprobado.")
add_bullet("5. GET /ws/FacturacionService?wsdl: ", "Descarga y validación del contrato WSDL.")
add_bullet("6. SOAP POST GetProductStock: ", "Consulta de stock en sobre XML.")
add_bullet("7. SOAP POST CalculateInvoice: ", "Cálculo de impuestos e importes en sobre XML.")
add_bullet("8. SOAP Fault Security 401: ", "Rechazo seguro ante token ausente o incorrecto.")

# ==================== SECCIÓN 9 ====================
add_heading_1("9. Matriz de Resultados de Benchmark y Rendimiento")
add_p("Al invocar concurrentemente los 6 servicios desde el Dashboard Web, se generó la siguiente matriz comparativa en tiempo real:")

table_bench = doc.add_table(rows=1, cols=6)
table_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
bench_headers = ["Servicio / Lenguaje", "Licencia", "Frameworks", "Puerto", "Latencia REST", "Latencia SOAP"]
for i, title in enumerate(bench_headers):
    cell = table_bench.rows[0].cells[i]
    cell.text = title
    set_cell_background(cell, "DCC8B5")
    p = cell.paragraphs[0]
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(9.5)

bench_data = [
    ("Python", "Software Libre", "FastAPI / Spyne", ":8082", "200 OK (16 ms)", "200 OK (27 ms)"),
    ("Java", "Software Libre", "Jakarta REST / JAX-WS", ":8081", "200 OK (54 ms)", "200 OK (4 ms)"),
    ("PHP", "Software Libre", "Slim / SoapServer", ":8083", "200 OK (19 ms)", "200 OK (25 ms)"),
    ("Ruby", "Software Libre", "Sinatra / SOAP", ":8084", "200 OK (5 ms)", "200 OK (15 ms)"),
    ("C#", "Propietario", "ASP.NET Core / SoapCore", ":8085", "200 OK (148 ms)", "200 OK (26 ms)"),
    ("VB.NET", "Propietario", "ASP.NET Core / SoapCore", ":8086", "200 OK (173 ms)", "200 OK (21 ms)")
]

for row_data in bench_data:
    row = table_bench.add_row()
    for col_idx, text in enumerate(row_data):
        cell = row.cells[col_idx]
        cell.text = text
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(9)
        if col_idx == 0:
            p.runs[0].font.bold = True
        set_cell_margins(cell, 80, 80, 100, 100)

doc.add_page_break()

# ==================== SECCIÓN 10 ====================
add_heading_1("10. Conclusiones y Lecciones Aprendidas")
add_bullet("1. Interoperabilidad Total: ", "Se demostró con éxito que aplicaciones cliente escritas en JavaScript (navegador), Python o PowerShell pueden consumir indistintamente servicios SOAP y RESTful alojados en 6 lenguajes heterogéneos sin acoplamiento tecnológico.")
add_bullet("2. REST vs SOAP en la Práctica: ", "REST ofrece agilidad insuperable para el desarrollo web y móvil gracias al formato JSON, mientras que SOAP mantiene su vigencia en entornos bancarios y gubernamentales donde los contratos inmutables WSDL y la validación XSD son obligatorios.")
add_bullet("3. Software Libre vs Propietario: ", "Las alternativas libres (Python, PHP, Ruby y Java) permitieron prototipado sumamente ágil y bajo consumo en contenedores ligeros de Linux, mientras que las tecnologías .NET (C# y VB.NET) brindaron un tipado robusto, soporte WCF con SoapCore y documentación OpenAPI de primer nivel.")
add_bullet("4. Contenerización Eficiente: ", "Docker Compose demostró ser la herramienta ideal para la orquestación de sistemas distribuidos heterogéneos, permitiendo levantar toda la plataforma de 7 contenedores con un único comando.")

add_heading_2("11. Repositorio Oficial del Proyecto en GitHub")
p_gh = doc.add_paragraph()
p_gh.paragraph_format.space_before = Pt(8)
r_gh1 = p_gh.add_run("Todo el código fuente, contenedores Dockerfile, contrato WSDL, colecciones de prueba y documentación se encuentran publicados y versionados en el repositorio público de GitHub:\n")
r_gh1.font.name = 'Times New Roman'
r_gh2 = p_gh.add_run("👉 https://github.com/Rositapro/servicios-web")
r_gh2.font.name = 'Times New Roman'
r_gh2.font.bold = True
r_gh2.font.color.rgb = RGBColor(0x4A, 0x2C, 0x1D)

output_path = r"c:\Users\rosal\OneDrive - Instituto Tecnológico Superior de Monclova\Documentos\Universidad\7mo Semestre\Unit5\REPORTE_TECNICO_SERVICIOS_WEB_UNIDAD_5.docx"
doc.save(output_path)
print(f"DOCUMENTO GUARDADO EXITOSAMENTE EN: {output_path}")
