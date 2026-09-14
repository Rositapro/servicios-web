FROM php:8.2-cli-alpine

RUN apk add --no-cache libxml2-dev \
    && docker-php-ext-install soap simplexml

WORKDIR /app

COPY . .

EXPOSE 8083

CMD ["php", "-S", "0.0.0.0:8083", "index.php"]
