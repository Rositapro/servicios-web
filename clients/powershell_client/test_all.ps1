# Script de prueba rápida en PowerShell para los 6 Servicios Web (Unit 5)
Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  PRUEBA RAPIDA DE SERVICIOS WEB SOAP & RESTful (.ps1)" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

$services = @(
    @{ Name = "Java"; Port = 8081; Type = "Software Libre" },
    @{ Name = "Python"; Port = 8082; Type = "Software Libre" },
    @{ Name = "PHP"; Port = 8083; Type = "Software Libre" },
    @{ Name = "Ruby"; Port = 8084; Type = "Software Libre" },
    @{ Name = "C# (.NET)"; Port = 8085; Type = "Propietario" },
    @{ Name = "VB.NET"; Port = 8086; Type = "Propietario" }
)

$restToken = "bearer-token-unit5-secret-key-2026"
$soapToken = "SOAP-SECRET-KEY-2026"

foreach ($s in $services) {
    Write-Host "--> Verificando Nodo $($s.Name) en puerto $($s.Port)..." -ForegroundColor Yellow
    $urlRest = "http://localhost:$($s.Port)/api/products"
    $urlSoap = "http://localhost:$($s.Port)/ws/FacturacionService"

    # REST Test
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $restRes = Invoke-RestMethod -Uri $urlRest -Method GET -TimeoutSec 3
        $sw.Stop()
        Write-Host "    [REST OK] GET /api/products -> $($restRes.Count) productos ($($sw.ElapsedMilliseconds)ms)" -ForegroundColor Green
    }
    catch {
        Write-Host "    [REST FAIL] No se pudo conectar a $urlRest" -ForegroundColor Red
    }

    # SOAP Test
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $soapBody = @"
<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>
    <tns:SecurityHeader>
      <tns:AuthToken>$soapToken</tns:AuthToken>
    </tns:SecurityHeader>
  </soapenv:Header>
  <soapenv:Body>
    <tns:GetProductStockRequest>
      <tns:ProductCode>PROD001</tns:ProductCode>
    </tns:GetProductStockRequest>
  </soapenv:Body>
</soapenv:Envelope>
"@
        $soapRes = Invoke-RestMethod -Uri $urlSoap -Method POST -ContentType "text/xml; charset=utf-8" -Body $soapBody -TimeoutSec 3
        $sw.Stop()
        Write-Host "    [SOAP OK] POST /ws/FacturacionService -> Respuesta recibida ($($sw.ElapsedMilliseconds)ms)" -ForegroundColor Green
    }
    catch {
        Write-Host "    [SOAP FAIL] No se pudo comunicar con $urlSoap" -ForegroundColor Red
    }
}

Write-Host "`nPruebas finalizadas. Abre http://localhost:8080 en tu navegador para ver el panel interactivo.`n" -ForegroundColor Cyan
