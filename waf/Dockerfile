# Это на будущее, добавить сюда надо еще сборку modsec модуля и через consul управление балансировкой нагрузки
# также предусмотреть TLS сертификаты

FROM buildpack-deps:bullseye

ENV NGINX_VERSION nginx-1.23.2

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y ca-certificates openssl libssl-dev git && \
    rm -rf /var/lib/apt/lists/*

# Создаем пользователя и группу nginx
RUN groupadd -r nginx && \
    useradd -r -g nginx -s /bin/false nginx

# Скачиваем и распаковываем исходники Nginx
RUN mkdir -p /tmp/build/nginx && \
    cd /tmp/build/nginx && \
    wget -O ${NGINX_VERSION}.tar.gz https://nginx.org/download/${NGINX_VERSION}.tar.gz && \
    tar -zxf ${NGINX_VERSION}.tar.gz

# Клонируем репозиторий upsync модуля (для коннекта с Consul)
RUN git clone https://github.com/weibocom/nginx-upsync-module.git /tmp/build/nginx-upsync-module

# Собираем Nginx
RUN cd /tmp/build/nginx/${NGINX_VERSION} && \
    ./configure \
        --sbin-path=/usr/local/sbin/nginx \
        --conf-path=/etc/nginx/nginx.conf \
        --error-log-path=/var/log/nginx/error.log \
        --pid-path=/var/run/nginx/nginx.pid \
        --lock-path=/var/lock/nginx/nginx.lock \
        --http-log-path=/var/log/nginx/access.log \
        --http-client-body-temp-path=/tmp/nginx-client-body \
        --with-http_ssl_module \
        --with-threads \
        --with-ipv6 \
        --add-dynamic-module=/tmp/build/nginx-upsync-module \
        --with-debug && \
    make -j $(getconf _NPROCESSORS_ONLN) && \
    make install && \
    mkdir -p /var/lock/nginx && \
    mkdir -p /usr/local/nginx/conf/servers && \
    mkdir -p /usr/local/nginx/proxy_temp && \
    chown -R nginx:nginx /usr/local/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /var/run/nginx && \
    rm -rf /tmp/build

# Перенаправляем логи в стандартный вывод контейнера
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Установка Nginx-конфига
COPY nginx.conf /etc/nginx/nginx.conf

# Устанавливаем владельца для конфигурации NGINX
RUN chown nginx:nginx /etc/nginx/nginx.conf

EXPOSE 80

# Запуск NGINX от пользователя nginx
USER nginx

CMD ["nginx", "-g", "daemon off;"]
