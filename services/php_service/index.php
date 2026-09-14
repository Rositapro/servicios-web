<?php
// Servicio Web de Facturación e Inventario - PHP 8.2 (RESTful + SOAP)

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$VALID_REST_TOKEN = "bearer-token-unit5-secret-key-2026";
$VALID_SOAP_TOKEN = "SOAP-SECRET-KEY-2026";

// Archivo de base de datos persistente en memoria / json temporal
$db_file = sys_get_temp_dir() . '/php_facturacion_db.json';
if (!file_exists($db_file)) {
    $initial_data = [
        'products' => [
            ['id' => 1, 'code' => 'PROD001', 'name' => 'Laptop ThinkPad E14', 'category' => 'Computación', 'price' => 15500.0, 'stock' => 12],
            ['id' => 2, 'code' => 'PROD002', 'name' => 'Monitor Dell 27 4K', 'category' => 'Periféricos', 'price' => 6200.0, 'stock' => 25],
            ['id' => 3, 'code' => 'PROD003', 'name' => 'Teclado Mecánico RGB', 'category' => 'Accesorios', 'price' => 1350.0, 'stock' => 40],
            ['id' => 4, 'code' => 'PROD004', 'name' => 'Mouse Inalámbrico Logitech', 'category' => 'Accesorios', 'price' => 650.0, 'stock' => 50],
            ['id' => 5, 'code' => 'PROD005', 'name' => 'Impresora Multifuncional HP', 'category' => 'Oficina', 'price' => 4100.0, 'stock' => 8]
        ],
        'invoices' => []
    ];
    file_put_contents($db_file, json_encode($initial_data, JSON_PRETTY_PRINT));
}

function load_db() {
    global $db_file;
    return json_decode(file_get_contents($db_file), true);
}

function save_db($data) {
    global $db_file;
    file_put_contents($db_file, json_encode($data, JSON_PRETTY_PRINT));
}

function json_response($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data);
    exit;
}

function check_auth() {
    global $VALID_REST_TOKEN;
    $headers = getallheaders();
    $auth = $headers['Authorization'] ?? $headers['authorization'] ?? '';
    if (empty($auth)) {
        json_response(['error' => 'Cabecera Authorization no provista'], 401);
    }
    $parts = explode(' ', $auth);
    if (count($parts) !== 2 || strtolower($parts[0]) !== 'bearer' || $parts[1] !== $VALID_REST_TOKEN) {
        json_response(['error' => 'Token Bearer inválido o expirado'], 401);
    }
}

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

