// Dashboard de Pruebas Multi-Servicio (RESTful + SOAP)

const SERVICES = [
  { id: 'python', name: 'Python', port: 8082, license: 'Libre', frameworks: 'FastAPI / Spyne' },
  { id: 'csharp', name: 'C# (.NET)', port: 8085, license: 'Propietario', frameworks: 'ASP.NET Core / SoapCore' },
  { id: 'vbnet', name: 'VB.NET', port: 8086, license: 'Propietario', frameworks: 'ASP.NET Core / SoapCore' },
  { id: 'java', name: 'Java', port: 8081, license: 'Libre', frameworks: 'Jakarta REST / JAX-WS' },
  { id: 'php', name: 'PHP', port: 8083, license: 'Libre', frameworks: 'Slim / PHP SoapServer' },
  { id: 'ruby', name: 'Ruby', port: 8084, license: 'Libre', frameworks: 'Sinatra / SOAP Server' }
];

let activeService = SERVICES[0]; // Python default
let activeProtocol = 'REST';     // REST o SOAP
const VALID_TOKEN = "bearer-token-unit5-secret-key-2026";
const VALID_SOAP_TOKEN = "SOAP-SECRET-KEY-2026";

// Elementos del DOM
const langTabs = document.getElementById('lang-tabs');
const statusChips = document.getElementById('status-chips');
const toggleRest = document.getElementById('toggle-rest');
const toggleSoap = document.getElementById('toggle-soap');
const sectionRest = document.getElementById('section-rest');
const sectionSoap = document.getElementById('section-soap');

const restPayloadEditor = document.getElementById('rest-payload');
const restResponseViewer = document.getElementById('rest-response-viewer');
const restStatusCode = document.getElementById('rest-status-code');
const restLatency = document.getElementById('rest-latency');
const restUrlBadge = document.getElementById('rest-url-badge');

const soapRequestXml = document.getElementById('soap-request-xml');
const soapResponseViewer = document.getElementById('soap-response-viewer');
const soapStatusCode = document.getElementById('soap-status-code');
const soapLatency = document.getElementById('soap-latency');
const soapUrlBadge = document.getElementById('soap-url-badge');
const chkSoapAuth = document.getElementById('chk-soap-auth');

const wsdlModal = document.getElementById('wsdl-modal');
const wsdlContent = document.getElementById('wsdl-content');
const btnViewWsdl = document.getElementById('btn-view-wsdl');
const btnCloseModal = document.getElementById('btn-close-modal');

const benchmarkTbody = document.getElementById('benchmark-tbody');
const btnRunBenchmark = document.getElementById('btn-run-all-benchmark');
const btnRefreshBenchmark = document.getElementById('btn-refresh-benchmark');

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
  renderStatusRibbon();
  initLangTabs();
  initProtocolToggles();
  initSoapTemplates();
  resetSampleRestJson();
  pingAllServices();
  runBenchmark();
});

// Selector de Lenguaje
function initLangTabs() {
  const tabs = document.querySelectorAll('.lang-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const langId = tab.dataset.lang;
      activeService = SERVICES.find(s => s.id === langId);
      updateBadges();
      // Refrescar payload SOAP para el servicio activo
      loadSoapOp('GetProductStock');
    });
  });
}

// Alternar entre REST y SOAP
function initProtocolToggles() {
  toggleRest.addEventListener('click', () => {
    activeProtocol = 'REST';
    toggleRest.classList.add('active');
    toggleSoap.classList.remove('active');
    sectionRest.classList.add('active');
    sectionSoap.classList.remove('active');
  });

  toggleSoap.addEventListener('click', () => {
    activeProtocol = 'SOAP';
    toggleSoap.classList.add('active');
    toggleRest.classList.remove('active');
    sectionSoap.classList.add('active');
    sectionRest.classList.remove('active');
    loadSoapOp('GetProductStock');
  });
}

function updateBadges() {
  restUrlBadge.textContent = `http://localhost:${activeService.port}/api/products`;
  soapUrlBadge.textContent = `http://localhost:${activeService.port}/ws/FacturacionService`;
}

// Ribbon de Estado en Vivo
function renderStatusRibbon() {
  statusChips.innerHTML = SERVICES.map(s => `
    <div class="status-chip" id="chip-${s.id}">
      <span class="chip-dot"></span>
      <span>${s.name} (:${s.port})</span>
    </div>
  `).join('');
}

