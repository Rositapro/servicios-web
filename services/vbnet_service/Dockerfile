FROM mcr.microsoft.com/dotnet/runtime-deps:9.0

WORKDIR /app

COPY ./publish/ .

RUN chmod +x ./vbnet_service

ENV ASPNETCORE_URLS=http://0.0.0.0:8086
EXPOSE 8086

ENTRYPOINT ["./vbnet_service"]
