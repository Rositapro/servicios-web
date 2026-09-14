require 'sinatra'
require 'json'
require 'rexml/document'
require 'rack/cors'

set :port, 8084
set :bind, '0.0.0.0'

use Rack::Cors do
  allow do
    origins '*'
    resource '*', headers: :any, methods: [:get, :post, :put, :delete, :options]
  end
end

VALID_REST_TOKEN = "bearer-token-unit5-secret-key-2026"
VALID_SOAP_TOKEN = "SOAP-SECRET-KEY-2026"

products_db = [
  { id: 1, code: "PROD001", name: "Laptop ThinkPad E14", category: "Computación", price: 15500.0, stock: 12 },
  { id: 2, code: "PROD002", name: "Monitor Dell 27 4K", category: "Periféricos", price: 6200.0, stock: 25 },
  { id: 3, code: "PROD003", name: "Teclado Mecánico RGB", category: "Accesorios", price: 1350.0, stock: 40 },
  { id: 4, code: "PROD004", name: "Mouse Inalámbrico Logitech", category: "Accesorios", price: 650.0, stock: 50 },
  { id: 5, code: "PROD005", name: "Impresora Multifuncional HP", category: "Oficina", price: 4100.0, stock: 8 }
]

invoices_db = []

helpers do
  def authenticate_rest!
    auth = request.env['HTTP_AUTHORIZATION']
    if auth.nil? || auth.empty?
      halt 401, { 'Content-Type' => 'application/json' }, { error: 'Cabecera Authorization no provista' }.to_json
    end
    parts = auth.split(' ')
    if parts.length != 2 || parts[0].downcase != 'bearer' || parts[1] != VALID_REST_TOKEN
      halt 401, { 'Content-Type' => 'application/json' }, { error: 'Token Bearer inválido o expirado' }.to_json
    end
  end
end

# ==================== ENDPOINT SOAP ====================

get '/ws/FacturacionService' do
  content_type 'text/xml; charset=utf-8'
  wsdl_path = File.join(File.dirname(__FILE__), 'FacturacionService.wsdl')
  if File.exist?(wsdl_path)
    File.read(wsdl_path)
  else
    "<error>WSDL no encontrado</error>"
  end
end

