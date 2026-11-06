# 2026-11-06: The Rust node runs Sedra's rules, and a first SIP draft

Since the first research results yesterday, the project decided how to build the merged-mining fork and has made the
first part work. Everything below links to its evidence.

## The decision: a Rust node (#4)

Sedra's node is a copy of Kaspa's old Go node, which Kaspa no longer maintains. The merged-mining code that already
exists (in ZKas) is written in Rust. So the project builds Sedra on Kaspa's Rust node (rusty-kaspa v1.0.1) in two steps:
first a Rust node with exactly the same rules as Sedra today, running next to the Go nodes without any fork; then the
merged-mining fork on top. The cost, stated in [research/0004](../research/0004-rust-path.md): that Rust version is no
longer maintained upstream, so this project carries over security fixes itself.

## Step 1 so far

| Milestone | Result |
|---|---|
| M1 Sedra network in the Rust node | Genesis, names, addresses, ports, rewards; full test suite as green as upstream, on two systems |
| M2 Block rewards | 813 reward values computed by Sedra's own Go code, all equal |
| M3 Real blocks | 2001 real Sedra blocks: same hash, valid proof of work, consistent structure |
| M4 Connection to the Go node | Both sides talk protocol version 5; the Rust node accepts the Go node's pruning point proof |
| M6 The v2.0.0 relaunch rules | Difficulty reset and treasury outputs ported exactly; 25 boundary values from Go, all equal |
| M8 Mining together | On a private test network, each node accepts the other's blocks; same balances and supply after 1400 blocks |

Every test's expected values come from Sedra's Go code or from real chain data, and every new test was shown to fail
when its rule is deliberately broken. Details and logs: [research/archive/](../research/archive/), issues #20-#27.

## What did not work yet, and why

**M5, full sync of the Rust node:** blocked. Our freshly synced Go node received an incomplete set of the 2,641 blocks
needed around the current pruning point (2,039) from one of the public fallback peers, and passes on what it has. Go
nodes tolerate that; the Rust node correctly refuses. A long-running node has the complete set, so the chain itself is
fine. When the pruning point moves forward (expected around 2026-11-07 03:00 UTC), our Go node will have complete data
and the sync can be retried. Details: issue #24; the question to the Sedra team: [QUESTIONS.md](../QUESTIONS.md) Q5.

## Other findings

- Building this Rust node version on current Linux systems (GCC 15) failed in its database library; fixed with a build
  setting, without changing any source code.
- Sedra's Go node has an inherited bug from Kaspa's Go node (a condition checked twice), found by Go 1.26's code
  checker. Probably minor; documented in [research/0005](../research/0005-test-coverage.md).
- Test coverage: 51 % (Go node) and 58 % (Rust node) overall, 78-96 % in the consensus core.

## First draft of the proposal

[SIP-0001](../proposals/SIP-0001-merged-mining.md) now has a full first draft: how a Sedra block can be proven by
Kaspa mining work, how it coexists with ZKas in the same Kaspa block, activation, effects on pools, and the security
trade-offs, including that merged mining does not make Sedra "secured by Kaspa". It is a draft for review, not a
decision, and it cannot activate before the Rust node is complete and in use.

## Next

Retry the full sync after the pruning point moves (M5), then compare balances and supply with the Go node on the live
chain (M7), then a seven-day run next to the Go nodes (M9).

Time and AI effort per milestone: [TIMELINE.md](../TIMELINE.md).
