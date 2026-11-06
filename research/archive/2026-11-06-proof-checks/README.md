# 2026-11-06: pruning-proof checks tested against a real Sedra proof (#29)

Two upstream pruning-proof checks had been held back until they could be tested against a real proof from a Sedra Go
node. Both tests were fresh syncs of a separate test node (`/data/sedra-proof-test`) from the **local** Go node on
the test machine only (`--connect=127.0.0.1:22111`), never from a production node.

## 1. Empty proof level (found while adapting the back-port)

**Verified:** in rusty-kaspa v1.0.1 a pruning point proof with an empty level reaches `selected_tip.unwrap()` on
`None` and panics; the node's panic hook then exits the process. Upstream rejects such a proof with an error since a
later refactor. Fix and regression test in sedra-rusty `7863751e`. `mut-proof.log`: the test passes with the fix and
fails with a panic at `validate.rs:337` when the check is removed.

## 2. Upstream `48b63582` (full levels need a selected tip with blue score >= 2M): rejected, not applied

`proof-sync-48b63582-rejected.log`: the real mainnet proof from sedrad was rejected:

> the pruning proof selected tip a990faed… at level 13 blue score 1998 < 2M and root is not genesis

Level 13 holds 2037 headers, but its selected tip has blue score 1998 inside the proof, below 2M = 2000.
**Consequence (Verified):** with this check the Rust node cannot sync from any Sedra Go node, so it was removed again
(`210a9065`) and is listed in SEDRA.md as deliberately not applied.

## 3. Final version: sync works, `11ffbcc6` passes

`proof-sync-20261106T211910Z.log` (`210a906`): proof received (75,884 headers, 24,479 unique), validated and applied,
2647 trusted blocks processed with the `11ffbcc6` check (trusted blocks must not be in the pruning point's future),
synced in 420 s, then new blocks accepted via relay. 0 errors.

Full test suite on the same commit (`sedra-rusty-proof-checks-20261106T210758Z.log`): 112 suites, 518 passed,
0 failed, 25 ignored. Merged into `dev` as `9cb74efc` (with the SEDRA.md note).

## Related: Q35

The same log again shows the Rust node's own rebuild of the proof differing from the Go node's on levels 0-13
(77,382 against 75,884 headers); the Rust-built proof validates. Together with the 1998 < 2000 result above this
**suggests (Inferred)** that sedrad's proof builder selects slightly fewer blocks on the lower levels than the Rust
builder expects. Not yet checked in the Go code.

## What this does NOT mean

- Not every possible malformed proof is now rejected cleanly; only the cases above were tested.
- The size of the proof message in bytes was not measured; the header counts above are the input for that.