async function pingAllServices() {
  for (const s of SERVICES) {
    const chip = document.getElementById(`chip-${s.id}`);
    try {
      const start = performance.now();
      const res = await fetch(`http://localhost:${s.port}/api/products`, { method: 'GET', signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        chip.classList.remove('offline');
        chip.classList.add('online');
      } else {
        chip.classList.remove('online');
        chip.classList.add('offline');
      }
    } catch (e) {
      chip.classList.remove('online');
      chip.classList.add('offline');
    }
  }
}

// ==================== OPERACIONES REST ====================

async function callRest(method, endpoint, customBody = null) {
  const url = `http://localhost:${activeService.port}${endpoint}`;
  restUrlBadge.textContent = `${method} ${endpoint} (:${activeService.port})`;
  restResponseViewer.textContent = 'Enviando petición HTTP...';
  restStatusCode.textContent = 'Cargando...';
  restStatusCode.className = 'status-code';

  const headers = {
    'Content-Type': 'application/json'
  };

  if (method !== 'GET') {
    headers['Authorization'] = `Bearer ${VALID_TOKEN}`;
  }

  const options = {
    method: method,
    headers: headers
  };

  if (customBody) {
    options.body = customBody;
  }

  const startTime = performance.now();
  try {
    const response = await fetch(url, options);
    const duration = Math.round(performance.now() - startTime);

    restStatusCode.textContent = `${response.status} ${response.statusText}`;
    restStatusCode.className = response.ok ? 'status-code' : 'status-code error';
    restLatency.textContent = `${duration} ms`;

    const text = await response.text();
    try {
      const json = JSON.parse(text);
      restResponseViewer.textContent = JSON.stringify(json, null, 2);
    } catch (err) {
      restResponseViewer.textContent = text;
    }
  } catch (error) {
    const duration = Math.round(performance.now() - startTime);
    restStatusCode.textContent = 'ERROR DE CONEXIÓN';
    restStatusCode.className = 'status-code error';
    restLatency.textContent = `${duration} ms`;
    restResponseViewer.textContent = `Error al conectar con http://localhost:${activeService.port}${endpoint}.\nAsegúrate de que los contenedores estén corriendo con 'docker compose up'.\nDetalles: ${error.message}`;
  }
}

function resetSampleRestJson() {
  restPayloadEditor.value = JSON.stringify({
    code: "PROD006",
    name: "Disco SSD NVMe 1TB Kingston",
    category: "Almacenamiento",
    price: 1850.0,
    stock: 30
  }, null, 2);
}

function prepareCreateProduct() {
  resetSampleRestJson();
  document.getElementById('btn-execute-custom-rest').onclick = () => {
    callRest('POST', '/api/products', restPayloadEditor.value);
  };
}

function prepareUpdateProduct() {
  restPayloadEditor.value = JSON.stringify({
    code: "PROD001",
    name: "Laptop ThinkPad E14 Gen 5 (Actualizada)",
    category: "Computación",
    price: 16900.0,
    stock: 15
  }, null, 2);
  document.getElementById('btn-execute-custom-rest').onclick = () => {
    callRest('PUT', '/api/products/1', restPayloadEditor.value);
  };
}

function prepareCreateInvoice() {
  restPayloadEditor.value = JSON.stringify({
    customerName: "Corporativo Industrial del Norte S.A.",
    items: [
      { productCode: "PROD001", quantity: 2 },
      { productCode: "PROD003", quantity: 3 }
    ]
  }, null, 2);
  document.getElementById('btn-execute-custom-rest').onclick = () => {
    callRest('POST', '/api/invoices', restPayloadEditor.value);
  };
}

document.getElementById('btn-execute-custom-rest').onclick = () => {
  callRest('POST', '/api/products', restPayloadEditor.value);
};

// ==================== OPERACIONES SOAP ====================

function getSoapEnvelope(headerToken, bodyXml) {
  const headerXml = headerToken ? `
    <tns:SecurityHeader>
      <tns:AuthToken>${headerToken}</tns:AuthToken>
    </tns:SecurityHeader>` : '';

  return `<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://facturacion.com/services">
  <soapenv:Header>${headerXml}
  </soapenv:Header>
  <soapenv:Body>
${bodyXml}
  </soapenv:Body>
</soapenv:Envelope>`;
}

function loadSoapOp(operation) {
  const useValidToken = chkSoapAuth.checked;
  const token = useValidToken ? VALID_SOAP_TOKEN : "INVALIDO-TOKEN-TEST";

  let body = '';
  if (operation === 'GetProductStock') {
    body = `    <tns:GetProductStockRequest>
      <tns:ProductCode>PROD001</tns:ProductCode>
    </tns:GetProductStockRequest>`;
  } else if (operation === 'CalculateInvoice') {
    body = `    <tns:CalculateInvoiceRequest>
      <tns:CustomerName>Industrias Metálicas S.A.</tns:CustomerName>
      <tns:Items>
        <tns:Item>
          <tns:ProductCode>PROD001</tns:ProductCode>
          <tns:Quantity>2</tns:Quantity>
        </tns:Item>
        <tns:Item>
          <tns:ProductCode>PROD002</tns:ProductCode>
          <tns:Quantity>1</tns:Quantity>
        </tns:Item>
      </tns:Items>
    </tns:CalculateInvoiceRequest>`;
  } else if (operation === 'ProcessInvoice') {
    body = `    <tns:ProcessInvoiceRequest>
      <tns:CustomerName>Constructora del Centro S.A.</tns:CustomerName>
      <tns:Items>
        <tns:Item>
          <tns:ProductCode>PROD003</tns:ProductCode>
          <tns:Quantity>2</tns:Quantity>
        </tns:Item>
      </tns:Items>
    </tns:ProcessInvoiceRequest>`;
  }

  soapRequestXml.value = getSoapEnvelope(token, body);
}

function initSoapTemplates() {
  chkSoapAuth.addEventListener('change', () => {
    loadSoapOp('GetProductStock');
  });

  document.getElementById('btn-execute-soap').addEventListener('click', async () => {
    const url = `http://localhost:${activeService.port}/ws/FacturacionService`;
    soapUrlBadge.textContent = `POST /ws/FacturacionService (:${activeService.port})`;
    soapResponseViewer.textContent = 'Enviando Envelope SOAP XML...';
    soapStatusCode.textContent = 'Cargando...';
    soapStatusCode.className = 'status-code';

    const xmlPayload = soapRequestXml.value;
    const startTime = performance.now();

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'text/xml; charset=utf-8',
          'SOAPAction': 'http://facturacion.com/services'
        },
        body: xmlPayload
      });

      const duration = Math.round(performance.now() - startTime);
      soapStatusCode.textContent = `${response.status} ${response.statusText}`;
      soapStatusCode.className = response.ok ? 'status-code' : 'status-code error';
      soapLatency.textContent = `${duration} ms`;

      const text = await response.text();
      soapResponseViewer.textContent = formatXml(text);
    } catch (error) {
      const duration = Math.round(performance.now() - startTime);
      soapStatusCode.textContent = 'ERROR DE CONEXIÓN';
      soapStatusCode.className = 'status-code error';
      soapLatency.textContent = `${duration} ms`;
      soapResponseViewer.textContent = `Error al comunicar con endpoint SOAP en :${activeService.port}.\nDetalles: ${error.message}`;
    }
  });

  // Modal WSDL
  btnViewWsdl.addEventListener('click', async () => {
    wsdlModal.classList.add('active');
    wsdlContent.textContent = 'Descargando contrato WSDL...';
    try {
      const res = await fetch(`http://localhost:${activeService.port}/ws/FacturacionService?wsdl`);
      const xml = await res.text();
      wsdlContent.textContent = formatXml(xml);
    } catch (err) {
      wsdlContent.textContent = 'Error al descargar WSDL: ' + err.message;
    }
  });

  btnCloseModal.addEventListener('click', () => {
    wsdlModal.classList.remove('active');
  });
}

