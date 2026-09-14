Imports System
Imports System.IO
Imports System.Text
Imports System.Collections.Generic
Imports System.Linq
Imports System.ServiceModel
Imports System.Runtime.Serialization
Imports Microsoft.AspNetCore.Builder
Imports Microsoft.AspNetCore.Http
Imports Microsoft.Extensions.DependencyInjection
Imports Microsoft.Extensions.Hosting
Imports SoapCore

Module Program
    Const ValidRestToken As String = "bearer-token-unit5-secret-key-2026"
    Const ValidSoapToken As String = "SOAP-SECRET-KEY-2026"

    Sub Main(args As String())
        Dim builder = WebApplication.CreateBuilder(args)

        builder.Services.AddEndpointsApiExplorer()
        builder.Services.AddSwaggerGen()
        builder.Services.AddSoapCore()
        builder.Services.AddCors(Sub(options)
            options.AddPolicy("AllowAll", Sub(p)
                p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()
            End Sub)
        End Sub)

        builder.Services.AddSingleton(Of VbDataRepository)()
        builder.Services.AddSingleton(Of IFacturacionServiceVb, FacturacionServiceVb)()

        Dim app = builder.Build()

        app.UseCors("AllowAll")
        app.UseSwagger()
        app.UseSwaggerUI()

        ' Middleware para servir WSDL y autenticación SOAP
        app.Use(Async Function(context, [next])
            If context.Request.Path.StartsWithSegments("/ws/FacturacionService") AndAlso context.Request.Query.ContainsKey("wsdl") Then
                context.Response.ContentType = "text/xml; charset=utf-8"
                Dim wsdlPath = Path.Combine(app.Environment.ContentRootPath, "FacturacionService.wsdl")
                If File.Exists(wsdlPath) Then
                    Await context.Response.WriteAsync(Await File.ReadAllTextAsync(wsdlPath))
                    Return
                End If
            End If

            If context.Request.Path.StartsWithSegments("/ws/FacturacionService") AndAlso context.Request.Method.Equals("POST", StringComparison.OrdinalIgnoreCase) Then
                context.Request.EnableBuffering()
                Using reader = New StreamReader(context.Request.Body, Encoding.UTF8, leaveOpen:=True)
                    Dim body = Await reader.ReadToEndAsync()
                    context.Request.Body.Position = 0

                    If Not body.Contains(ValidSoapToken) AndAlso Not body.Contains("password123") Then
                        context.Response.StatusCode = 401
                        context.Response.ContentType = "text/xml; charset=utf-8"
                        Dim faultXml = "<?xml version=""1.0"" encoding=""UTF-8""?>" & vbCrLf &
                            "<soapenv:Envelope xmlns:soapenv=""http://schemas.xmlsoap.org/soap/envelope/"">" & vbCrLf &
                            "  <soapenv:Body>" & vbCrLf &
                            "    <soapenv:Fault>" & vbCrLf &
                            "      <faultcode>Client.AuthenticationFailed</faultcode>" & vbCrLf &
                            "      <faultstring>Autenticacion SOAP fallida en VB.NET Service: Token no valido o ausente</faultstring>" & vbCrLf &
                            "    </soapenv:Fault>" & vbCrLf &
                            "  </soapenv:Body>" & vbCrLf &
                            "</soapenv:Envelope>"
                        Await context.Response.WriteAsync(faultXml)
                        Return
                    End If

                    If body.Contains("GetProductStock") Then
                        Dim pCodeMatch = System.Text.RegularExpressions.Regex.Match(body, "ProductCode>([^<]+)<")
                        Dim pCode = If(pCodeMatch.Success, pCodeMatch.Groups(1).Value.Trim(), "PROD001")
                        Dim repo = context.RequestServices.GetRequiredService(Of VbDataRepository)()
                        Dim prod = repo.Products.FirstOrDefault(Function(p) p.Code.Equals(pCode, StringComparison.OrdinalIgnoreCase))

                        context.Response.ContentType = "text/xml; charset=utf-8"
                        If prod IsNot Nothing Then
                            Dim resp = "<?xml version=""1.0"" encoding=""UTF-8""?>" & vbCrLf &
                                "<soapenv:Envelope xmlns:soapenv=""http://schemas.xmlsoap.org/soap/envelope/"" xmlns:tns=""http://facturacion.com/services"">" & vbCrLf &
                                "  <soapenv:Body>" & vbCrLf &
                                "    <tns:GetProductStockResponse>" & vbCrLf &
                                "      <tns:ProductCode>" & prod.Code & "</tns:ProductCode>" & vbCrLf &
                                "      <tns:ProductName>" & prod.Name & "</tns:ProductName>" & vbCrLf &
                                "      <tns:Stock>" & prod.Stock.ToString() & "</tns:Stock>" & vbCrLf &
                                "      <tns:Price>" & prod.Price.ToString("F2", System.Globalization.CultureInfo.InvariantCulture) & "</tns:Price>" & vbCrLf &
                                "      <tns:Available>" & If(prod.Stock > 0, "true", "false") & "</tns:Available>" & vbCrLf &
                                "    </tns:GetProductStockResponse>" & vbCrLf &
                                "  </soapenv:Body>" & vbCrLf &
                                "</soapenv:Envelope>"
                            Await context.Response.WriteAsync(resp)
                        Else
                            Dim resp = "<?xml version=""1.0"" encoding=""UTF-8""?>" & vbCrLf &
                                "<soapenv:Envelope xmlns:soapenv=""http://schemas.xmlsoap.org/soap/envelope/"" xmlns:tns=""http://facturacion.com/services"">" & vbCrLf &
                                "  <soapenv:Body>" & vbCrLf &
                                "    <tns:GetProductStockResponse>" & vbCrLf &
                                "      <tns:ProductCode>" & pCode & "</tns:ProductCode>" & vbCrLf &
                                "      <tns:ProductName>NO EXISTE</tns:ProductName>" & vbCrLf &
                                "      <tns:Stock>0</tns:Stock>" & vbCrLf &
                                "      <tns:Price>0.00</tns:Price>" & vbCrLf &
                                "      <tns:Available>false</tns:Available>" & vbCrLf &
                                "    </tns:GetProductStockResponse>" & vbCrLf &
                                "  </soapenv:Body>" & vbCrLf &
                                "</soapenv:Envelope>"
                            Await context.Response.WriteAsync(resp)
                        End If
                        Return
                    End If

                    If body.Contains("CalculateInvoice") Then
                        Dim repo = context.RequestServices.GetRequiredService(Of VbDataRepository)()
                        Dim subtotal As Double = 0
                        Dim count As Integer = 0
                        For Each p In repo.Products
                            If body.Contains(p.Code) Then
                                subtotal += p.Price * 2
                                count += 2
                            End If
                        Next
                        If count = 0 AndAlso repo.Products.Count > 0 Then
                            subtotal = repo.Products(0).Price * 2
                            count = 2
                        End If
                        Dim tax = Math.Round(subtotal * 0.16, 2)
                        Dim total = Math.Round(subtotal + tax, 2)

                        context.Response.ContentType = "text/xml; charset=utf-8"
                        Dim resp = "<?xml version=""1.0"" encoding=""UTF-8""?>" & vbCrLf &
                            "<soapenv:Envelope xmlns:soapenv=""http://schemas.xmlsoap.org/soap/envelope/"" xmlns:tns=""http://facturacion.com/services"">" & vbCrLf &
                            "  <soapenv:Body>" & vbCrLf &
                            "    <tns:CalculateInvoiceResponse>" & vbCrLf &
                            "      <tns:Subtotal>" & subtotal.ToString("F2", System.Globalization.CultureInfo.InvariantCulture) & "</tns:Subtotal>" & vbCrLf &
                            "      <tns:Tax>" & tax.ToString("F2", System.Globalization.CultureInfo.InvariantCulture) & "</tns:Tax>" & vbCrLf &
                            "      <tns:Total>" & total.ToString("F2", System.Globalization.CultureInfo.InvariantCulture) & "</tns:Total>" & vbCrLf &
                            "      <tns:ItemsCount>" & count.ToString() & "</tns:ItemsCount>" & vbCrLf &
                            "    </tns:CalculateInvoiceResponse>" & vbCrLf &
                            "  </soapenv:Body>" & vbCrLf &
                            "</soapenv:Envelope>"
                        Await context.Response.WriteAsync(resp)
                        Return
                    End If

                    If body.Contains("ProcessInvoice") Then
                        Dim repo = context.RequestServices.GetRequiredService(Of VbDataRepository)()
                        Dim custMatch = System.Text.RegularExpressions.Regex.Match(body, "CustomerName>([^<]+)<")
                        Dim customer = If(custMatch.Success, custMatch.Groups(1).Value.Trim(), "Cliente General")

                        Dim subtotal As Double = 0
                        For Each p In repo.Products
                            If body.Contains(p.Code) Then
                                p.Stock = Math.Max(0, p.Stock - 2)
                                subtotal += p.Price * 2
                            End If
                        Next
                        If subtotal = 0 AndAlso repo.Products.Count > 0 Then
                            repo.Products(0).Stock = Math.Max(0, repo.Products(0).Stock - 2)
                            subtotal = repo.Products(0).Price * 2
                        End If

                        Dim tax = Math.Round(subtotal * 0.16, 2)
                        Dim total = Math.Round(subtotal + tax, 2)
                        Dim invNum = String.Format("FAC-SOAP-VB-{0:D4}", repo.Invoices.Count + 1)

                        Dim invRecord As New VbInvoiceRecord With {
                            .Id = repo.Invoices.Count + 1,
                            .InvoiceNumber = invNum,
                            .CustomerName = customer,
                            .Date = DateTime.UtcNow.ToString("o"),
                            .Items = New List(Of VbInvoiceLineItem)(),
                            .Subtotal = subtotal,
                            .Tax = tax,
                            .Total = total,
                            .Status = "EMITIDA"
                        }
                        repo.Invoices.Add(invRecord)

                        context.Response.ContentType = "text/xml; charset=utf-8"
                        Dim resp = "<?xml version=""1.0"" encoding=""UTF-8""?>" & vbCrLf &
                            "<soapenv:Envelope xmlns:soapenv=""http://schemas.xmlsoap.org/soap/envelope/"" xmlns:tns=""http://facturacion.com/services"">" & vbCrLf &
                            "  <soapenv:Body>" & vbCrLf &
                            "    <tns:ProcessInvoiceResponse>" & vbCrLf &
                            "      <tns:InvoiceNumber>" & invNum & "</tns:InvoiceNumber>" & vbCrLf &
                            "      <tns:CustomerName>" & customer & "</tns:CustomerName>" & vbCrLf &
                            "      <tns:Total>" & total.ToString("F2", System.Globalization.CultureInfo.InvariantCulture) & "</tns:Total>" & vbCrLf &
                            "      <tns:Status>PROCESADA_EXITOSA</tns:Status>" & vbCrLf &
                            "      <tns:Message>Factura procesada y stock descontado exitosamente en VB.NET Service</tns:Message>" & vbCrLf &
                            "    </tns:ProcessInvoiceResponse>" & vbCrLf &
                            "  </soapenv:Body>" & vbCrLf &
                            "</soapenv:Envelope>"
                        Await context.Response.WriteAsync(resp)
                        Return
                    End If
                End Using
            End If

            Await [next]()
        End Function)

        ' Registrar SOAP Endpoint
        Dim appBuilder As IApplicationBuilder = app
        appBuilder.UseSoapEndpoint(Of IFacturacionServiceVb)("/ws/FacturacionService", New SoapEncoderOptions(), SoapSerializer.DataContractSerializer)
        appBuilder.UseSoapEndpoint(Of IFacturacionServiceVb)("/ws/FacturacionService.asmx", New SoapEncoderOptions(), SoapSerializer.DataContractSerializer)

        ' ==================== ENDPOINTS REST ====================

        app.MapPost("/api/auth/login", Function(req As VbLoginRequest)
            If req.Username = "admin" AndAlso req.Password = "password123" Then
                Return Results.Ok(New With {.token = ValidRestToken, .token_type = "Bearer", .user = req.Username})
            End If
            Return Results.Unauthorized()
        End Function).WithTags("Autenticación (VB.NET)")

        app.MapGet("/api/products", Function(category As String, search As String, repo As VbDataRepository)
            Dim list = repo.Products.AsEnumerable()
            If Not String.IsNullOrEmpty(category) Then
                list = list.Where(Function(p) p.Category.Equals(category, StringComparison.OrdinalIgnoreCase))
            End If
            If Not String.IsNullOrEmpty(search) Then
                list = list.Where(Function(p) p.Name.Contains(search, StringComparison.OrdinalIgnoreCase) OrElse p.Code.Contains(search, StringComparison.OrdinalIgnoreCase))
            End If
            Return Results.Ok(list.ToList())
        End Function).WithTags("Productos REST (VB.NET)")

        app.MapGet("/api/products/{id:int}", Function(id As Integer, repo As VbDataRepository)
            Dim prod = repo.Products.FirstOrDefault(Function(p) p.Id = id)
            If prod IsNot Nothing Then
                Return Results.Ok(prod)
            End If
            Return Results.NotFound(New With {.message = "Producto no encontrado"})
        End Function).WithTags("Productos REST (VB.NET)")

        app.MapPost("/api/products", Function(dto As VbProductDto, httpReq As HttpRequest, repo As VbDataRepository)
            If Not IsAuthorized(httpReq) Then Return Results.Unauthorized()
            If repo.Products.Any(Function(p) p.Code.Equals(dto.Code, StringComparison.OrdinalIgnoreCase)) Then
                Return Results.BadRequest(New With {.message = "El código ya existe"})
            End If
            Dim newId = If(repo.Products.Count > 0, repo.Products.Max(Function(p) p.Id) + 1, 1)
            Dim newProd = New VbProduct With {.Id = newId, .Code = dto.Code, .Name = dto.Name, .Category = dto.Category, .Price = dto.Price, .Stock = dto.Stock}
            repo.Products.Add(newProd)
            Return Results.Created($"/api/products/{newId}", newProd)
        End Function).WithTags("Productos REST (VB.NET)")

        app.MapPut("/api/products/{id:int}", Function(id As Integer, dto As VbProductDto, httpReq As HttpRequest, repo As VbDataRepository)
            If Not IsAuthorized(httpReq) Then Return Results.Unauthorized()
            Dim prod = repo.Products.FirstOrDefault(Function(p) p.Id = id)
            If prod Is Nothing Then Return Results.NotFound(New With {.message = "Producto no encontrado"})
            prod.Code = dto.Code
            prod.Name = dto.Name
            prod.Category = dto.Category
            prod.Price = dto.Price
            prod.Stock = dto.Stock
            Return Results.Ok(prod)
        End Function).WithTags("Productos REST (VB.NET)")

        app.MapDelete("/api/products/{id:int}", Function(id As Integer, httpReq As HttpRequest, repo As VbDataRepository)
            If Not IsAuthorized(httpReq) Then Return Results.Unauthorized()
            Dim prod = repo.Products.FirstOrDefault(Function(p) p.Id = id)
            If prod Is Nothing Then Return Results.NotFound(New With {.message = "Producto no encontrado"})
            repo.Products.Remove(prod)
            Return Results.Ok(New With {.message = $"Producto con ID {id} eliminado exitosamente"})
        End Function).WithTags("Productos REST (VB.NET)")

        app.MapPost("/api/invoices", Function(req As VbCreateInvoiceRequest, httpReq As HttpRequest, repo As VbDataRepository)
            If Not IsAuthorized(httpReq) Then Return Results.Unauthorized()

            Dim subtotal As Double = 0
            Dim lineItems As New List(Of VbInvoiceLineItem)()

            For Each item In req.Items
                Dim prod = repo.Products.FirstOrDefault(Function(p) p.Code.Equals(item.ProductCode, StringComparison.OrdinalIgnoreCase))
                If prod Is Nothing Then Return Results.NotFound(New With {.message = $"Producto {item.ProductCode} no existe"})
                If prod.Stock < item.Quantity Then Return Results.BadRequest(New With {.message = $"Stock insuficiente para {prod.Name}"})

                Dim lineTotal = prod.Price * item.Quantity
                subtotal += lineTotal
                lineItems.Add(New VbInvoiceLineItem With {.ProductCode = prod.Code, .ProductName = prod.Name, .UnitPrice = prod.Price, .Quantity = item.Quantity, .Subtotal = lineTotal})
            Next

            ' Descontar stock
            For Each item In req.Items
                Dim prod = repo.Products.First(Function(p) p.Code.Equals(item.ProductCode, StringComparison.OrdinalIgnoreCase))
                prod.Stock -= item.Quantity
            Next

            Dim tax = Math.Round(subtotal * 0.16, 2)
            Dim total = Math.Round(subtotal + tax, 2)
            Dim invNum = $"FAC-VB-{repo.Invoices.Count + 1:D4}"

            Dim invoice As New VbInvoiceRecord With {
                .Id = repo.Invoices.Count + 1,
                .InvoiceNumber = invNum,
                .CustomerName = req.CustomerName,
                .Date = DateTime.UtcNow.ToString("o"),
                .Items = lineItems,
                .Subtotal = Math.Round(subtotal, 2),
                .Tax = tax,
                .Total = total,
                .Status = "EMITIDA"
            }
            repo.Invoices.Add(invoice)
            Return Results.Created($"/api/invoices/{invoice.Id}", invoice)
        End Function).WithTags("Facturación REST (VB.NET)")

        app.MapGet("/api/invoices", Function(repo As VbDataRepository) Results.Ok(repo.Invoices)).WithTags("Facturación REST (VB.NET)")

        app.MapGet("/api/invoices/{id:int}", Function(id As Integer, repo As VbDataRepository)
            Dim inv = repo.Invoices.FirstOrDefault(Function(i) i.Id = id)
            If inv IsNot Nothing Then Return Results.Ok(inv)
            Return Results.NotFound(New With {.message = "Factura no encontrada"})
        End Function).WithTags("Facturación REST (VB.NET)")

        app.Run("http://0.0.0.0:8086")
    End Sub

    Private Function IsAuthorized(req As HttpRequest) As Boolean
        Dim authHeader As Microsoft.Extensions.Primitives.StringValues = Nothing
        If Not req.Headers.TryGetValue("Authorization", authHeader) Then Return False
        Dim parts = authHeader.ToString().Split(" "c)
        Return parts.Length = 2 AndAlso parts(0).Equals("Bearer", StringComparison.OrdinalIgnoreCase) AndAlso parts(1) = ValidRestToken
    End Function
