# 2026-11-07: real Kaspa mainnet headers as M10 test data (Q19)

- 20 consecutive selected-chain Kaspa mainnet blocks (DAA 586,360,429 to 586,360,564, block version 2), read with
  `GetBlock` (without transactions) from a Kaspa mainnet node (kaspad 2.1.0), read-only. Stored in sedra-rusty branch
  `m10-auxpow` as `testing/integration/testdata/kaspa_mainnet_headers_v2.json.gz` (`60b942fc`).
- `kaspa_hash_check.py`: an independent Python implementation of the header hashing layout of rusty-kaspa
  (`consensus/core/src/hashing/header.rs`: blake2b-256 keyed "BlockHash"). **Verified: 20 of 20 hashes reproduce.**
- The public REST API `api.kaspa.org/blocks/{hash}` returns only the level-0 parents (1 level instead of 56 for the
  same blocks), so its headers cannot be re-hashed (0 of 20). **Verified** by comparing both sources.

**What this does NOT mean:** Q19 is not closed yet. The hashing layout is the one Sedra's Rust code uses, but the
proof is a test in sedra-rusty itself that hashes these headers; that is the first M10 step.
