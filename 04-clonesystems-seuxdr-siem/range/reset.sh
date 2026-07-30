#!/usr/bin/env bash
# Reset the scenario 04 target between trainee sessions.
#   ./reset.sh          clear database + certificates, keep the clone and model
#   ./reset.sh --full   also drop the clone and the Ollama model volume (~9GB re-download)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$here/.env" ]] || { echo "!! no .env"; exit 1; }
set -a; source "$here/.env"; set +a
: "${RANGE_INSTALL_DIR:=/srv/seuxdr}"
: "${RANGE_PRODUCT_REF:=00a95ad}"
full=0; [[ "${1:-}" == "--full" ]] && full=1

say() { printf '\n[reset] %s\n' "$*"; }
[[ -d "$RANGE_INSTALL_DIR" ]] || { echo "!! $RANGE_INSTALL_DIR not found — nothing to reset"; exit 1; }
cd "$RANGE_INSTALL_DIR"

say "stopping the stack"
docker compose down --remove-orphans || true

say "clearing databases and certificates"
[[ -f clear-db.sh ]]     && sh clear-db.sh     || true
[[ -f delete-certs.sh ]] && sh delete-certs.sh || true
rm -rf /tmp/seuxdr-logs 2>/dev/null || true

if [[ "$full" -eq 1 ]]; then
  say "--full: removing the model volume and the clone"
  docker volume rm "$(basename "$RANGE_INSTALL_DIR")_ollama_models" 2>/dev/null \
    || docker volume rm seuxdr_ollama_models 2>/dev/null || true
  cd /
  sudo rm -rf "$RANGE_INSTALL_DIR"
  say "done. run deploy.sh for a clean build."
  exit 0
fi

say "restoring the working tree to $RANGE_PRODUCT_REF"
git checkout --quiet --force "$RANGE_PRODUCT_REF"
git clean -fdq -e manager/certs -e agent/certs -e manager_front/certs || true

say "regenerating certificates"
sh gen-certs.sh

say "done. bring it back with: $here/deploy.sh"
