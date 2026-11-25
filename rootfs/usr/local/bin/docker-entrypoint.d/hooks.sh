# shellcheck shell=bash

function load_nftables_configs() {
    local hooks_dir="${1:?hooks_dir required}"
    local config_dir="${hooks_dir}/nftables.d"
    
    local -a nft_args=()
    local wan_if="$(wan_iface)"

    if [[ -n "${wan_if}" ]]; then
        nft_args+=(--define "wan_iface=${wan_if}")
    fi

    log "Loading nftables basic rules..."
    nft "${nft_args[@]}" -f /etc/nftables.nft || {
        log "Error: nftables base rules failed to load (is NET_ADMIN granted?)."
        exit 1
    }

    log "Loading nftables configurations from ${config_dir}"
    if [[ -d "${config_dir}" ]]; then
        local file

        for file in "${config_dir}"/*.nft; do
            [[ -f "${file}" ]] || continue
            log "Applying nftables configuration: ${file}"
            nft  "${nft_args[@]}" -f "${file}"
        done
    fi
}

function run_bash_scripts() {
    local hooks_dir="${1:?hooks_dir required}"
    local scripts_dir="${hooks_dir}/scripts.d"

    log "Executing bash scripts in ${scripts_dir}"
    if [[ -d "${scripts_dir}" ]]; then
        local script

        for script in "${scripts_dir}"/*.sh; do
            [[ -f "${script}" ]] || continue
            log "Running script: ${script}"
            bash "${script}"
        done
    fi
}
