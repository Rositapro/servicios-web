import os
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header, Response, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Servicio de Facturación e Inventario - Python (FastAPI + SOAP)",
    description="Microservicio desarrollado en Python para la Práctica de Servicios Web (RESTful + SOAP).",
    version="1.0.0"
)

# Habilitar CORS para consumo desde dashboard web u otros clientes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base de datos en memoria compartida
products_db = [
    {"id": 1, "code": "PROD001", "name": "Laptop ThinkPad E14", "category": "Computación", "price": 15500.0, "stock": 12},
    {"id": 2, "code": "PROD002", "name": "Monitor Dell 27 4K", "category": "Periféricos", "price": 6200.0, "stock": 25},
    {"id": 3, "code": "PROD003", "name": "Teclado Mecánico RGB", "category": "Accesorios", "price": 1350.0, "stock": 40},
    {"id": 4, "code": "PROD004", "name": "Mouse Inalámbrico Logitech", "category": "Accesorios", "price": 650.0, "stock": 50},
    {"id": 5, "code": "PROD005", "name": "Impresora Multifuncional HP", "category": "Oficina", "price": 4100.0, "stock": 8}
]

invoices_db = []

VALID_REST_TOKEN = "bearer-token-unit5-secret-key-2026"
VALID_SOAP_TOKEN = "SOAP-SECRET-KEY-2026"

# Modelos Pydantic para REST
class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="password123")

class LoginResponse(BaseModel):
    token: str
    token_type: str = "Bearer"
    user: str

class ProductModel(BaseModel):
    code: str = Field(..., example="PROD006")
    name: str = Field(..., example="Disco SSD NVMe 1TB")
    category: str = Field(..., example="Almacenamiento")
    price: float = Field(..., gt=0, example=1850.0)
    stock: int = Field(..., ge=0, example=30)

class ProductResponse(ProductModel):
    id: int

class InvoiceItem(BaseModel):
    productCode: str = Field(..., example="PROD001")
    quantity: int = Field(..., gt=0, example=2)

class CreateInvoiceRequest(BaseModel):
    customerName: str = Field(..., example="Comercializadora del Norte S.A.")
    items: List[InvoiceItem]

# Autenticación REST
def verify_rest_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabecera Authorization no provista"
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or parts[1] != VALID_REST_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer inválido o expirado"
        )
    return parts[1]

# ==================== ENDPOINTS REST ====================

@app.post("/api/auth/login", response_model=LoginResponse, tags=["Autenticación"])
def login(creds: LoginRequest):
    if creds.username == "admin" and creds.password == "password123":
        return LoginResponse(token=VALID_REST_TOKEN, user=creds.username)
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@app.get("/api/products", response_model=List[ProductResponse], tags=["Productos (REST)"])
def get_products(category: Optional[str] = None, search: Optional[str] = None):
    results = products_db
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    if search:
        s = search.lower()
        results = [p for p in results if s in p["name"].lower() or s in p["code"].lower()]
    return results

@app.get("/api/products/{product_id}", response_model=ProductResponse, tags=["Productos (REST)"])
def get_product(product_id: int):
    prod = next((p for p in products_db if p["id"] == product_id), None)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

@app.post("/api/products", response_model=ProductResponse, status_code=201, tags=["Productos (REST)"])
def create_product(product: ProductModel, token: str = Depends(verify_rest_token)):
    if any(p["code"].upper() == product.code.upper() for p in products_db):
        raise HTTPException(status_code=400, detail="El código de producto ya existe")
    new_id = max((p["id"] for p in products_db), default=0) + 1
    new_prod = {"id": new_id, **product.model_dump()}
    products_db.append(new_prod)
    return new_prod

@app.put("/api/products/{product_id}", response_model=ProductResponse, tags=["Productos (REST)"])
def update_product(product_id: int, product: ProductModel, token: str = Depends(verify_rest_token)):
    prod = next((p for p in products_db if p["id"] == product_id), None)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    prod.update(product.model_dump())
    return prod

@app.delete("/api/products/{product_id}", tags=["Productos (REST)"])
def delete_product(product_id: int, token: str = Depends(verify_rest_token)):
    global products_db
    prod = next((p for p in products_db if p["id"] == product_id), None)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    products_db = [p for p in products_db if p["id"] != product_id]
    return {"message": f"Producto con ID {product_id} eliminado exitosamente"}