function formatXml(xml) {
  let formatted = '';
  let indent = '';
  const tab = '  ';
  xml.split(/>\s*</).forEach(node => {
    if (node.match(/^\/\w/)) indent = indent.substring(tab.length);
    formatted += indent + '<' + node + '>\r\n';
    if (node.match(/^<?\w[^>]*[^\/]$/)) indent += tab;
  });
  return formatted.substring(1, formatted.length - 3);
}

// ==================== BENCHMARK COMPARATIVO ====================

btnRunBenchmark.addEventListener('click', () => runBenchmark(true));
btnRefreshBenchmark.addEventListener('click', () => runBenchmark(false));

async function runBenchmark(scrollToView = false) {
  if (btnRunBenchmark) {
    btnRunBenchmark.disabled = true;
    btnRunBenchmark.innerHTML = `<span class="pulse-dot"></span> ⏳ Midiendo los 6 Nodos...`;
  }
  if (btnRefreshBenchmark) {
    btnRefreshBenchmark.disabled = true;
    btnRefreshBenchmark.innerHTML = `⏳ Evaluando...`;
  }

  const benchSection = document.getElementById('section-benchmark');
  if (scrollToView && benchSection) {
    benchSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  benchmarkTbody.innerHTML = SERVICES.map(s => `
    <tr id="bench-row-${s.id}">
      <td><strong>${s.name}</strong></td>
      <td><span class="lang-tag ${s.license === 'Libre' ? 'libre' : 'prop'}">${s.license}</span></td>
      <td><code>${s.frameworks}</code></td>
      <td><span class="port-tag">:${s.port}</span></td>
      <td class="bench-rest"><span style="color: var(--accent-caramel);">⏳ Midiendo...</span></td>
      <td class="bench-soap"><span style="color: var(--accent-caramel);">⏳ Midiendo...</span></td>
      <td class="bench-interop"><span style="color: var(--text-muted);">Evaluando...</span></td>
    </tr>
  `).join('');

  for (const s of SERVICES) {
    const row = document.getElementById(`bench-row-${s.id}`);
    if (!row) continue;
    const restCell = row.querySelector('.bench-rest');
    const soapCell = row.querySelector('.bench-soap');
    const interopCell = row.querySelector('.bench-interop');

    // Prueba REST
    let restOk = false;
    let restTime = 0;
    try {
      const t0 = performance.now();
      const rRes = await fetch(`http://localhost:${s.port}/api/products`, { signal: AbortSignal.timeout(4000) });
      restTime = Math.round(performance.now() - t0);
      if (rRes.ok) {
        restOk = true;
        restCell.innerHTML = `<span class="status-code">200 OK</span> (${restTime} ms)`;
      } else {
        restCell.innerHTML = `<span class="status-code error">${rRes.status}</span> (${restTime} ms)`;
      }
    } catch (e) {
      restCell.innerHTML = `<span class="status-code error">DOWN</span>`;
    }

    // Prueba SOAP
    let soapOk = false;
    let soapTime = 0;
    try {
      const soapReq = getSoapEnvelope(VALID_SOAP_TOKEN, `
        <tns:GetProductStockRequest>
          <tns:ProductCode>PROD001</tns:ProductCode>
        </tns:GetProductStockRequest>`);
      const t0 = performance.now();
      const sRes = await fetch(`http://localhost:${s.port}/ws/FacturacionService`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/xml; charset=utf-8' },
        body: soapReq,
        signal: AbortSignal.timeout(4000)
      });
      soapTime = Math.round(performance.now() - t0);
      if (sRes.ok) {
        soapOk = true;
        soapCell.innerHTML = `<span class="status-code">200 OK</span> (${soapTime} ms)`;
      } else {
        soapCell.innerHTML = `<span class="status-code error">${sRes.status}</span> (${soapTime} ms)`;
      }
    } catch (e) {
      soapCell.innerHTML = `<span class="status-code error">DOWN</span>`;
    }

    // Interoperabilidad
    if (restOk && soapOk) {
      interopCell.innerHTML = `<span style="color: var(--accent-emerald); font-weight: 700;">✅ 100% Compatible</span>`;
    } else if (restOk || soapOk) {
      interopCell.innerHTML = `<span style="color: var(--accent-amber); font-weight: 700;">⚠️ Parcial</span>`;
    } else {
      interopCell.innerHTML = `<span style="color: var(--accent-rose); font-weight: 700;">❌ Inaccesible</span>`;
    }
  }

  if (btnRunBenchmark) {
    btnRunBenchmark.disabled = false;
    btnRunBenchmark.innerHTML = `<span class="pulse-dot"></span> ⚡ Ejecutar Benchmark en los 6 Servicios`;
  }
  if (btnRefreshBenchmark) {
    btnRefreshBenchmark.disabled = false;
    btnRefreshBenchmark.innerHTML = `🔄 Re-ejecutar Pruebas`;
  }
}
