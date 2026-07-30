#!/usr/bin/env bash
# Produce the source archive a trainee needs, without giving them repo access
# or asking them to deploy the stack.
#
# Most of scenario 04 is source-side: CyberFort's SBOM Generator, Dependency
# Check and Code Analysis all take an archive. Only Step 5 of the trainee
# handbook needs the product running.
#
#   ./fetch-source.sh                              # uses RANGE_PRODUCT_REF from .env
#   ./fetch-source.sh cra/remediation-sprint-1     # or name a ref explicitly
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$here/.env" ]] && { set -a; source "$here/.env"; set +a; }
: "${RANGE_PRODUCT_REPO:=git@github.com:CyberGuardEU/t4.4_siem_ai_remediation.git}"
: "${RANGE_PRODUCT_REF:=cra/remediation-sprint-1}"
ref="${1:-$RANGE_PRODUCT_REF}"
outdir="${2:-$here/dist}"

command -v git >/dev/null || { echo "!! git not found"; exit 1; }
mkdir -p "$outdir"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

echo "[fetch] cloning $RANGE_PRODUCT_REPO at $ref"
git clone --quiet "$RANGE_PRODUCT_REPO" "$work/src"
git -C "$work/src" checkout --quiet --force "$ref"
sha="$(git -C "$work/src" rev-parse --short HEAD)"
version="$(cat "$work/src/VERSION" 2>/dev/null || echo unversioned)"

# Exclude git history, node_modules and any committed build artefact. The
# scanners want source, and a 22MB history makes the upload needlessly slow.
name="seuxdr-${version}-${sha}-src.zip"
echo "[fetch] packaging $name"
( cd "$work/src" && zip -qr "$outdir/$name" . \
    -x '*.git/*' -x '*/node_modules/*' -x 'manager/manager' -x 'assets/*' )

echo
echo "  ref      $ref ($sha)"
echo "  version  $version"
echo "  archive  $outdir/$name  ($(du -h "$outdir/$name" | cut -f1))"
echo
echo "Hand this to the trainee. Upload it to CyberFort under:"
echo "  Security Tools -> SBOM Generator     (accept the authorisation disclaimer)"
echo "  Security Tools -> Dependency Check"
echo "  Security Tools -> Code Analysis"
