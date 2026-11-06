# Security back-ports evidence (2026-11-06)

Issue #29, analysis in [research/0006](../../0006-security-backports.md). Code: `necatgit/sedra-rusty` `dev`, commit
`c0b14ccd` (fixes and tests).

| File | What it is |
|---|---|
| `apply_sec.py` | The script that applied the four fixes and their regression tests |
| `test-vm-security-backports.log` | Full test run on the test VM: 112 suites, 511 passed, 0 failed, 25 ignored |

**Regression tests, each shown to fail with the original rusty-kaspa v1.0.1 code** (the fix reverted one at a time):

| Test | Result with the original code |
|---|---|
| `flow_context::sedra_backport_tests::handshake_time_offset_does_not_overflow_test` | panics: "attempt to subtract with overflow" |
| `manager_tests::tests::sedra_reject_impossible_outpoint_test` | panics: "index out of bounds: the len is 1 but the index is 5" |
| `manager_tests::tests::sedra_reject_coinbase_transaction_test` | the coinbase transaction is accepted into the mempool (`Ok(())`), with non-standard transactions allowed as in upstream's own test |
| `tests::sedra_wrong_payload_length_is_an_error_test` | panics on the length assertion in `Address::new` |

In the release build (`overflow-checks = true`, panic hook ends the process) each of these panics would stop the node.
