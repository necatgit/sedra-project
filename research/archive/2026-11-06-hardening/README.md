# Hardening back-ports evidence (2026-11-06)

Issue #29, analysis in [research/0006](../../0006-security-backports.md). Code: `necatgit/sedra-rusty` branch
`hardening` (`f31e35b6`, `aa9ec0e0`, `e736445f`, `SEDRA.md` in `4d2f8b91`), to be merged after the M5 sync.

| Change | Upstream | Regression test and mutation check |
|---|---|---|
| Storage mass: `(sum_ins / ins_plurality).max(1)` | `778b21e2` (part) | `sedra_storage_mass_tiny_inputs_do_not_divide_by_zero_test`; original code: "attempt to divide by zero" |
| 2 MB cap on decoded P2P block messages (`ConversionError::Size`) | `2a47b249` (part) | 3 tests: oversized message rejected (fails with the check removed), normal block round-trip, ≥ 2x slack over the consensus limit (500,000 bytes) on all networks |
| Inbound handshakes: ≤ 32 pending, ≤ 2 per IP, each in its own task; the hub only registers finished peers | `2a47b249` (part) | `pending_inbound_handshake_limits_and_reuses_slots_test` (ported from upstream); limit check removed: "third handshake from one IP must be refused" |

**Why the storage-mass fix is not a consensus change:** in block validation, `check_mass_commitment` only runs when
`crescendo_activation` is active (`tx_validation_in_utxo_context.rs:46`), which is never on Sedra. Storage mass is
otherwise computed only for mempool transactions (`utxo_validation.rs:432`).

**Not taken:** upstream also lowers the overall P2P message limit from 1 GB to 256 MB. Protocol v5 sends the pruning
point proof as one message; for Sedra (75,884 headers in the proof seen during M4, up to 48 parent levels) it may be
close to or above 256 MB. To be measured first.

| File | What it is |
|---|---|
| `apply_h1.py`, `apply_h2.py`, `apply_h3.py` | The scripts that applied the changes and tests |
| `test-vm-hardening.log` | Full test run of the branch on the test VM: 112 suites, 517 passed, 0 failed, 25 ignored |
| `devnet-inbound-test.txt` | Real-world check of the rebuilt inbound path on an isolated devnet: the Go node (sedrad v2.0.0) connected **into** the Rust node (protocol v5, "P2P Connected to incoming peer"); 150 blocks mined through each node; both ended at DAA 300, the same tip and the same supply (149,000 SDR); 0 rejects, 0 errors |