@app.post("/api/invoices", status_code=201, tags=["Facturación (REST)"])
def create_invoice(invoice_req: CreateInvoiceRequest, token: str = Depends(verify_rest_token)):
    subtotal = 0.0
    items_detail = []
    
    # Validar existencias y calcular
    for item in invoice_req.items:
        prod = next((p for p in products_db if p["code"].upper() == item.productCode.upper()), None)
        if not prod:
            raise HTTPException(status_code=404, detail=f"Producto {item.productCode} no encontrado")
        if prod["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {prod['name']}. Disponible: {prod['stock']}")
        
        line_total = prod["price"] * item.quantity
        subtotal += line_total
        items_detail.append({
            "productCode": prod["code"],
            "productName": prod["name"],
            "unitPrice": prod["price"],
            "quantity": item.quantity,
            "subtotal": line_total
        })

    # Descontar stock
    for item in invoice_req.items:
        prod = next(p for p in products_db if p["code"].upper() == item.productCode.upper())
        prod["stock"] -= item.quantity

    tax = round(subtotal * 0.16, 2)
    total = round(subtotal + tax, 2)
    invoice_number = f"FAC-PY-{len(invoices_db) + 1:04d}"

    invoice_record = {
        "id": len(invoices_db) + 1,
        "invoiceNumber": invoice_number,
        "customerName": invoice_req.customerName,
        "date": datetime.now().isoformat(),
        "items": items_detail,
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "total": total,
        "status": "EMITIDA"
    }
    invoices_db.append(invoice_record)
    return invoice_record

@app.get("/api/invoices", tags=["Facturación (REST)"])
def list_invoices():
    return invoices_db

@app.get("/api/invoices/{invoice_id}", tags=["Facturación (REST)"])
def get_invoice(invoice_id: int):
    inv = next((i for i in invoices_db if i["id"] == invoice_id), None)
    if not inv:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return inv

# ==================== ENDPOINT SOAP Y WSDL ====================

WSDL_PATH = os.path.join(os.path.dirname(__file__), "FacturacionService.wsdl")

