# 2026-11-10: Merged mining works in the Rust node and through a pool

## M10: the merged-mining rules are in the Rust node

Branch `m10-auxpow` of `sedra-rusty` now carries the complete merged-mining design of SIP-0001, switched off on every
network until an activation point is agreed with the Sedra team (#10):

- Kaspa parent blocks are hashed exactly as Kaspa does today, checked on 20 real Kaspa mainnet blocks.
- The proof is an optional field next to the Sedra header, outside the header hash, as ZKas does it. Peers and pools
  can send it (P2P and mining RPC); a bad proof from a peer is dropped, not trusted.
- A block counts if its own work is enough, or, only after activation, if the Kaspa parent's work is enough. Native
  mining keeps working unchanged.
- From two days before activation, a Sedra block may no longer carry a merged-mining commitment for Sedra itself
  (SIP §4.5, decided 2026-11-10).

Tests beyond unit level: deterministic fuzzing of every decoder and check (one free byte range found and closed), two
nodes syncing 240 blocks with a pruning proof full of merged-mined headers, and an older node correctly rejecting them.
Full suite: 557 passed.

## End-to-end through a pool

On a local, isolated test network (two Sedra and two Kaspa devnet nodes), the pool software Miningcore and a small CPU
miner produced **401 of 401** accepted merged-mined Sedra blocks, relayed to the second node and credited to the
miner's own Sedra address. The test found three bugs in the pool software, all fixed; one of them also affected the
pool's live ZKas merged mining (not yet triggered, fix deployed the same day).

The pool side (one Kaspa job carrying ZKas and Sedra commitments, a separate Sedra payout wallet, display and payout
settings per chain) is ready on its own branch and goes live together with the node.

## The existing wallet works with the Rust node

Pools, games and exchanges pay out through the Go wallet daemon `sedrawallet`. Tested the same day on a local test
network: the wallet from sedrad v2.0.0, connected to the Rust node, shows balances, sends, and pays out exactly as
the pool software calls it; amounts and fees add up to the last unit. Operators who switch to the Rust node keep
their wallet and only point it at the new node.

## Next

- 2026-11-14: the seven-day run (M9) ends; then the Rust node is published as `v0.1.0`.
- Activation needs a date agreed with the Sedra team (Phase 4).