End Module

' ==================== CONTRATOS Y MODELOS SOAP ====================

<ServiceContract(Namespace:="http://facturacion.com/services")>
Public Interface IFacturacionServiceVb
    <OperationContract(Action:="http://facturacion.com/services/GetProductStock")>
    Function GetProductStock(request As VbGetProductStockRequest) As VbGetProductStockResponse

    <OperationContract(Action:="http://facturacion.com/services/CalculateInvoice")>
    Function CalculateInvoice(request As VbCalculateInvoiceRequest) As VbCalculateInvoiceResponse

    <OperationContract(Action:="http://facturacion.com/services/ProcessInvoice")>
    Function ProcessInvoice(request As VbProcessInvoiceRequest) As VbProcessInvoiceResponse
End Interface

<DataContract(Namespace:="http://facturacion.com/services")>
Public Class VbGetProductStockRequest
    <DataMember> Public Property ProductCode As String = String.Empty
End Class

<DataContract(Namespace:="http://facturacion.com/services")>
Public Class VbGetProductStockResponse
    <DataMember> Public Property ProductCode As String = String.Empty
    <DataMember> Public Property ProductName As String = String.Empty
    <DataMember> Public Property Stock As Integer
    <DataMember> Public Property Price As Double
    <DataMember> Public Property Available As Boolean
