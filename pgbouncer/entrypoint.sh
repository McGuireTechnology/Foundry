#!/bin/sh
set -eu

DB_USER="${DB_USER:-${POSTGRES_USER:-postgres}}"
DB_PASSWORD="${DB_PASSWORD:-${POSTGRES_PASSWORD:-postgres}}"
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-${POSTGRES_DB:-vortex}}"
POOL_MODE="${POOL_MODE:-transaction}"
MAX_CLIENT_CONN="${MAX_CLIENT_CONN:-500}"
DEFAULT_POOL_SIZE="${DEFAULT_POOL_SIZE:-20}"
LISTEN_PORT="${LISTEN_PORT:-5432}"
LISTEN_ADDR="${LISTEN_ADDR:-0.0.0.0}"
AUTH_TYPE="${AUTH_TYPE:-md5}"

mkdir -p /etc/pgbouncer

if [ ! -f /etc/pgbouncer/userlist.txt ]; then
  printf "\"%s\" \"%s\"\n" "$DB_USER" "$DB_PASSWORD" > /etc/pgbouncer/userlist.txt
fi

cat > /etc/pgbouncer/pgbouncer.ini <<EOF
[databases]
${DB_NAME} = host=${DB_HOST} port=${DB_PORT} dbname=${DB_NAME} user=${DB_USER} password=${DB_PASSWORD}

[pgbouncer]
listen_addr = ${LISTEN_ADDR}
listen_port = ${LISTEN_PORT}
auth_type = ${AUTH_TYPE}
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = ${POOL_MODE}
max_client_conn = ${MAX_CLIENT_CONN}
default_pool_size = ${DEFAULT_POOL_SIZE}
admin_users = ${DB_USER}
ignore_startup_parameters = extra_float_digits
EOF

exec "$@"
