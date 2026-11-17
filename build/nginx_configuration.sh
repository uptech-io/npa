#!/bin/bash

NGINX_VERSION_CONF_INPUT_PATH=/tmp/nginx.sourcefile.ver
NGINX_VERSION_CONF_OUTPUT_PATH=/tmp/nginx.sourcefile.conf
BUILD_OUTPUT_DIR=out

nginx -V &> "${NGINX_VERSION_CONF_INPUT_PATH}"

dos2unix ${NGINX_VERSION_CONF_INPUT_PATH}
$(dirname $0)/nginx_extractor.sh -i ${NGINX_VERSION_CONF_INPUT_PATH} -o ${NGINX_VERSION_CONF_OUTPUT_PATH}

if [[ ${BUILD_OUTPUT_DIR} != /* ]]; then
    BUILD_OUTPUT_DIR=$(pwd)/${BUILD_OUTPUT_DIR}
fi

source ${NGINX_VERSION_CONF_OUTPUT_PATH}
CURRENT_PWD=$(pwd)

mkdir -p ${BUILD_OUTPUT_DIR}
cd ${BUILD_OUTPUT_DIR}

wget --no-check-certificate https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz
if [[ $? != 0 ]]; then
    echo "Failed to download NGINX source code. Path used: 'https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz'"
    exit 1
fi

tar -xzvf nginx-${NGINX_VERSION}.tar.gz
if [[ $? != 0 ]]; then
    echo "Failed to untar NGINX source code. Tar file: 'nginx-${NGINX_VERSION}.tar.gz'"
    exit 1
fi

#######################################
NB_VER=master
HMNM_VER=v0.40
ACME=v0.4.1
OIDC=0.8.0

git clone --depth 1 --recurse-submodules -j8 https://github.com/google/ngx_brotli --branch "${NB_VER}" ngx_brotli
git clone --depth 1 https://github.com/openresty/headers-more-nginx-module --branch "${HMNM_VER}" headers-more-nginx-module
git clone --depth 1 https://github.com/nginx/nginx-acme --branch "${ACME}" nginx-acme
git clone --recurse-submodules https://github.com/kjdev/nginx-oidc.git --branch "${OIDC}" oidc
#######################################

rm -f nginx-${NGINX_VERSION}.tar.gz
mv nginx-${NGINX_VERSION} nginx-src
cd nginx-src

echo "Configuring nginx compiler: ./configure ${CONFIGURE_OPT} --with-cc-opt=\"${EXTRA_CC_OPT} ${LOCAL_CC_OPT}\" && touch configured.ok..."

./configure ${CONFIGURE_OPT} \
    --with-cc-opt="${EXTRA_CC_OPT} ${LOCAL_CC_OPT}" \
    --add-dynamic-module="${BUILD_OUTPUT_DIR}/ngx_brotli" \
    --add-dynamic-module="${BUILD_OUTPUT_DIR}/headers-more-nginx-module" \
    --add-dynamic-module="${BUILD_OUTPUT_DIR}/nginx-acme" \
    --add-dynamic-module="${BUILD_OUTPUT_DIR}/oidc"
make -j"$(nproc)" modules

mv objs/*.so /usr/lib/nginx/modules
