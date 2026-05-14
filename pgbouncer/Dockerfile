FROM alpine:3.22

ARG PGBOUNCER_VERSION=1.25.2

COPY pgbouncer/entrypoint.sh /entrypoint.sh

RUN set -eux; \
    apk add --no-cache --virtual .build-deps \
      build-base \
      autoconf \
      automake \
      libtool \
      pkgconf \
      linux-headers \
      libevent-dev \
      openssl-dev \
      c-ares-dev \
      pandoc \
      curl \
      tar; \
    apk add --no-cache \
      libevent \
      openssl \
      c-ares \
      tini; \
    curl -fsSL "https://www.pgbouncer.org/downloads/files/${PGBOUNCER_VERSION}/pgbouncer-${PGBOUNCER_VERSION}.tar.gz" -o /tmp/pgbouncer.tar.gz; \
    mkdir -p /tmp/src; \
    tar -xzf /tmp/pgbouncer.tar.gz -C /tmp/src --strip-components=1; \
    cd /tmp/src; \
    ./configure --prefix=/usr/local; \
    make -j"$(getconf _NPROCESSORS_ONLN)"; \
    make install; \
    addgroup -S pgbouncer; \
    adduser -S -G pgbouncer pgbouncer; \
    mkdir -p /etc/pgbouncer; \
    chown -R pgbouncer:pgbouncer /etc/pgbouncer; \
    chmod +x /entrypoint.sh; \
    cd /; \
    rm -rf /tmp/src /tmp/pgbouncer.tar.gz; \
    apk del .build-deps

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]
USER pgbouncer
CMD ["pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]