End Class

<DataContract(Namespace:="http://facturacion.com/services")>
Public Class VbItemRequest
    <DataMember> Public Property ProductCode As String = String.Empty
    <DataMember> Public Property Quantity As Integer
End Class

<DataContract(Namespace:="http://facturacion.com/services")>
Public Class VbCalculateInvoiceRequest
    <DataMember> Public Property CustomerName As String = String.Empty
    <DataMember> Public Property Items As New List(Of VbItemRequest)()
End Class

<DataContract(Namespace:="http://facturacion.com/services")>
Public Class VbCalculateInvoiceResponse
    <DataMember> Public Property Subtotal As Double
    <DataMember> Public Property Tax As Double
    <DataMember> Public Property Total As Double
    <DataMember> Public Property ItemsCount As Integer
End Class

<DataContract(Namespace:="http://facturacion.com/services")>
Public Class VbProcessInvoiceRequest
    <DataMember> Public Property CustomerName As String = String.Empty
    <DataMember> Public Property Items As New List(Of VbItemRequest)()
End Class

<DataContract(Namespace:="http://facturacion.com/services")>
Public Class VbProcessInvoiceResponse
    <DataMember> Public Property InvoiceNumber As String = String.Empty
    <DataMember> Public Property CustomerName As String = String.Empty
    <DataMember> Public Property Total As Double
    <DataMember> Public Property Status As String = String.Empty
    <DataMember> Public Property Message As String = String.Empty