// ==================== ENDPOINT SOAP ====================
if ($uri === '/ws/FacturacionService' || $uri === '/ws/FacturacionService.php') {
    $wsdl_path = __DIR__ . '/FacturacionService.wsdl';

    if (isset($_GET['wsdl']) || $method === 'GET') {
        header("Content-Type: text/xml; charset=utf-8");
        if (file_exists($wsdl_path)) {
            readfile($wsdl_path);
        } else {
            echo "<error>WSDL no encontrado</error>";
        }
        exit;
    }

    if ($method === 'POST') {
        $raw_post = file_get_contents('php://input');

        // Validar seguridad SOAP
        if (strpos($raw_post, $VALID_SOAP_TOKEN) === false && strpos($raw_post, 'password123') === false) {
            http_response_code(401);
            header("Content-Type: text/xml; charset=utf-8");
            echo '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>Client.AuthenticationFailed</faultcode>
      <faultstring>Autenticacion SOAP fallida en PHP Service: Token invalido o ausente</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>';
            exit;
        }

        // Procesar XML SOAP
        try {
            $xml = new SimpleXMLElement($raw_post);
            $xml->registerXPathNamespace('soapenv', 'http://schemas.xmlsoap.org/soap/envelope/');
            $xml->registerXPathNamespace('tns', 'http://facturacion.com/services');

            $body = $xml->xpath('//soapenv:Body/*');
            if (empty($body)) {
                $body = $xml->xpath('/*[local-name()="Envelope"]/*[local-name()="Body"]/*');
            }
            $op_node = $body[0] ?? null;
            $op_name = $op_node ? $op_node->getName() : '';

            $db = load_db();
            header("Content-Type: text/xml; charset=utf-8");

            if ($op_name === 'GetProductStockRequest' || strpos($raw_post, 'GetProductStock') !== false) {
                $code_nodes = $xml->xpath('//*[local-name()="ProductCode"]');
                $code = (string)($code_nodes[0] ?? '');
                
                $found = null;
                foreach ($db['products'] as $p) {
                    if (strcasecmp($p['code'], $code) === 0) {
                        $found = $p;
                        break;
                    }
                }

                if ($found) {
                    echo '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Body>
    <tns:GetProductStockResponse>
      <tns:ProductCode>' . htmlspecialchars($found['code']) . '</tns:ProductCode>
      <tns:ProductName>' . htmlspecialchars($found['name']) . '</tns:ProductName>
      <tns:Stock>' . $found['stock'] . '</tns:Stock>
      <tns:Price>' . $found['price'] . '</tns:Price>
      <tns:Available>' . ($found['stock'] > 0 ? 'true' : 'false') . '</tns:Available>
    </tns:GetProductStockResponse>
  </soapenv:Body>
</soapenv:Envelope>';
                } else {
                    echo '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Body>
    <tns:GetProductStockResponse>
      <tns:ProductCode>' . htmlspecialchars($code) . '</tns:ProductCode>
      <tns:ProductName>NO EXISTE</tns:ProductName>
      <tns:Stock>0</tns:Stock>
      <tns:Price>0.0</tns:Price>
      <tns:Available>false</tns:Available>
    </tns:GetProductStockResponse>
  </soapenv:Body>
</soapenv:Envelope>';
                }
                exit;
            }

            if ($op_name === 'CalculateInvoiceRequest' || strpos($raw_post, 'CalculateInvoice') !== false) {
                $items = $xml->xpath('//*[local-name()="Item"]');
                $subtotal = 0;
                $count = 0;
                foreach ($items as $item) {
                    $pcode = (string)$item->xpath('*[local-name()="ProductCode"]')[0];
                    $qty = (int)$item->xpath('*[local-name()="Quantity"]')[0];
                    foreach ($db['products'] as $p) {
                        if (strcasecmp($p['code'], $pcode) === 0) {
                            $subtotal += $p['price'] * $qty;
                            $count += $qty;
                        }
                    }
                }
                $tax = round($subtotal * 0.16, 2);
                $total = round($subtotal + $tax, 2);

                echo '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Body>
    <tns:CalculateInvoiceResponse>
      <tns:Subtotal>' . round($subtotal, 2) . '</tns:Subtotal>
      <tns:Tax>' . $tax . '</tns:Tax>
      <tns:Total>' . $total . '</tns:Total>
      <tns:ItemsCount>' . $count . '</tns:ItemsCount>
    </tns:CalculateInvoiceResponse>
  </soapenv:Body>
</soapenv:Envelope>';
                exit;
            }

            if ($op_name === 'ProcessInvoiceRequest' || strpos($raw_post, 'ProcessInvoice') !== false) {
                $cust_nodes = $xml->xpath('//*[local-name()="CustomerName"]');
                $cust_name = (string)($cust_nodes[0] ?? 'Cliente General');
                $items = $xml->xpath('//*[local-name()="Item"]');

                $subtotal = 0;
                $items_to_process = [];
                foreach ($items as $item) {
                    $pcode = (string)$item->xpath('*[local-name()="ProductCode"]')[0];
                    $qty = (int)$item->xpath('*[local-name()="Quantity"]')[0];
                    $found_prod = null;
                    foreach ($db['products'] as &$p) {
                        if (strcasecmp($p['code'], $pcode) === 0) {
                            $found_prod = &$p;
                            break;
                        }
                    }
                    if (!$found_prod) {
                        http_response_code(500);
                        echo '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>Client.ProductNotFound</faultcode>
      <faultstring>Producto ' . htmlspecialchars($pcode) . ' no existe en inventario PHP</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>';
                        exit;
                    }
                    if ($found_prod['stock'] < $qty) {
                        http_response_code(500);
                        echo '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>Client.InsufficientStock</faultcode>
      <faultstring>Stock insuficiente para ' . htmlspecialchars($found_prod['name']) . '</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>';
                        exit;
                    }
                    $subtotal += $found_prod['price'] * $qty;
                    $items_to_process[] = ['code' => $pcode, 'qty' => $qty];
                }

                // Descontar inventario
                foreach ($items_to_process as $it) {
                    foreach ($db['products'] as &$p) {
                        if (strcasecmp($p['code'], $it['code']) === 0) {
                            $p['stock'] -= $it['qty'];
                        }
                    }
                }

                $tax = round($subtotal * 0.16, 2);
                $total = round($subtotal + $tax, 2);
                $inv_num = sprintf("FAC-SOAP-PHP-%04d", count($db['invoices']) + 1);

                $db['invoices'][] = [
                    'id' => count($db['invoices']) + 1,
                    'invoiceNumber' => $inv_num,
                    'customerName' => $cust_name,
                    'total' => $total,
                    'status' => 'EMITIDA'
                ];
                save_db($db);

                echo '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Body>
    <tns:ProcessInvoiceResponse>
      <tns:InvoiceNumber>' . $inv_num . '</tns:InvoiceNumber>
      <tns:CustomerName>' . htmlspecialchars($cust_name) . '</tns:CustomerName>
      <tns:Total>' . $total . '</tns:Total>
      <tns:Status>PROCESADA_EXITOSA</tns:Status>
      <tns:Message>Factura procesada y stock descontado exitosamente en PHP Service</tns:Message>
    </tns:ProcessInvoiceResponse>
  </soapenv:Body>
</soapenv:Envelope>';
                exit;
            }

        } catch (Exception $e) {
            http_response_code(500);
            echo '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>Client.Error</faultcode>
      <faultstring>' . htmlspecialchars($e->getMessage()) . '</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>';
            exit;
        }
    }
}

