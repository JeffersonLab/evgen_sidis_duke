#!/bin/bash
# Start JupyterLab for this project.
#
#   ./start_jupyter.sh [port] [--noauth]     # default port 8888
#
# Default is token authentication with a *persistent* token, kept in
# ~/.jupyter/solid_token (mode 600) and generated on first run. Because it does
# not change between restarts you can bookmark the printed ?token=... URL once
# and never type a password again.
#
#   --noauth   disable authentication completely (no token, no password).
#              Only the loopback interface is bound either way, but with
#              --noauth any other account on this machine can connect to the
#              port and run code as you.
#
# Reach it from your laptop over an SSH tunnel:
#   ssh -L 8888:127.0.0.1:8888 <this host>    then open the printed URL
#
# Stop it with Ctrl-C, or from another shell:
#   with auth:    jupyter server stop <port>
#   with --noauth: kill <the PID printed at startup>   (`jupyter server stop`
#                  is refused with HTTP 403 when auth is off)

cd "$(dirname "$0")" || exit 1

PORT=8888
AUTH=1
for arg in "$@"; do
    case "$arg" in
        --noauth) AUTH=0 ;;
        --auth)   AUTH=1 ;;
        [0-9]*)   PORT="$arg" ;;
        *) echo "usage: $0 [port] [--noauth]" >&2; exit 1 ;;
    esac
done

# module is not initialized in a non-login shell; setup.sh needs it for ROOT
if [ -f /usr/share/Modules/init/bash ]; then
    . /usr/share/Modules/init/bash
fi
. ./setup.sh

if [ "$AUTH" = 1 ]; then
    TOKEN_FILE="$HOME/.jupyter/solid_token"
    if [ ! -s "$TOKEN_FILE" ]; then
        mkdir -p "$(dirname "$TOKEN_FILE")" || exit 1
        ( umask 077; python3 -c 'import secrets; print(secrets.token_hex(24))' > "$TOKEN_FILE" ) || exit 1
        echo "generated a new token in $TOKEN_FILE"
    fi
    chmod 600 "$TOKEN_FILE"
    TOKEN=$(cat "$TOKEN_FILE")
    echo "JupyterLab on http://127.0.0.1:${PORT}/lab?token=${TOKEN}"
    echo "token from $TOKEN_FILE -- stop with Ctrl-C or 'jupyter server stop ${PORT}'"
    exec jupyter lab --no-browser --ip=127.0.0.1 --port="$PORT" \
        --IdentityProvider.token="$TOKEN"
else
    echo "JupyterLab on http://127.0.0.1:${PORT}/  (authentication DISABLED)"
    echo "PID $$ -- stop with Ctrl-C, or 'kill $$' from another shell"
    exec jupyter lab --no-browser --ip=127.0.0.1 --port="$PORT" \
        --IdentityProvider.token='' \
        --ServerApp.password='' \
        --ServerApp.password_required=False
fi
