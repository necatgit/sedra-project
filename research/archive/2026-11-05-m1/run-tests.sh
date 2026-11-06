#!/usr/bin/env bash
# Full build + test run for sedra-rusty on sedra-dev. Usage: run-tests.sh <git ref> <label>
set -u
. ~/.cargo/env
REF=${1:-dev}; LABEL=${2:-run}; LOG=/data/logs/sedra-rusty-$LABEL-$(date -u +%Y%m%dT%H%M%SZ).log
cd /data/repos/sedra-rusty && git fetch -q origin && git checkout -q "$REF" && git reset -q --hard "origin/$REF" 2>/dev/null || git checkout -q "$REF"
{
  echo "== $LABEL $(date -u +%FT%TZ) $(git rev-parse --short HEAD) | $(. /etc/os-release; echo $PRETTY_NAME) | $(rustc --version) | $(nproc) cpus | CXXFLAGS(env)=${CXXFLAGS:-unset}"
  S=$(date +%s); cargo build --release --bin kaspad 2>&1 | grep -E "^error|Finished"; echo "build exit: ${PIPESTATUS[0]} ($(( $(date +%s)-S ))s)"
  S=$(date +%s); timeout 3600 cargo test --release --no-fail-fast --workspace --exclude kaspa-wasm --exclude kaspa-wallet-pskt 2>&1 | grep -E "^error|^test |^test result|panicked at|^     Running"; echo "test exit: ${PIPESTATUS[0]} ($(( $(date +%s)-S ))s)"
  echo "== end $(date -u +%FT%TZ)"
} > "$LOG" 2>&1
echo "$LOG: $(grep -c "^test result" "$LOG") suites, $(grep "^test result" "$LOG" | awk "{p+=\$4;x+=\$6;i+=\$8} END{print p\" passed, \"x\" failed, \"i\" ignored\"}")"
grep -E "^test .* FAILED" "$LOG"; grep -E "exit:" "$LOG"
