FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY styles/ /usr/share/nginx/html/styles/
COPY app.js /usr/share/nginx/html/app.js

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
