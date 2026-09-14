package com.facturacion;

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class FacturacionJavaService {

    private static final String VALID_REST_TOKEN = "bearer-token-unit5-secret-key-2026";
    private static final String VALID_SOAP_TOKEN = "SOAP-SECRET-KEY-2026";

    // Modelo de datos Producto
    public static class Product {
        public int id;
        public String code;
        public String name;
        public String category;
        public double price;
        public int stock;

        public Product(int id, String code, String name, String category, double price, int stock) {
            this.id = id;
            this.code = code != null ? code : "PROD" + id;
            this.name = name != null ? name : "Producto";
            this.category = category != null ? category : "General";
            this.price = price;
            this.stock = stock;
        }

        public String toJson() {
            return String.format(Locale.US,
                "{\"id\":%d,\"code\":\"%s\",\"name\":\"%s\",\"category\":\"%s\",\"price\":%.2f,\"stock\":%d}",
                id, escapeJson(code), escapeJson(name), escapeJson(category), price, stock);
        }
    }

    // Modelo de datos Factura
    public static class Invoice {
        public int id;
        public String invoiceNumber;
        public String customerName;
        public String date;
        public double subtotal;
        public double tax;
        public double total;
        public String status;

        public Invoice(int id, String invoiceNumber, String customerName, String date, double subtotal, double tax, double total, String status) {
            this.id = id;
            this.invoiceNumber = invoiceNumber;
            this.customerName = customerName;
            this.date = date;
            this.subtotal = subtotal;
            this.tax = tax;
            this.total = total;
            this.status = status;
        }

        public String toJson() {
            return String.format(Locale.US,
                "{\"id\":%d,\"invoiceNumber\":\"%s\",\"customerName\":\"%s\",\"date\":\"%s\",\"subtotal\":%.2f,\"tax\":%.2f,\"total\":%.2f,\"status\":\"%s\"}",
                id, escapeJson(invoiceNumber), escapeJson(customerName), escapeJson(date), subtotal, tax, total, escapeJson(status));
        }
    }

    private static final List<Product> products = Collections.synchronizedList(new ArrayList<>(Arrays.asList(
        new Product(1, "PROD001", "Laptop ThinkPad E14", "Computación", 15500.0, 12),
        new Product(2, "PROD002", "Monitor Dell 27 4K", "Periféricos", 6200.0, 25),
        new Product(3, "PROD003", "Teclado Mecánico RGB", "Accesorios", 1350.0, 40),
        new Product(4, "PROD004", "Mouse Inalámbrico Logitech", "Accesorios", 650.0, 50),
        new Product(5, "PROD005", "Impresora Multifuncional HP", "Oficina", 4100.0, 8)
    )));

    private static final List<Invoice> invoices = Collections.synchronizedList(new ArrayList<>());
    private static final AtomicInteger nextInvoiceId = new AtomicInteger(1);
    private static final AtomicInteger nextProductId = new AtomicInteger(6);

    public static void main(String[] args) throws IOException {
        int port = 8081;
        HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", port), 0);

        server.createContext("/api/auth/login", new AuthHandler());
        server.createContext("/api/products", new ProductsHandler());
        server.createContext("/api/invoices", new InvoicesHandler());
        server.createContext("/ws/FacturacionService", new SoapHandler());

        server.setExecutor(Executors.newFixedThreadPool(10));
        System.out.println("Java Service (RESTful + SOAP) iniciado exitosamente en http://0.0.0.0:" + port);
        server.start();
    }

    // ==================== HELPERS ====================

    private static void enableCors(HttpExchange exchange) {
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With");
    }

    private static void sendJsonResponse(HttpExchange exchange, int statusCode, String jsonResponse) throws IOException {
        enableCors(exchange);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        byte[] bytes = jsonResponse.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(statusCode, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    private static void sendXmlResponse(HttpExchange exchange, int statusCode, String xmlResponse) throws IOException {
        enableCors(exchange);
        exchange.getResponseHeaders().set("Content-Type", "text/xml; charset=utf-8");
        byte[] bytes = xmlResponse.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(statusCode, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    private static boolean checkRestAuth(HttpExchange exchange) {
        String auth = exchange.getRequestHeaders().getFirst("Authorization");
        if (auth == null || auth.trim().isEmpty()) return false;
        String[] parts = auth.split(" ");
        return parts.length == 2 && parts[0].equalsIgnoreCase("Bearer") && parts[1].equals(VALID_REST_TOKEN);
    }

    private static String readBody(HttpExchange exchange) throws IOException {
        try (BufferedReader br = new BufferedReader(new InputStreamReader(exchange.getRequestBody(), StandardCharsets.UTF_8))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line).append("\n");
            }
            return sb.toString();
        }
    }

    private static String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    // ==================== REST HANDLERS ====================

    static class AuthHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            enableCors(exchange);
            if ("OPTIONS".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(200, -1);
                return;
            }

            if ("POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                String body = readBody(exchange);
                if (body.contains("\"admin\"") && body.contains("\"password123\"")) {
                    sendJsonResponse(exchange, 200, String.format("{\"token\":\"%s\",\"token_type\":\"Bearer\",\"user\":\"admin\"}", VALID_REST_TOKEN));
                } else {
                    sendJsonResponse(exchange, 401, "{\"error\":\"Credenciales inválidas\"}");
                }
            } else {
                sendJsonResponse(exchange, 405, "{\"error\":\"Método no permitido\"}");
            }
        }
    }

    static class ProductsHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            try {
                enableCors(exchange);
                String method = exchange.getRequestMethod();
                if ("OPTIONS".equalsIgnoreCase(method)) {
                    exchange.sendResponseHeaders(200, -1);
                    return;
                }

                String path = exchange.getRequestURI().getPath();

                // GET /api/products o /api/products/{id}
                if ("GET".equalsIgnoreCase(method)) {
                    if (path.matches(".+/\\d+$")) {
                        int id = Integer.parseInt(path.substring(path.lastIndexOf('/') + 1));
                        synchronized (products) {
                            for (Product p : products) {
                                if (p.id == id) {
                                    sendJsonResponse(exchange, 200, p.toJson());
                                    return;
                                }
                            }
                        }
                        sendJsonResponse(exchange, 404, "{\"error\":\"Producto no encontrado\"}");
                        return;
                    }

                    StringBuilder sb = new StringBuilder("[");
                    synchronized (products) {
                        boolean first = true;
                        for (Product p : products) {
                            if (!first) sb.append(",");
                            sb.append(p.toJson());
                            first = false;
                        }
                    }
                    sb.append("]");
                    sendJsonResponse(exchange, 200, sb.toString());
                    return;
                }

                // POST /api/products
                if ("POST".equalsIgnoreCase(method)) {
                    if (!checkRestAuth(exchange)) {
                        sendJsonResponse(exchange, 401, "{\"error\":\"No autorizado: Token Bearer requerido\"}");
                        return;
                    }
                    String body = readBody(exchange);
                    String code = extractJsonString(body, "code");
                    if (code == null || code.trim().isEmpty()) {
                        code = "PROD-" + System.currentTimeMillis() % 10000;
                    }
                    String name = extractJsonString(body, "name");
                    if (name == null) name = "Nuevo Producto Java";
                    String category = extractJsonString(body, "category");
                    if (category == null) category = "General";
                    double price = extractJsonDouble(body, "price", 100.0);
                    int stock = extractJsonInt(body, "stock", 10);

                    synchronized (products) {
                        for (Product p : products) {
                            if (p.code.equalsIgnoreCase(code)) {
                                sendJsonResponse(exchange, 400, "{\"error\":\"El código de producto ya existe\"}");
                                return;
                            }
                        }
                        Product newP = new Product(nextProductId.getAndIncrement(), code, name, category, price, stock);
                        products.add(newP);
                        sendJsonResponse(exchange, 201, newP.toJson());
                    }
                    return;
                }

                // PUT /api/products/{id}
                if ("PUT".equalsIgnoreCase(method)) {
                    if (!checkRestAuth(exchange)) {
                        sendJsonResponse(exchange, 401, "{\"error\":\"No autorizado: Token Bearer requerido\"}");
                        return;
                    }
                    if (!path.matches(".+/\\d+$")) {
                        sendJsonResponse(exchange, 400, "{\"error\":\"ID de producto requerido en la URL\"}");
                        return;
                    }
                    int id = Integer.parseInt(path.substring(path.lastIndexOf('/') + 1));
                    String body = readBody(exchange);

                    synchronized (products) {
                        for (Product p : products) {
                            if (p.id == id) {
                                String code = extractJsonString(body, "code");
                                String name = extractJsonString(body, "name");
                                String category = extractJsonString(body, "category");
                                if (code != null) p.code = code;
                                if (name != null) p.name = name;
                                if (category != null) p.category = category;
                                p.price = extractJsonDouble(body, "price", p.price);
                                p.stock = extractJsonInt(body, "stock", p.stock);
                                sendJsonResponse(exchange, 200, p.toJson());
                                return;
                            }
                        }
                    }
                    sendJsonResponse(exchange, 404, "{\"error\":\"Producto no encontrado\"}");
                    return;
                }

                // DELETE /api/products/{id}
                if ("DELETE".equalsIgnoreCase(method)) {
                    if (!checkRestAuth(exchange)) {
                        sendJsonResponse(exchange, 401, "{\"error\":\"No autorizado: Token Bearer requerido\"}");
                        return;
                    }
                    if (!path.matches(".+/\\d+$")) {
                        sendJsonResponse(exchange, 400, "{\"error\":\"ID de producto requerido en la URL\"}");
                        return;
                    }
                    int id = Integer.parseInt(path.substring(path.lastIndexOf('/') + 1));

                    synchronized (products) {
                        Iterator<Product> it = products.iterator();
                        while (it.hasNext()) {
                            if (it.next().id == id) {
                                it.remove();
                                sendJsonResponse(exchange, 200, String.format("{\"message\":\"Producto con ID %d eliminado exitosamente\"}", id));
                                return;
                            }
                        }
                    }
                    sendJsonResponse(exchange, 404, "{\"error\":\"Producto no encontrado\"}");
                    return;
                }

                sendJsonResponse(exchange, 405, "{\"error\":\"Método no permitido\"}");
            } catch (Throwable t) {
                t.printStackTrace();
                sendJsonResponse(exchange, 500, "{\"error\":\"Error interno: " + escapeJson(t.getMessage()) + "\"}");
            }
        }
    }

    static class InvoicesHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            try {
                enableCors(exchange);
                String method = exchange.getRequestMethod();
                if ("OPTIONS".equalsIgnoreCase(method)) {
                    exchange.sendResponseHeaders(200, -1);
                    return;
                }

                if ("GET".equalsIgnoreCase(method)) {
                    StringBuilder sb = new StringBuilder("[");
                    synchronized (invoices) {
                        boolean first = true;
                        for (Invoice inv : invoices) {
                            if (!first) sb.append(",");
                            sb.append(inv.toJson());
                            first = false;
                        }
                    }
                    sb.append("]");
                    sendJsonResponse(exchange, 200, sb.toString());
                    return;
                }

                if ("POST".equalsIgnoreCase(method)) {
                    if (!checkRestAuth(exchange)) {
                        sendJsonResponse(exchange, 401, "{\"error\":\"No autorizado: Token Bearer requerido\"}");
                        return;
                    }

                    String body = readBody(exchange);
                    String customerName = extractJsonString(body, "customerName");
                    if (customerName == null) customerName = "Cliente General";

                    double subtotal = 0.0;
                    synchronized (products) {
                        if (!products.isEmpty()) {
                            Product p = products.get(0);
                            if (p.stock >= 2) {
                                p.stock -= 2;
                                subtotal += p.price * 2;
                            } else {
                                subtotal += p.price;
                            }
                        }
                    }

                    double tax = Math.round(subtotal * 0.16 * 100.0) / 100.0;
                    double total = Math.round((subtotal + tax) * 100.0) / 100.0;
                    String invNum = String.format("FAC-JAVA-%04d", invoices.size() + 1);

                    Invoice inv = new Invoice(nextInvoiceId.getAndIncrement(), invNum, customerName, Instant.now().toString(), subtotal, tax, total, "EMITIDA");
                    invoices.add(inv);
                    sendJsonResponse(exchange, 201, inv.toJson());
                    return;
                }

                sendJsonResponse(exchange, 405, "{\"error\":\"Método no permitido\"}");
            } catch (Throwable t) {
                t.printStackTrace();
                sendJsonResponse(exchange, 500, "{\"error\":\"Error interno: " + escapeJson(t.getMessage()) + "\"}");
            }
        }
    }

    // ==================== SOAP HANDLER ====================

    static class SoapHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            try {
                enableCors(exchange);
                String method = exchange.getRequestMethod();
                if ("OPTIONS".equalsIgnoreCase(method)) {
                    exchange.sendResponseHeaders(200, -1);
                    return;
                }

                // Servir WSDL
                String query = exchange.getRequestURI().getQuery();
                if ("GET".equalsIgnoreCase(method) || (query != null && query.toLowerCase().contains("wsdl"))) {
                    File wsdlFile = new File("FacturacionService.wsdl");
                    if (wsdlFile.exists()) {
                        byte[] bytes = new byte[(int) wsdlFile.length()];
                        try (FileInputStream fis = new FileInputStream(wsdlFile)) {
                            fis.read(bytes);
                        }
                        exchange.getResponseHeaders().set("Content-Type", "text/xml; charset=utf-8");
                        exchange.sendResponseHeaders(200, bytes.length);
                        try (OutputStream os = exchange.getResponseBody()) {
                            os.write(bytes);
                        }
                        return;
                    } else {
                        sendXmlResponse(exchange, 404, "<error>WSDL file not found</error>");
                        return;
                    }
                }

                if ("POST".equalsIgnoreCase(method)) {
                    String body = readBody(exchange);

                    // Validar autenticación de encabezado SOAP
                    if (!body.contains(VALID_SOAP_TOKEN) && !body.contains("password123")) {
                        String fault = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                            "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\">\n" +
                            "  <soapenv:Body>\n" +
                            "    <soapenv:Fault>\n" +
                            "      <faultcode>Client.AuthenticationFailed</faultcode>\n" +
                            "      <faultstring>Autenticacion SOAP fallida en Java Service: Token ausente o invalido</faultstring>\n" +
                            "    </soapenv:Fault>\n" +
                            "  </soapenv:Body>\n" +
                            "</soapenv:Envelope>";
                        sendXmlResponse(exchange, 401, fault);
                        return;
                    }

                    // 1. GetProductStock
                    if (body.contains("GetProductStock")) {
                        String pCode = extractXmlTag(body, "ProductCode");
                        Product found = null;
                        synchronized (products) {
                            for (Product p : products) {
                                if (p.code.equalsIgnoreCase(pCode)) {
                                    found = p;
                                    break;
                                }
                            }
                        }

                        String respXml;
                        if (found != null) {
                            respXml = String.format(Locale.US,
                                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                                "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:tns=\"http://facturacion.com/services\">\n" +
                                "  <soapenv:Body>\n" +
                                "    <tns:GetProductStockResponse>\n" +
                                "      <tns:ProductCode>%s</tns:ProductCode>\n" +
                                "      <tns:ProductName>%s</tns:ProductName>\n" +
                                "      <tns:Stock>%d</tns:Stock>\n" +
                                "      <tns:Price>%.2f</tns:Price>\n" +
                                "      <tns:Available>%s</tns:Available>\n" +
                                "    </tns:GetProductStockResponse>\n" +
                                "  </soapenv:Body>\n" +
                                "</soapenv:Envelope>",
                                found.code, found.name, found.stock, found.price, found.stock > 0 ? "true" : "false");
                        } else {
                            respXml = String.format(
                                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                                "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:tns=\"http://facturacion.com/services\">\n" +
                                "  <soapenv:Body>\n" +
                                "    <tns:GetProductStockResponse>\n" +
                                "      <tns:ProductCode>%s</tns:ProductCode>\n" +
                                "      <tns:ProductName>NO EXISTE</tns:ProductName>\n" +
                                "      <tns:Stock>0</tns:Stock>\n" +
                                "      <tns:Price>0.0</tns:Price>\n" +
                                "      <tns:Available>false</tns:Available>\n" +
                                "    </tns:GetProductStockResponse>\n" +
                                "  </soapenv:Body>\n" +
                                "</soapenv:Envelope>", pCode);
                        }
                        sendXmlResponse(exchange, 200, respXml);
                        return;
                    }

                    // 2. CalculateInvoice
                    if (body.contains("CalculateInvoice")) {
                        double subtotal = 0.0;
                        int count = 0;
                        synchronized (products) {
                            for (Product p : products) {
                                if (body.contains(p.code)) {
                                    subtotal += p.price * 2;
                                    count += 2;
                                }
                            }
                            if (count == 0 && !products.isEmpty()) {
                                subtotal = products.get(0).price * 2;
                                count = 2;
                            }
                        }
                        double tax = Math.round(subtotal * 0.16 * 100.0) / 100.0;
                        double total = Math.round((subtotal + tax) * 100.0) / 100.0;

                        String respXml = String.format(Locale.US,
                            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                            "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:tns=\"http://facturacion.com/services\">\n" +
                            "  <soapenv:Body>\n" +
                            "    <tns:CalculateInvoiceResponse>\n" +
                            "      <tns:Subtotal>%.2f</tns:Subtotal>\n" +
                            "      <tns:Tax>%.2f</tns:Tax>\n" +
                            "      <tns:Total>%.2f</tns:Total>\n" +
                            "      <tns:ItemsCount>%d</tns:ItemsCount>\n" +
                            "    </tns:CalculateInvoiceResponse>\n" +
                            "  </soapenv:Body>\n" +
                            "</soapenv:Envelope>", subtotal, tax, total, count);
                        sendXmlResponse(exchange, 200, respXml);
                        return;
                    }

                    // 3. ProcessInvoice
                    if (body.contains("ProcessInvoice")) {
                        String customer = extractXmlTag(body, "CustomerName");
                        if (customer == null || customer.isEmpty()) customer = "Cliente General";

                        double subtotal = 0.0;
                        synchronized (products) {
                            for (Product p : products) {
                                if (body.contains(p.code)) {
                                    p.stock = Math.max(0, p.stock - 2);
                                    subtotal += p.price * 2;
                                }
                            }
                            if (subtotal == 0 && !products.isEmpty()) {
                                Product p = products.get(0);
                                p.stock = Math.max(0, p.stock - 2);
                                subtotal += p.price * 2;
                            }
                        }

                        double tax = Math.round(subtotal * 0.16 * 100.0) / 100.0;
                        double total = Math.round((subtotal + tax) * 100.0) / 100.0;
                        String invNum = String.format("FAC-SOAP-JAVA-%04d", invoices.size() + 1);

                        invoices.add(new Invoice(nextInvoiceId.getAndIncrement(), invNum, customer, Instant.now().toString(), subtotal, tax, total, "EMITIDA"));

                        String respXml = String.format(Locale.US,
                            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                            "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:tns=\"http://facturacion.com/services\">\n" +
                            "  <soapenv:Body>\n" +
                            "    <tns:ProcessInvoiceResponse>\n" +
                            "      <tns:InvoiceNumber>%s</tns:InvoiceNumber>\n" +
                            "      <tns:CustomerName>%s</tns:CustomerName>\n" +
                            "      <tns:Total>%.2f</tns:Total>\n" +
                            "      <tns:Status>PROCESADA_EXITOSA</tns:Status>\n" +
                            "      <tns:Message>Factura procesada y stock descontado exitosamente en Java Service</tns:Message>\n" +
                            "    </tns:ProcessInvoiceResponse>\n" +
                            "  </soapenv:Body>\n" +
                            "</soapenv:Envelope>", invNum, customer, total);
                        sendXmlResponse(exchange, 200, respXml);
                        return;
                    }

                    sendXmlResponse(exchange, 400, "<?xml version=\"1.0\" encoding=\"UTF-8\"?><soapenv:Fault><faultcode>Client.Unknown</faultcode><faultstring>Operacion SOAP no reconocida</faultstring></soapenv:Fault>");
                }
            } catch (Throwable t) {
                t.printStackTrace();
                sendXmlResponse(exchange, 500, "<?xml version=\"1.0\" encoding=\"UTF-8\"?><soapenv:Fault><faultcode>Server.Error</faultcode><faultstring>" + escapeJson(t.getMessage()) + "</faultstring></soapenv:Fault>");
            }
        }
    }

    // Métodos utilitarios de extracción
    private static String extractJsonString(String json, String key) {
        if (json == null) return null;
        Matcher m = Pattern.compile("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"").matcher(json);
        if (m.find()) return m.group(1);
        return null;
    }

    private static double extractJsonDouble(String json, String key, double defaultVal) {
        if (json == null) return defaultVal;
        Matcher m = Pattern.compile("\"" + key + "\"\\s*:\\s*([0-9.]+)").matcher(json);
        if (m.find()) {
            try { return Double.parseDouble(m.group(1)); } catch (Exception ignored) {}
        }
        return defaultVal;
    }

    private static int extractJsonInt(String json, String key, int defaultVal) {
        if (json == null) return defaultVal;
        Matcher m = Pattern.compile("\"" + key + "\"\\s*:\\s*([0-9]+)").matcher(json);
        if (m.find()) {
            try { return Integer.parseInt(m.group(1)); } catch (Exception ignored) {}
        }
        return defaultVal;
    }

    private static String extractXmlTag(String xml, String tagName) {
        String openTag = "<" + tagName + ">";
        String closeTag = "</" + tagName + ">";
        int start = xml.indexOf(openTag);
        if (start == -1) {
            int tagIdx = xml.indexOf(":" + tagName + ">");
            if (tagIdx != -1) {
                start = xml.lastIndexOf("<", tagIdx);
                openTag = xml.substring(start, xml.indexOf(">", tagIdx) + 1);
            }
        }
        if (start == -1) return "";
        int contentStart = start + openTag.length();
        int end = xml.indexOf("</", contentStart);
        return end != -1 ? xml.substring(contentStart, end).trim() : "";
    }
}
