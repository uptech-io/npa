# shellcheck shell=bash

SUPERVISOR_CONF=/etc/supervisor/supervisord.conf

INSTANCE_DIR=/data
HOOKS_DIR="${INSTANCE_DIR}/entrypoint-hooks.d"

function log() {
    echo "$(date +"%Y-%m-%d %T") $1"
}

function wan_iface() {
    awk '$2 == 00000000 {print $1}' /proc/net/route
}
