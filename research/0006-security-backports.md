# 0006: Security fixes to carry over from later rusty-kaspa releases (Q31)

| | |
|---|---|
| Question | Q31 in [QUESTIONS.md](../QUESTIONS.md) |
| Date | 2026-11-06 |
| Compared | rusty-kaspa `v1.0.1` (`fcd9c28f`) with `origin/master` (`4863866f`): 252 commits |
| Applies to | sedra-rusty, which is based on v1.0.1 (checked at `42ea0c23`) |
| Full report | [archive/2026-11-06-q31-backports-raw.md](archive/2026-11-06-q31-backports-raw.md) |
| Tracked in | Issue for the back-ports (see ROADMAP.md, Phase 2) |

Labels: **Verified** (checked in the code), **Inferred** (reasoned), **Unknown**.

## Summary

- The Sedra Rust node is built on a rusty-kaspa version (v1.0.1) that is no longer maintained upstream. Kaspa fixed
  several crash bugs after that version. The project has to carry these fixes over by hand.
- **Why crashes matter here (Verified):** the release build stops on any arithmetic overflow (`Cargo.toml:332`,
  `overflow-checks = true`), and the node's panic handler ends the whole process on any panic
  (`core/src/panic.rs`). A single reachable overflow or out-of-range access therefore takes the node down.
- **Four fixes are required** before the Rust node is exposed to anything other than a trusted local node: two crash
  paths reachable from network peers (Verified: the code is present unchanged in sedra-rusty), one reachable through the
  RPC interface, and one mempool rule that lets an invalid kind of transaction in (Inferred).
- Several further hardening fixes are recommended, and a few are optional clean cherry-picks.
- Most of the important fixes are hidden inside large upstream commits whose titles do not say "fix". Upstream also
  deleted the P2P protocol v5 code and the pre-Crescendo paths, so most fixes have to be re-applied by hand as small
  changes rather than cherry-picked.

## The back-port list

| Priority | Upstream source | Area | Status in sedra-rusty |
|---|---|---|---|
| Must | `2a47b249` (part of "Arithmetic safety and more", v2.1.0) | P2P handshake: unchecked arithmetic on a value chosen by the peer | Present (Verified) |
| Must | `778b21e2` (part) | Mempool: unchecked index when a transaction refers to another mempool transaction | Present (Verified) |
| Must | `eb0a856d` | Mempool: missing check that rejects coinbase transactions | Present (Inferred) |
| Must | `2a47b249` (part) | RPC: address with valid checksum but wrong length triggers an assertion | Present (Inferred; exposure depends on who can reach RPC) |
| Should | `778b21e2` (part) | Storage-mass calculation: possible division by zero | Inferred, depends on a crafted block |
| Should | `2a47b249` (part) | Unbounded pending inbound handshakes | Inferred |
| Should | `2a47b249` (part) | Size caps on decoded blocks and transactions; the upstream message-size cap must not be copied blindly, because protocol v5 sends the pruning proof as one message | Inferred |
| Should | `cea06453` | Crash on a block-count RPC during sync | Clean cherry-pick (Inferred) |
| Should | `11ffbcc6`, `48b63582` | Pruning-proof validation hardening | Inferred |
| Should | — | Run `cargo audit` on the dependency lockfile | Not done yet |
| Optional | `1fe3697b`, `8ae55970`, `d2901794`, `07941fa1`, `6a94fac3` | Shutdown panic, file-descriptor overflow and smaller fixes; `6a94fac3` removes duplicate hashes from `GetBlocks`, which PuddlePool's payout handler calls | Clean cherry-picks (Inferred) |
| Not applicable | `4e8f3135` and bridge, wallet, Toccata/covenant fixes | Fix regressions or code added after v1.0.1 | — |

## Status

*Update 2026-11-06:* the four must-fix items are done in sedra-rusty `c0b14ccd`. Each has a regression test that
fails with the original code (two overflow/out-of-bounds panics, the coinbase transaction accepted, the address
assertion), and the full test suite passes on the test VM (511 passed, 0 failed). Evidence:
[archive/2026-11-06-security-backports/](archive/2026-11-06-security-backports/README.md). The "should" and
"optional" items are still open (#29).

*Update 2026-11-06, afternoon:* also done: the block-count underflow during sync (upstream `cea06453`, sedra-rusty
`b8182ca8`, regression test fails with the original code), which the project's own sync monitoring would otherwise
trigger. `cargo audit` was run for the first time: 28 vulnerabilities before, 10 after a small lockfile update on
branch `deps-security` (`49e314f6`), none of the remaining 10 reachable from the network in the node as run here.
Both changes pass the full test suite (512 passed, 0 failed). The two pruning-proof checks (`11ffbcc6`, `48b63582`)
are held back until after the M5 sync, so they can be tested against a real Sedra proof first. Evidence:
[archive/2026-11-06-cargo-audit/](archive/2026-11-06-cargo-audit/README.md).

*Update 2026-11-06, evening:* the remaining "should" items are done on branch `hardening`: storage mass without
division by zero (checked: not a consensus change on Sedra), a 2 MB cap on decoded P2P block messages, and bounded,
concurrent inbound handshakes. 517 tests pass, each new test fails with the original code, and a devnet test with the
Go node connecting into the Rust node confirmed the rebuilt inbound path. Upstream's lower overall message limit
(256 MB) was not taken, because Sedra's pruning proof travels as one message of possibly that size. Evidence:
[archive/2026-11-06-hardening/](archive/2026-11-06-hardening/README.md). Open: the optional cherry-picks.

## Every fix is done the same way as the milestones

A regression test that crashes or fails **before** the fix and passes after it, the full test suite on the test VM,
an entry in `SEDRA.md` with the upstream commit it comes from, and the evidence in `research/archive/`.

## What this does NOT mean

- It does not affect Sedra mainnet today: mainnet runs the Go node, which these findings are not about.
- It does not mean the Rust node is in use anywhere: the project's test node talks only to a local Go node on a
  separate machine, and its RPC is reachable only on that machine.
- It is not a complete security audit. It covers fixes Kaspa made upstream after v1.0.1. Problems that Kaspa has not
  found, and Sedra-specific code, are not covered.
- The dependency advisories mentioned in the full report come from memory, not from `cargo audit`; they are unverified
  until that tool has been run.

## Review notes

Re-checked independently on 2026-11-06 at rusty-kaspa `v1.0.1` and sedra-rusty `42ea0c23`: `overflow-checks = true`
(`Cargo.toml:332`); panic hook calls `process::exit(1)` (`core/src/panic.rs:7,29`); the handshake time-offset
subtraction (`protocol/flows/src/flow_context.rs`, line 765 at v1.0.1, 762 in sedra-rusty); the unchecked
`outputs[index]` in `mining/src/mempool/populate_entries_and_try_validate.rs:16`.

*Public wording:* this document names the areas and the upstream commits, not how to trigger the problems. Kaspa fixed
them publicly, but other networks may still run v1.0.1.
