#!/usr/bin/env bash
# Deploy the SEUXDR target for scenario 04 on a cyber-range VM.
#
# Idempotent: re-running re-checks-out the ref and rebuilds without wiping
# trainee data. Use reset.sh to clear state.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$here/.env" ]] || { echo "!! no .env — copy .env.example and edit it first"; exit 1; }
set -a; source "$here/.env"; set +a

: "${RANGE_HOST_IP:?set RANGE_HOST_IP in .env}"
: "${RANGE_INSTALL_DIR:=/srv/seuxdr}"
: "${RANGE_PRODUCT_REF:=00a95ad}"
: "${RANGE_HOSTNAME:=seuxdr-range}"
: "${RANGE_GPU:=off}"
: "${RANGE_MODEL:=phi4:14b}"
: "${RANGE_STARTUP_MODE:=TEST}"

say() { printf '\n[deploy] %s\n' "$*"; }

for tool in git docker openssl; do
  command -v "$tool" >/dev/null || { echo "!! $tool not found"; exit 1; }
done
docker compose version >/dev/null 2>&1 || { echo "!! docker compose v2 required"; exit 1; }

# ---- 1. fetch the product at the pinned ref ---------------------------------
if [[ -d "$RANGE_INSTALL_DIR/.git" ]]; then
  say "updating $RANGE_INSTALL_DIR"
  git -C "$RANGE_INSTALL_DIR" fetch --all --tags --quiet
else
  say "cloning $RANGE_PRODUCT_REPO -> $RANGE_INSTALL_DIR"
  sudo mkdir -p "$(dirname "$RANGE_INSTALL_DIR")"
  sudo chown "$(id -u):$(id -g)" "$(dirname "$RANGE_INSTALL_DIR")"
  git clone --quiet "$RANGE_PRODUCT_REPO" "$RANGE_INSTALL_DIR"
fi
git -C "$RANGE_INSTALL_DIR" checkout --quiet --force "$RANGE_PRODUCT_REF"
say "deployed ref: $(git -C "$RANGE_INSTALL_DIR" rev-parse --short HEAD) ($RANGE_PRODUCT_REF)"

cd "$RANGE_INSTALL_DIR"

# ---- 2. point the product at this host --------------------------------------
# Both files ship with a hard-coded 192.168.0.154.
say "setting host IP to $RANGE_HOST_IP"
if [[ -f localhost.ext ]]; then
  sed -i.range-bak -E "s/^IP\.1[[:space:]]*=.*/IP.1 = ${RANGE_HOST_IP}/" localhost.ext
fi
if [[ -f manager/manager.yaml ]]; then
  sed -i.range-bak -E "s/192\.168\.0\.154/${RANGE_HOST_IP}/g" manager/manager.yaml
fi

# ---- 3. range adjustments to the compose file -------------------------------
python3 - "$RANGE_HOSTNAME" "$RANGE_GPU" "$RANGE_MODEL" <<'PY'
import re, shutil, sys
from pathlib import Path

hostname, gpu, model = sys.argv[1], sys.argv[2].lower(), sys.argv[3]
p = Path("docker-compose.yml")
if not Path("docker-compose.yml.range-bak").exists():
    shutil.copy(p, "docker-compose.yml.range-bak")

lines = p.read_text().splitlines(keepends=True)
notes = []


def indent(line):
    return len(line) - len(line.lstrip(" \t"))


# The compose file hard-codes a developer's motherboard model as the hostname.
for i, line in enumerate(lines):
    if re.match(r"^\s*hostname:", line):
        lines[i] = re.sub(r"(^\s*hostname:\s*).*$", r"\g<1>" + hostname, line.rstrip("\n")) + "\n"
        notes.append("hostname -> " + hostname)
        break

if gpu == "off":
    # A hard device reservation makes compose refuse to start Ollama on a host
    # with no NVIDIA GPU instead of falling back to CPU. Drop the block by
    # indentation - a regex here will happily eat the sibling keys that follow.
    out, i, removed = [], 0, 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*devices:\s*$", line):
            base = indent(line)
            j = i + 1
            block = []
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() and indent(nxt) <= base:
                    break
                block.append(nxt)
                j += 1
            if any("nvidia" in b for b in block):
                removed = len(block) + 1
                i = j
                continue
        out.append(line)
        i += 1
    if removed:
        lines = out
        notes.append("removed the NVIDIA device reservation, %d lines (CPU-only)" % removed)

text = "".join(lines)
if model != "phi4:14b":
    text = text.replace("phi4:14b", model)
    notes.append("model -> " + model)

p.write_text(text)
print("  " + "\n  ".join(notes) if notes else "  no compose changes needed")
PY

# ---- 4. certificates --------------------------------------------------------
say "generating certificates"
sh gen-certs.sh

# ---- 5. bring the stack up --------------------------------------------------
say "building and starting (first run pulls ~9GB of model — expect 25-40 min)"
docker compose up --build -d

# ---- 6. install Wazuh inside the manager ------------------------------------
say "running startup.sh $RANGE_STARTUP_MODE (Wazuh all-in-one, 10-15 min)"
docker exec -i seuxdr-manager /usr/local/bin/startup.sh "$RANGE_STARTUP_MODE"

say "done. verify with: $here/verify.sh"
echo "  front end   https://${RANGE_HOST_IP}:8080   (unreachable in baseline mode: no /api/login route)"
echo "  manager API https://${RANGE_HOST_IP}:8443"
echo "  enrolment   ${RANGE_HOST_IP}:8081 (mTLS)"
