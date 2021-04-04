FROM nginx:mainline-alpine

WORKDIR /var/www
COPY ./app/static ./static
COPY ./nginx.conf.tmpl /nginx.conf.tmpl

ENV HOSTNAME= \
    HTTP_PORT=80 \
    YOTTER_ADDRESS=http://127.0.0.1:5000 \
    YTPROXY_ADDRESS=http://unix:/var/run/ytproxy/http-proxy.sock

CMD ["/bin/sh", "-c", "envsubst '${HOSTNAME} ${HTTP_PORT} ${YOTTER_ADDRESS} ${YTPROXY_ADDRESS}' < /nginx.conf.tmpl > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
