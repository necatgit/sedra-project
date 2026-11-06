# cargo audit and dependency updates (2026-11-06)

Issue #29, analysis in [research/0006](../../0006-security-backports.md).

| File | What it is |
|---|---|
| `cargo-audit-before.json` | `cargo audit` (cargo-audit 0.22.2, RustSec database of 2026-11-06) on sedra-rusty `c0b14cc`: 28 vulnerabilities, 26 warnings, 604 packages |
| `cargo-audit-after.json` | The same after the dependency update on branch `deps-security` (`49e314f6`): 10 vulnerabilities |
| `summary.txt` | Both reports as readable lists |
| `test-vm-blockcount-backport.log` | Full test run with the block-count back-port (`b8182ca8`): 112 suites, 512 passed, 0 failed |
| `test-vm-deps-security.log` | Full test run with the dependency update (`49e314f6`): 112 suites, 512 passed, 0 failed |

**Which findings reach the node (`kaspad`)**, checked with `cargo tree -p kaspad -i <crate>`: the gRPC/P2P stack
(h2 0.4, bytes), consensus (crossbeam-channel), rayon (crossbeam-epoch), TLS (ring, rustls, rustls-webpki,
webpki-roots), and through UPnP h2 0.3 and idna. quinn-proto and time are not in the node at all.

**Updated** (lockfile only, each within its compatible version range, minimum Rust version unchanged at 1.82): h2
0.4.6 → 0.4.20, bytes 1.7.2 → 1.12.1, crossbeam-channel 0.5.13 → 0.5.17, crossbeam-epoch 0.9.18 → 0.9.21, ring 0.17.8 →
0.17.14, rustls 0.23.14 → 0.23.46 (with rustls-webpki 0.102.8 → 0.103.16), hashbrown 0.15.0 → 0.15.5, libz-sys 1.1.20 →
1.1.31, webpki-roots 0.26.6 → 0.26.11 / 1.0.11.

**Remaining 10, with reasons:** h2 0.3.26 (no patched 0.3 release; only on the UPnP path, which the test node disables);
idna 0.5.0 (UPnP path; the fix needs url 2.5.4, which raises the minimum Rust version to 1.83); quinn-proto (6
advisories) and time (not in the node); zstd-sys (the advisory only concerns the WebAssembly build).

**Not taken:** a first, broader update attempt also moved serde, syn, thiserror and others; it was rolled back to keep
the change small.

**Timing:** the dependency update is merged into `dev` only after the M5 sync, so that sync runs on the network stack
that was already tested with the Go node (M4, M8).