post '/ws/FacturacionService' do
  content_type 'text/xml; charset=utf-8'
  raw_body = request.body.read

  # Validación de seguridad SOAP
  unless raw_body.include?(VALID_SOAP_TOKEN) || raw_body.include?('password123')
    status 401
    return <<~XML
      <?xml version="1.0" encoding="UTF-8"?>
      <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
          <soapenv:Fault>
            <faultcode>Client.AuthenticationFailed</faultcode>
            <faultstring>Autenticacion SOAP fallida en Ruby Service: Token invalido o ausente</faultstring>
          </soapenv:Fault>
        </soapenv:Body>
      </soapenv:Envelope>
    XML
  end

  begin
    doc = REXML::Document.new(raw_body)
    
    # 1. GetProductStock
    if raw_body.include?('GetProductStock')
      code_elem = REXML::XPath.first(doc, "//*[local-name()='ProductCode']")
      pcode = code_elem ? code_elem.text.to_s.strip : ''
      prod = products_db.find { |p| p[:code].casecmp?(pcode) }
      if prod
        return <<~XML
          <?xml version="1.0" encoding="UTF-8"?>
          <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
            <soapenv:Body>
              <tns:GetProductStockResponse>
                <tns:ProductCode>#{prod[:code]}</tns:ProductCode>
                <tns:ProductName>#{prod[:name]}</tns:ProductName>
                <tns:Stock>#{prod[:stock]}</tns:Stock>
                <tns:Price>#{prod[:price]}</tns:Price>
                <tns:Available>#{prod[:stock] > 0 ? 'true' : 'false'}</tns:Available>
              </tns:GetProductStockResponse>
            </soapenv:Body>
          </soapenv:Envelope>
        XML
      else
        return <<~XML
          <?xml version="1.0" encoding="UTF-8"?>
          <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
            <soapenv:Body>
              <tns:GetProductStockResponse>
                <tns:ProductCode>#{pcode}</tns:ProductCode>
                <tns:ProductName>NO EXISTE</tns:ProductName>
                <tns:Stock>0</tns:Stock>
                <tns:Price>0.0</tns:Price>
                <tns:Available>false</tns:Available>
              </tns:GetProductStockResponse>
            </soapenv:Body>
          </soapenv:Envelope>
        XML
      end
    end

    # 2. CalculateInvoice
    if raw_body.include?('CalculateInvoice')
      subtotal = 0.0
      count = 0
      REXML::XPath.each(doc, "//*[local-name()='Item']") do |item|
        p_code = REXML::XPath.first(item, "*[local-name()='ProductCode']")&.text.to_s.strip
        qty = REXML::XPath.first(item, "*[local-name()='Quantity']")&.text.to_i
        prod = products_db.find { |p| p[:code].casecmp?(p_code) }
        if prod
          subtotal += prod[:price] * qty
          count += qty
        end
      end
      tax = (subtotal * 0.16).round(2)
      total = (subtotal + tax).round(2)

      return <<~XML
        <?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
          <soapenv:Body>
            <tns:CalculateInvoiceResponse>
              <tns:Subtotal>#{subtotal.round(2)}</tns:Subtotal>
              <tns:Tax>#{tax}</tns:Tax>
              <tns:Total>#{total}</tns:Total>
              <tns:ItemsCount>#{count}</tns:ItemsCount>
            </tns:CalculateInvoiceResponse>
          </soapenv:Body>
        </soapenv:Envelope>
      XML
    end

    # 3. ProcessInvoice
    if raw_body.include?('ProcessInvoice')
      cust_elem = REXML::XPath.first(doc, "//*[local-name()='CustomerName']")
      cust_name = cust_elem ? cust_elem.text.to_s.strip : "Cliente General"

      items_to_process = []
      subtotal = 0.0
      error_msg = nil

      REXML::XPath.each(doc, "//*[local-name()='Item']") do |item|
        p_code = REXML::XPath.first(item, "*[local-name()='ProductCode']")&.text.to_s.strip
        qty = REXML::XPath.first(item, "*[local-name()='Quantity']")&.text.to_i
        prod = products_db.find { |p| p[:code].casecmp?(p_code) }
        
        if prod.nil?
          error_msg = "Producto #{p_code} no existe en inventario Ruby"
          break
        end
        if prod[:stock] < qty
          error_msg = "Stock insuficiente para #{prod[:name]}"
          break
        end

        subtotal += prod[:price] * qty
        items_to_process << { prod: prod, qty: qty }
      end

      if error_msg
        status 500
        return <<~XML
          <?xml version="1.0" encoding="UTF-8"?>
          <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
              <soapenv:Fault>
                <faultcode>Client.ProcessError</faultcode>
                <faultstring>#{error_msg}</faultstring>
              </soapenv:Fault>
            </soapenv:Body>
          </soapenv:Envelope>
        XML
      end

      # Descontar stock
      items_to_process.each do |it|
        it[:prod][:stock] -= it[:qty]
      end

      tax = (subtotal * 0.16).round(2)
      total = (subtotal + tax).round(2)
      inv_num = sprintf("FAC-SOAP-RB-%04d", invoices_db.length + 1)

      invoices_db << {
        id: invoices_db.length + 1,
        invoiceNumber: inv_num,
        customerName: cust_name,
        total: total,
        status: "EMITIDA"
      }

      return <<~XML
        <?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
          <soapenv:Body>
            <tns:ProcessInvoiceResponse>
              <tns:InvoiceNumber>#{inv_num}</tns:InvoiceNumber>
              <tns:CustomerName>#{cust_name}</tns:CustomerName>
              <tns:Total>#{total}</tns:Total>
              <tns:Status>PROCESADA_EXITOSA</tns:Status>
              <tns:Message>Factura procesada y stock descontado exitosamente en Ruby Service</tns:Message>
            </tns:ProcessInvoiceResponse>
          </soapenv:Body>
        </soapenv:Envelope>
      XML
    end

  rescue => e
    status 500
    return <<~XML
      <?xml version="1.0" encoding="UTF-8"?>
      <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
          <soapenv:Fault>
            <faultcode>Client.Error</faultcode>
            <faultstring>#{e.message}</faultstring>
          </soapenv:Fault>
        </soapenv:Body>
      </soapenv:Envelope>
    XML
  end
end

# ==================== ENDPOINTS REST ====================