// ==================== ENDPOINTS REST ====================

// Auth Login
if ($uri === '/api/auth/login' && $method === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    if (($input['username'] ?? '') === 'admin' && ($input['password'] ?? '') === 'password123') {
        json_response(['token' => $VALID_REST_TOKEN, 'token_type' => 'Bearer', 'user' => 'admin']);
    }
    json_response(['error' => 'Credenciales inválidas'], 401);
}

// GET /api/products
if ($uri === '/api/products' && $method === 'GET') {
    $db = load_db();
    $list = $db['products'];
    if (!empty($_GET['category'])) {
        $cat = strtolower($_GET['category']);
        $list = array_values(array_filter($list, fn($p) => strtolower($p['category']) === $cat));
    }
    if (!empty($_GET['search'])) {
        $q = strtolower($_GET['search']);
        $list = array_values(array_filter($list, fn($p) => str_contains(strtolower($p['name']), $q) || str_contains(strtolower($p['code']), $q)));
    }
    json_response($list);
}

// GET /api/products/{id}
if (preg_match('#^/api/products/(\d+)$#', $uri, $m) && $method === 'GET') {
    $id = (int)$m[1];
    $db = load_db();
    foreach ($db['products'] as $p) {
        if ($p['id'] === $id) json_response($p);
    }
    json_response(['error' => 'Producto no encontrado'], 404);
}

// POST /api/products (Protegido)
if ($uri === '/api/products' && $method === 'POST') {
    check_auth();
    $input = json_decode(file_get_contents('php://input'), true);
    $db = load_db();
    foreach ($db['products'] as $p) {
        if (strcasecmp($p['code'], $input['code']) === 0) {
            json_response(['error' => 'El código de producto ya existe'], 400);
        }
    }
    $max_id = 0;
    foreach ($db['products'] as $p) {
        if ($p['id'] > $max_id) $max_id = $p['id'];
    }
    $new_prod = [
        'id' => $max_id + 1,
        'code' => $input['code'],
        'name' => $input['name'],
        'category' => $input['category'],
        'price' => (float)$input['price'],
        'stock' => (int)$input['stock']
    ];
    $db['products'][] = $new_prod;
    save_db($db);
    json_response($new_prod, 201);
}