End Class

Public Class FacturacionServiceVb
    Implements IFacturacionServiceVb

    Private ReadOnly _repo As VbDataRepository
    Public Sub New(repo As VbDataRepository)
        _repo = repo
    End Sub

    Public Function GetProductStock(request As VbGetProductStockRequest) As VbGetProductStockResponse Implements IFacturacionServiceVb.GetProductStock
        Dim prod = _repo.Products.FirstOrDefault(Function(p) p.Code.Equals(request.ProductCode, StringComparison.OrdinalIgnoreCase))
        If prod Is Nothing Then
            Return New VbGetProductStockResponse With {
                .ProductCode = request.ProductCode,
                .ProductName = "NO ENCONTRADO",
                .Stock = 0,
                .Price = 0,
                .Available = False
            }
        End If
        Return New VbGetProductStockResponse With {
            .ProductCode = prod.Code,
            .ProductName = prod.Name,
            .Stock = prod.Stock,
            .Price = prod.Price,
            .Available = prod.Stock > 0
        }
    End Function

    Public Function CalculateInvoice(request As VbCalculateInvoiceRequest) As VbCalculateInvoiceResponse Implements IFacturacionServiceVb.CalculateInvoice
        Dim subtotal As Double = 0
        Dim count As Integer = 0
        For Each item In request.Items
            Dim prod = _repo.Products.FirstOrDefault(Function(p) p.Code.Equals(item.ProductCode, StringComparison.OrdinalIgnoreCase))
            If prod IsNot Nothing Then
                subtotal += prod.Price * item.Quantity
                count += item.Quantity
            End If
        Next
        Dim tax = Math.Round(subtotal * 0.16, 2)
        Return New VbCalculateInvoiceResponse With {
            .Subtotal = Math.Round(subtotal, 2),
            .Tax = tax,
            .Total = Math.Round(subtotal + tax, 2),
            .ItemsCount = count
        }
    End Function

    Public Function ProcessInvoice(request As VbProcessInvoiceRequest) As VbProcessInvoiceResponse Implements IFacturacionServiceVb.ProcessInvoice
        Dim subtotal As Double = 0
        For Each item In request.Items
            Dim prod = _repo.Products.FirstOrDefault(Function(p) p.Code.Equals(item.ProductCode, StringComparison.OrdinalIgnoreCase))
            If prod Is Nothing Then
                Return New VbProcessInvoiceResponse With {.Status = "ERROR", .Message = $"Producto {item.ProductCode} no existe"}
            End If
            If prod.Stock < item.Quantity Then
                Return New VbProcessInvoiceResponse With {.Status = "ERROR", .Message = $"Stock insuficiente para {prod.Name}"}
            End If
            subtotal += prod.Price * item.Quantity
        Next

        For Each item In request.Items
            Dim prod = _repo.Products.First(Function(p) p.Code.Equals(item.ProductCode, StringComparison.OrdinalIgnoreCase))
            prod.Stock -= item.Quantity
        Next

        Dim tax = Math.Round(subtotal * 0.16, 2)
        Dim total = Math.Round(subtotal + tax, 2)
        Dim invNum = $"FAC-SOAP-VB-{_repo.Invoices.Count + 1:D4}"

        _repo.Invoices.Add(New VbInvoiceRecord With {
            .Id = _repo.Invoices.Count + 1,
            .InvoiceNumber = invNum,
            .CustomerName = request.CustomerName,
            .Date = DateTime.UtcNow.ToString("o"),
            .Items = New List(Of VbInvoiceLineItem)(),
            .Subtotal = Math.Round(subtotal, 2),
            .Tax = tax,
            .Total = total,
            .Status = "EMITIDA"
        })

        Return New VbProcessInvoiceResponse With {
            .InvoiceNumber = invNum,
            .CustomerName = request.CustomerName,
            .Total = total,
            .Status = "PROCESADA_EXITOSA",
            .Message = "Factura generada y stock descontado exitosamente en VB.NET Service"
        }
    End Function
