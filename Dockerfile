FROM ghcr.io/openappsec/agent-unified:1.1.36

LABEL br.com.uptech.image.name="@uptech/nginx-proxy-agent"
LABEL br.com.uptech.image.vendor="UPTECH"

ENV UV_NO_DEV=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN set -eux; \
	\
	apk add --no-cache \
		tzdata \
		nftables \
		fail2ban \
		logrotate \
		bash \
		supervisor \
		hiredis \
		curl \
		bind-tools \
	; \
	\
	ln -sf /usr/share/zoneinfo/America/Recife /etc/localtime; \
    mkdir -p /var/log/supervisor

COPY --chmod=755 build /build

RUN set -eux; \
	\
	apk add --no-cache --virtual .build-deps \
		build-base \
		cargo \
		rust \
		git \
		cmake \
		linux-headers \
		clang-dev \
		libatomic_ops-dev \
		luajit-dev \
		pcre2-dev \
		pcre-dev \
		gd-dev \
		libxslt-dev \
		libxml2-dev \
		zlib-dev \
		brotli-dev \
		zstd-dev \
		openssl-dev \
		geoip-dev \
		libmaxminddb-dev \
		openldap-dev \
		perl-dev \
		jansson-dev \
		hiredis-dev \
	; \
	\
	cd /build; \
	./nginx_configuration.sh; \
	\
	cd /; \
	rm -rf /build /root/.cargo; \
	\
	apk del .build-deps

COPY rootfs/app/pyproject.toml rootfs/app/uv.lock rootfs/app/.python-version ./

RUN uv sync --locked --no-dev --compile-bytecode

COPY rootfs/ /

RUN chmod +x /usr/local/bin/* && \
	chmod 0644 /etc/logrotate.d/nginx && \
	rm -rf /etc/fail2ban/jail.d && \
    ln -s /data/fail2ban/jail.d /etc/fail2ban/jail.d && \
	ln -s /data/cp /etc/cp && \
	ln -s /data/log/nano_agent /var/log/nano_agent

HEALTHCHECK --interval=10s --timeout=3s --start-period=180s --retries=3 \
	CMD curl -sS -o /dev/null --noproxy '*' --max-time 2 http://127.0.0.1/; [ $? -ne 7 ]

ENTRYPOINT ["docker-entrypoint"]
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