// PUT /api/products/{id} (Protegido)
if (preg_match('#^/api/products/(\d+)$#', $uri, $m) && $method === 'PUT') {
    check_auth();
    $id = (int)$m[1];
    $input = json_decode(file_get_contents('php://input'), true);
    $db = load_db();
    $found = false;
    foreach ($db['products'] as &$p) {
        if ($p['id'] === $id) {
            $p['code'] = $input['code'] ?? $p['code'];
            $p['name'] = $input['name'] ?? $p['name'];
            $p['category'] = $input['category'] ?? $p['category'];
            $p['price'] = isset($input['price']) ? (float)$input['price'] : $p['price'];
            $p['stock'] = isset($input['stock']) ? (int)$input['stock'] : $p['stock'];
            $found = true;
            save_db($db);
            json_response($p);
        }
    }
    if (!$found) json_response(['error' => 'Producto no encontrado'], 404);
}

// DELETE /api/products/{id} (Protegido)
if (preg_match('#^/api/products/(\d+)$#', $uri, $m) && $method === 'DELETE') {
    check_auth();
    $id = (int)$m[1];
    $db = load_db();
    $initial_count = count($db['products']);
    $db['products'] = array_values(array_filter($db['products'], fn($p) => $p['id'] !== $id));
    if (count($db['products']) < $initial_count) {
        save_db($db);
        json_response(['message' => "Producto con ID $id eliminado exitosamente"]);
    }
    json_response(['error' => 'Producto no encontrado'], 404);
}

// POST /api/invoices (Protegido)
if ($uri === '/api/invoices' && $method === 'POST') {
    check_auth();
    $input = json_decode(file_get_contents('php://input'), true);
    $db = load_db();
    $subtotal = 0;
    $line_items = [];

    foreach ($input['items'] as $item) {
        $pcode = $item['productCode'];
        $qty = (int)$item['quantity'];
        $found = null;
        foreach ($db['products'] as $p) {
            if (strcasecmp($p['code'], $pcode) === 0) {
                $found = $p;
                break;
            }
        }
        if (!$found) json_response(['error' => "Producto $pcode no existe"], 404);
        if ($found['stock'] < $qty) json_response(['error' => "Stock insuficiente para {$found['name']}"], 400);

        $line_total = $found['price'] * $qty;
        $subtotal += $line_total;
        $line_items[] = [
            'productCode' => $found['code'],
            'productName' => $found['name'],
            'unitPrice' => $found['price'],
            'quantity' => $qty,
            'subtotal' => $line_total
        ];
    }

    // Descontar inventario
    foreach ($input['items'] as $item) {
        foreach ($db['products'] as &$p) {
            if (strcasecmp($p['code'], $item['productCode']) === 0) {
                $p['stock'] -= (int)$item['quantity'];
            }
        }
    }

    $tax = round($subtotal * 0.16, 2);
    $total = round($subtotal + $tax, 2);
    $inv_num = sprintf("FAC-PHP-%04d", count($db['invoices']) + 1);

    $new_inv = [
        'id' => count($db['invoices']) + 1,
        'invoiceNumber' => $inv_num,
        'customerName' => $input['customerName'],
        'date' => date('c'),
        'items' => $line_items,
        'subtotal' => round($subtotal, 2),
        'tax' => $tax,
        'total' => $total,
        'status' => 'EMITIDA'
    ];
    $db['invoices'][] = $new_inv;
    save_db($db);
    json_response($new_inv, 201);
}

// GET /api/invoices
if ($uri === '/api/invoices' && $method === 'GET') {
    $db = load_db();
    json_response($db['invoices']);
}

// GET /api/invoices/{id}
if (preg_match('#^/api/invoices/(\d+)$#', $uri, $m) && $method === 'GET') {
    $id = (int)$m[1];
    $db = load_db();
    foreach ($db['invoices'] as $inv) {
        if ($inv['id'] === $id) json_response($inv);
    }
    json_response(['error' => 'Factura no encontrada'], 404);
}

// Fallback o documentación rápida
json_response([
    'service' => 'PHP Billing & Inventory Web Service (RESTful + SOAP)',
    'endpoints' => [
        'GET /api/products',
        'POST /api/products (Bearer token required)',
        'PUT /api/products/{id} (Bearer token required)',
        'DELETE /api/products/{id} (Bearer token required)',
        'POST /api/invoices (Bearer token required)',
        'GET /api/invoices',
        'SOAP Endpoint' => 'POST /ws/FacturacionService',
        'WSDL' => 'GET /ws/FacturacionService?wsdl'
    ]
]);