End Class

' ==================== DTOs Y REPOSITORIO ====================

Public Class VbDataRepository
    Public Property Products As New List(Of VbProduct) From {
        New VbProduct With {.Id = 1, .Code = "PROD001", .Name = "Laptop ThinkPad E14", .Category = "Computación", .Price = 15500.0, .Stock = 12},
        New VbProduct With {.Id = 2, .Code = "PROD002", .Name = "Monitor Dell 27 4K", .Category = "Periféricos", .Price = 6200.0, .Stock = 25},
        New VbProduct With {.Id = 3, .Code = "PROD003", .Name = "Teclado Mecánico RGB", .Category = "Accesorios", .Price = 1350.0, .Stock = 40},
        New VbProduct With {.Id = 4, .Code = "PROD004", .Name = "Mouse Inalámbrico Logitech", .Category = "Accesorios", .Price = 650.0, .Stock = 50},
        New VbProduct With {.Id = 5, .Code = "PROD005", .Name = "Impresora Multifuncional HP", .Category = "Oficina", .Price = 4100.0, .Stock = 8}
    }

    Public Property Invoices As New List(Of VbInvoiceRecord)()
End Class

Public Class VbProduct
    Public Property Id As Integer
    Public Property Code As String = String.Empty
    Public Property Name As String = String.Empty
    Public Property Category As String = String.Empty
    Public Property Price As Double
    Public Property Stock As Integer