post '/api/auth/login' do
  content_type :json
  raw = begin
    request.body.read
  rescue
    '{}'
  end
  raw = '{}' if raw.nil? || raw.strip.empty?
  payload = JSON.parse(raw)
  if payload['username'] == 'admin' && payload['password'] == 'password123'
    return { token: VALID_REST_TOKEN, token_type: 'Bearer', user: 'admin' }.to_json
  end
  status 401
  { error: 'Credenciales inválidas' }.to_json
end

get '/api/products' do
  content_type :json
  results = products_db
  if params['category']
    results = results.select { |p| p[:category].downcase == params['category'].downcase }
  end
  if params['search']
    s = params['search'].downcase
    results = results.select { |p| p[:name].downcase.include?(s) || p[:code].downcase.include?(s) }
  end
  results.to_json
end

get '/api/products/:id' do
  content_type :json
  id = params['id'].to_i
  prod = products_db.find { |p| p[:id] == id }
  if prod
    prod.to_json
  else
    status 404
    { error: 'Producto no encontrado' }.to_json
  end
end

post '/api/products' do
  authenticate_rest!
  content_type :json
  payload = JSON.parse(request.body.read)

  if products_db.any? { |p| p[:code].casecmp?(payload['code']) }
    status 400
    return { error: 'El código de producto ya existe' }.to_json
  end

  new_id = products_db.map { |p| p[:id] }.max.to_i + 1
  new_prod = {
    id: new_id,
    code: payload['code'],
    name: payload['name'],
    category: payload['category'],
    price: payload['price'].to_f,
    stock: payload['stock'].to_i
  }
  products_db << new_prod
  status 201
  new_prod.to_json
end

put '/api/products/:id' do
  authenticate_rest!
  content_type :json
  id = params['id'].to_i
  payload = JSON.parse(request.body.read)
  prod = products_db.find { |p| p[:id] == id }

  if prod.nil?
    status 404
    return { error: 'Producto no encontrado' }.to_json
  end

  prod[:code] = payload['code'] if payload['code']
  prod[:name] = payload['name'] if payload['name']
  prod[:category] = payload['category'] if payload['category']
  prod[:price] = payload['price'].to_f if payload['price']
  prod[:stock] = payload['stock'].to_i if payload['stock']

  prod.to_json
end

delete '/api/products/:id' do
  authenticate_rest!
  content_type :json
  id = params['id'].to_i
  initial_len = products_db.length
  products_db.reject! { |p| p[:id] == id }

  if products_db.length < initial_len
    { message: "Producto con ID #{id} eliminado exitosamente" }.to_json
  else
    status 404
    { error: 'Producto no encontrado' }.to_json
  end
end

post '/api/invoices' do
  authenticate_rest!
  content_type :json
  payload = JSON.parse(request.body.read)

  subtotal = 0.0
  items_detail = []

  payload['items'].each do |item|
    prod = products_db.find { |p| p[:code].casecmp?(item['productCode']) }
    if prod.nil?
      status 404
      return { error: "Producto #{item['productCode']} no existe" }.to_json
    end
    if prod[:stock] < item['quantity'].to_i
      status 400
      return { error: "Stock insuficiente para #{prod[:name]}" }.to_json
    end

    line_total = prod[:price] * item['quantity'].to_i
    subtotal += line_total
    items_detail << {
      productCode: prod[:code],
      productName: prod[:name],
      unitPrice: prod[:price],
      quantity: item['quantity'].to_i,
      subtotal: line_total
    }
  end

  # Descontar stock
  payload['items'].each do |item|
    prod = products_db.find { |p| p[:code].casecmp?(item['productCode']) }
    prod[:stock] -= item['quantity'].to_i
  end

  tax = (subtotal * 0.16).round(2)
  total = (subtotal + tax).round(2)
  inv_num = sprintf("FAC-RB-%04d", invoices_db.length + 1)

  invoice = {
    id: invoices_db.length + 1,
    invoiceNumber: inv_num,
    customerName: payload['customerName'],
    date: Time.now.iso8601,
    items: items_detail,
    subtotal: subtotal.round(2),
    tax: tax,
    total: total,
    status: 'EMITIDA'
  }
  invoices_db << invoice

  status 201
  invoice.to_json
end

get '/api/invoices' do
  content_type :json
  invoices_db.to_json
end

get '/api/invoices/:id' do
  content_type :json
  id = params['id'].to_i
  inv = invoices_db.find { |i| i[:id] == id }
  if inv
    inv.to_json
  else
    status 404
    { error: 'Factura no encontrada' }.to_json
  end
end
