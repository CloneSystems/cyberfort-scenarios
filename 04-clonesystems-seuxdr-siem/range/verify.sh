#!/usr/bin/env bash
# Health-check the scenario 04 target and report which mode is deployed.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$here/.env" ]] && { set -a; source "$here/.env"; set +a; }
: "${RANGE_HOST_IP:=127.0.0.1}"
: "${RANGE_INSTALL_DIR:=/srv/seuxdr}"

pass=0; fail=0
ok()   { printf '  \033[32mok\033[0m    %s\n' "$*"; pass=$((pass+1)); }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; fail=$((fail+1)); }
note() { printf '        %s\n' "$*"; }

echo "== containers =="
for c in seuxdr-manager frontend seuxdr-ollama; do
  state="$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null)"
  [[ "$state" == "running" ]] && ok "$c running" || bad "$c not running (${state:-absent})"
done

echo
echo "== published ports on $RANGE_HOST_IP =="
probe() { curl -sk -o /dev/null -m 8 -w '%{http_code}' "$1" 2>/dev/null; }
code="$(probe "https://${RANGE_HOST_IP}:8080/")"
[[ "$code" =~ ^(200|301|302|404)$ ]] && ok "8080 front end (HTTP $code)" || bad "8080 front end (HTTP ${code:-none})"
code="$(probe "https://${RANGE_HOST_IP}:8443/api/certs/server-ca.crt")"
[[ "$code" =~ ^(200|404)$ ]] && ok "8443 manager API (HTTP $code)" || bad "8443 manager API (HTTP ${code:-none})"
nc -z -w 5 "$RANGE_HOST_IP" 8081 2>/dev/null && ok "8081 agent enrolment reachable" || bad "8081 agent enrolment"
code="$(curl -s -o /dev/null -m 8 -w '%{http_code}' "http://${RANGE_HOST_IP}:11434/api/tags" 2>/dev/null)"
[[ "$code" == "200" ]] && ok "11434 Ollama responding" || bad "11434 Ollama (HTTP ${code:-none})"

echo
echo "== model =="
if docker exec seuxdr-ollama ollama list 2>/dev/null | tail -n +2 | grep -q .; then
  ok "a model is present"
  docker exec seuxdr-ollama ollama list 2>/dev/null | sed -n '2,4p' | sed 's/^/        /'
else
  bad "no model pulled yet (first run can take 20 min)"
fi

echo
echo "== deployed mode =="
if [[ -d "$RANGE_INSTALL_DIR/.git" ]]; then
  note "ref $(git -C "$RANGE_INSTALL_DIR" rev-parse --short HEAD) on $(git -C "$RANGE_INSTALL_DIR" rev-parse --abbrev-ref HEAD)"
  [[ -f "$RANGE_INSTALL_DIR/SECURITY.md" ]] \
    && note "SECURITY.md present  -> looks like the remediated ref" \
    || note "no SECURITY.md       -> looks like the baseline ref"
fi
# The clearest behavioural difference: does the remediation endpoint need a credential?
code="$(curl -sk -o /dev/null -m 8 -w '%{http_code}' -X POST \
        -H 'Content-Type: application/json' -d '{}' \
        "https://${RANGE_HOST_IP}:8443/api/agent/1/execute-action" 2>/dev/null)"
case "$code" in
  401|403) note "execute-action returns $code -> authentication IS enforced (remediated)";;
  400|404|422|500) note "execute-action returns $code -> reached the handler with NO credential (baseline)";;
  *) note "execute-action returned ${code:-none} — inconclusive";;
esac

echo
echo "== $pass ok, $fail failed =="
[[ "$fail" -eq 0 ]] || exit 1