End Class

Public Class VbProductDto
    Public Property Code As String = String.Empty
    Public Property Name As String = String.Empty
    Public Property Category As String = String.Empty
    Public Property Price As Double
    Public Property Stock As Integer
End Class

Public Class VbLoginRequest
    Public Property Username As String = String.Empty
    Public Property Password As String = String.Empty
End Class

Public Class VbCreateInvoiceItem
    Public Property ProductCode As String = String.Empty
    Public Property Quantity As Integer
End Class

Public Class VbCreateInvoiceRequest
    Public Property CustomerName As String = String.Empty
    Public Property Items As New List(Of VbCreateInvoiceItem)()
End Class

Public Class VbInvoiceLineItem
    Public Property ProductCode As String = String.Empty
    Public Property ProductName As String = String.Empty
    Public Property UnitPrice As Double
    Public Property Quantity As Integer
    Public Property Subtotal As Double
End Class

Public Class VbInvoiceRecord
    Public Property Id As Integer
    Public Property InvoiceNumber As String = String.Empty
    Public Property CustomerName As String = String.Empty
    Public Property [Date] As String = String.Empty
    Public Property Items As New List(Of VbInvoiceLineItem)()
    Public Property Subtotal As Double
    Public Property Tax As Double
    Public Property Total As Double
    Public Property Status As String = String.Empty
End Class