def make_soap_fault(fault_code: str, fault_string: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>{fault_code}</faultcode>
      <faultstring>{fault_string}</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>"""

@app.get("/ws/FacturacionService", tags=["Servicio SOAP"])
def get_wsdl(wsdl: Optional[str] = None):
    if os.path.exists(WSDL_PATH):
        with open(WSDL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "<error>WSDL file not found</error>"
    return Response(content=content, media_type="text/xml; charset=utf-8")

@app.post("/ws/FacturacionService", tags=["Servicio SOAP"])
async def handle_soap(request: Request):
    body = await request.body()
    try:
        root = ET.fromstring(body)
    except Exception as e:
        return Response(content=make_soap_fault("Client.InvalidXML", f"XML malformado: {str(e)}"), media_type="text/xml; charset=utf-8", status_code=500)

    # Validar autenticación SOAP Header
    # Busca <AuthToken> o <wsse:Password>
    auth_token = None
    for elem in root.iter():
        if elem.tag.endswith("AuthToken"):
            auth_token = elem.text.strip() if elem.text else ""
            break
        elif elem.tag.endswith("Password"):
            auth_token = elem.text.strip() if elem.text else ""
            break

    if not auth_token or (auth_token != VALID_SOAP_TOKEN and auth_token != "password123"):
        fault_xml = make_soap_fault("Client.AuthenticationFailed", "Autenticacion SOAP fallida: Token de seguridad no valido o ausente en el encabezado")
        return Response(content=fault_xml, media_type="text/xml; charset=utf-8", status_code=401)

    # Identificar la operación solicitada
    soap_body = None
    for child in root:
        if child.tag.endswith("Body"):
            soap_body = child
            break

    if soap_body is None or len(soap_body) == 0:
        return Response(content=make_soap_fault("Client.EmptyBody", "Cuerpo SOAP vacio"), media_type="text/xml; charset=utf-8", status_code=500)

    op_elem = soap_body[0]
    tag_name = op_elem.tag.split("}")[-1] if "}" in op_elem.tag else op_elem.tag

    # 1. Operación GetProductStock
    if tag_name == "GetProductStockRequest":
        prod_code = ""
        for c in op_elem:
            if c.tag.endswith("ProductCode"):
                prod_code = c.text.strip() if c.text else ""
        prod = next((p for p in products_db if p["code"].upper() == prod_code.upper()), None)
        if prod:
            resp_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Body>
    <tns:GetProductStockResponse>
      <tns:ProductCode>{prod['code']}</tns:ProductCode>
      <tns:ProductName>{prod['name']}</tns:ProductName>
      <tns:Stock>{prod['stock']}</tns:Stock>
      <tns:Price>{prod['price']}</tns:Price>
      <tns:Available>{'true' if prod['stock'] > 0 else 'false'}</tns:Available>
    </tns:GetProductStockResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
        else:
            resp_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Body>
    <tns:GetProductStockResponse>
      <tns:ProductCode>{prod_code}</tns:ProductCode>
      <tns:ProductName>NO EXISTE</tns:ProductName>
      <tns:Stock>0</tns:Stock>
      <tns:Price>0.0</tns:Price>
      <tns:Available>false</tns:Available>
    </tns:GetProductStockResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
        return Response(content=resp_xml, media_type="text/xml; charset=utf-8")

    # 2. Operación CalculateInvoice
    elif tag_name == "CalculateInvoiceRequest":
        subtotal = 0.0
        count = 0
        for item in op_elem.iter():
            if item.tag.endswith("Item"):
                p_code = ""
                qty = 0
                for f in item:
                    if f.tag.endswith("ProductCode") and f.text:
                        p_code = f.text.strip()
                    elif f.tag.endswith("Quantity") and f.text:
                        qty = int(f.text.strip())
                prod = next((p for p in products_db if p["code"].upper() == p_code.upper()), None)
                if prod:
                    subtotal += prod["price"] * qty
                    count += qty

        tax = round(subtotal * 0.16, 2)
        total = round(subtotal + tax, 2)
        resp_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Body>
    <tns:CalculateInvoiceResponse>
      <tns:Subtotal>{round(subtotal, 2)}</tns:Subtotal>
      <tns:Tax>{tax}</tns:Tax>
      <tns:Total>{total}</tns:Total>
      <tns:ItemsCount>{count}</tns:ItemsCount>
    </tns:CalculateInvoiceResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
        return Response(content=resp_xml, media_type="text/xml; charset=utf-8")

    # 3. Operación ProcessInvoice
    elif tag_name == "ProcessInvoiceRequest":
        cust_name = "Cliente General"
        items_req = []
        for c in op_elem:
            if c.tag.endswith("CustomerName") and c.text:
                cust_name = c.text.strip()
        
        for item in op_elem.iter():
            if item.tag.endswith("Item"):
                p_code = ""
                qty = 0
                for f in item:
                    if f.tag.endswith("ProductCode") and f.text:
                        p_code = f.text.strip()
                    elif f.tag.endswith("Quantity") and f.text:
                        qty = int(f.text.strip())
                if p_code and qty > 0:
                    items_req.append((p_code, qty))

        subtotal = 0.0
        for p_code, qty in items_req:
            prod = next((p for p in products_db if p["code"].upper() == p_code.upper()), None)
            if not prod:
                return Response(content=make_soap_fault("Client.ProductNotFound", f"Producto {p_code} no existe"), media_type="text/xml; charset=utf-8", status_code=500)
            if prod["stock"] < qty:
                return Response(content=make_soap_fault("Client.InsufficientStock", f"Stock insuficiente para {prod['name']}"), media_type="text/xml; charset=utf-8", status_code=500)
            subtotal += prod["price"] * qty

        # Descontar stock
        for p_code, qty in items_req:
            prod = next(p for p in products_db if p["code"].upper() == p_code.upper())
            prod["stock"] -= qty

        tax = round(subtotal * 0.16, 2)
        total = round(subtotal + tax, 2)
        inv_num = f"FAC-SOAP-PY-{len(invoices_db) + 1:04d}"
        
        invoices_db.append({
            "id": len(invoices_db) + 1,
            "invoiceNumber": inv_num,
            "customerName": cust_name,
            "date": datetime.now().isoformat(),
            "total": total,
            "status": "EMITIDA"
        })

        resp_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Body>
    <tns:ProcessInvoiceResponse>
      <tns:InvoiceNumber>{inv_num}</tns:InvoiceNumber>
      <tns:CustomerName>{cust_name}</tns:CustomerName>
      <tns:Total>{total}</tns:Total>
      <tns:Status>PROCESADA_EXITOSA</tns:Status>
      <tns:Message>Factura generada e inventario actualizado correctamente</tns:Message>
    </tns:ProcessInvoiceResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
        return Response(content=resp_xml, media_type="text/xml; charset=utf-8")

    return Response(content=make_soap_fault("Client.UnknownOperation", f"Operacion desconocida: {tag_name}"), media_type="text/xml; charset=utf-8", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8082, reload=False)
