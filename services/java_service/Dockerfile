FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /app
COPY FacturacionJavaService.java .
RUN javac -d . FacturacionJavaService.java

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/com ./com
COPY FacturacionService.wsdl .

EXPOSE 8081

CMD ["java", "com.facturacion.FacturacionJavaService"]
