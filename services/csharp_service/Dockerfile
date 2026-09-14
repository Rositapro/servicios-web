FROM mcr.microsoft.com/dotnet/runtime-deps:9.0

WORKDIR /app

COPY ./publish/ .

RUN chmod +x ./csharp_service

ENV ASPNETCORE_URLS=http://0.0.0.0:8085
EXPOSE 8085

ENTRYPOINT ["./csharp_service"]
