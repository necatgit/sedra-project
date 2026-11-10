# Roadmap

Dates are targets, not promises. When one moves, the change and the reason go into [updates/](updates/).

Each item links to its GitHub issue, which holds the details and discussion. Phases are tracked as
[milestones](../../milestones).

Status: `[ ]` open · `[~]` in progress · `[x]` done · `[-]` dropped

## Phase 0: Research and planning (current)

- [x] Set up the project repository (2026-11-05)
- [x] Review what the current mainnet release `2.0.0-relaunch` changed and how it was activated (#1, [research/0001](research/0001-relaunch-review.md))
- [x] Study the ZKas AuxPoW design (#2, [research/0002](research/0002-zkas-auxpow.md))
- [x] Find out whether one Kaspa block can carry commitments for both ZKas and Sedra (#3): yes, but only just
- [x] Decide the implementation path (#4): **Rust node based on rusty-kaspa v1.0.1**, in two steps ([research/0004](research/0004-rust-path.md), decided 2026-11-05)
- [ ] Rough effort and timeline estimate (#5)
- [x] Publish the first full draft of SIP-0001 (#6): draft published 2026-11-06, reviewed by Nec 2026-11-09 (Q20, Q22, Q25, Q33 decided)

## Phase 1: Community and coordination

- [~] Contact the Sedra owner: support, repository access, infrastructure (#7): questions sent 2026-11-05
- [~] Open SIP-0001 for public comment (#8): open since 2026-11-09 in the public repository [necatgit/sedra-sips](https://github.com/necatgit/sedra-sips) (comments: sedra-sips#1); this repository stays private until the security write-up (around 2026-11-23)
- [ ] Reach out to pools, explorers and exchanges (#9): **for the Sedra team** (owner of the network and its contacts); Nec is not the owner and provides the technical information (SIP, node, test results) on request

## Phase 2: Implementation

Step 1: a Rust node with exactly Sedra mainnet's current consensus, running next to the Go nodes (no fork).
Code: `necatgit/sedra-rusty`, branch `dev`.

- [x] M0: Sedra's genesis hash reproduced with rusty-kaspa's hashing rules ([research/0004](research/0004-rust-path.md))
- [x] M1: Sedra network on rusty-kaspa v1.0.1 (#20, `sedra-rusty@7fa343ab`)
- [x] M2: Subsidy parity with sedrad (#21, `sedra-rusty@8aa3d981`, 813 vectors from sedrad)
- [x] M3: Real Sedra headers decode and validate offline (#22, `sedra-rusty@b9b51075`, 2001 real blocks; GHOSTDAG/DAA in M5)
- [x] M4: P2P v5 handshake with a local Go node (#23, 2026-11-06)
- [x] M5: Full sync from a local Go node (#24, 2026-11-06: synced in 7.5 min, followed the tip for 1 h with 0 difference)
- [x] M6: v2.0.0 rules behave exactly like Go (#25, `sedra-rusty@4873e9af`)
- [x] M7: UTXO commitment and supply parity (#26, 2026-11-06: identical supply, commitment, balances and UTXOs)
- [x] M8: Mining parity on an isolated test setup (#27, private devnet, 1400 blocks)
- [~] Security back-ports from later rusty-kaspa releases (#29, [research/0006](research/0006-security-backports.md)): must-fix and should items done and merged (`sedra-rusty@9cb74efc`, 518 tests pass; upstream `48b63582` deliberately not applied, it rejects real Sedra proofs); optional fixes ready on branch `optional-backports` (tested), to be merged after M9
- [~] M9: Seven-day soak next to Go nodes (#28) (running 2026-11-07 07:20 to 2026-11-14 07:20 UTC)
- [ ] After M9: a public Rust node of this project as the first independent public Sedra node, on a machine separate from any pool ([SIP-0002](proposals/SIP-0002-network-resilience.md), #30)
  - [x] Release preparation (2026-11-09, `sedra-rusty@a87436d9`): Sedra version string (`0.1.0 (rusty-kaspa v1.0.1, commit …)`), reproducible build (`contrib/reproducible/`, pinned toolchain, image and Debian snapshot), `docs/RELEASE.md`, README for outsiders. Two clones built identical binaries on one host; the container route across two machines is still to be run
  - [x] The Go wallet daemon `sedrawallet` (sedrad v2.0.0) against the Rust node on a local devnet (2026-11-10, `tools/e2e-merged-mining/wallet_test.sh`): addresses, balance, CLI send and the daemon's `Send` as Miningcore's payout calls it all work; amounts and fees add up exactly. Operators keep the Go wallet binary and point `--rpcserver` at the Rust node (started with `--utxoindex`)
  - [ ] On 2026-11-14: make `sedra-rusty` public, test the container build on the test VM, tag `v0.1.0`, turn the test VM into the public node (decided 2026-11-09: same host as the pool, so not fully independent; a separate machine later)

Step 2: the merged-mining hard fork.

- [~] M10: Port the AuxPoW verifier into the Rust node behind an activation point (#10), branch `m10-auxpow` of `sedra-rusty`
  - [x] Step 1 (2026-11-10, `4638efe2`): Kaspa parents hashed as Kaspa does today; checked on 20 real Kaspa mainnet blocks (headers, kHeavyHash, coinbase hashes, Merkle branches). Finding: Kaspa coinbases are transaction version 1 since Toccata, so they need their own type (Q19 answered)
  - [x] Step 2 (2026-11-10, `f3f589c3`): the proof format and its structural rules (SDM1 base64url commitment, exactly once, nonce binding, limits), tested on a real Kaspa block with every rule broken once
  - [x] Step 3 (2026-11-10, `7f9a37b5`): the parent's work against the Sedra target, dual acceptance (native first, proof only after activation), block level from the parent's work; six rules mutation-checked
  - [x] Step 4 (2026-11-10, in three commits; full suite 548 passed):
    - 4a `42ca58c8`: the proof as an optional header field outside the header hash, as ZKas does (decided 2026-11-10), nesting rejected, DB version 5 (existing Rust nodes resync once)
    - 4b `45e74643`: P2P field 15 (a bad proof from a peer is dropped, the header kept) and the mining RPC (`RpcRawHeader.auxPow`, gRPC field 16, wRPC format 2; a bad proof is an error the pool sees)
    - 4c `12630118`: `aux_pow_activation` (never on every network), the gate in header validation and pruning proof, self-parent ban from 2 × finality depth (~2 days) before activation (decided 2026-11-10, as in ZKas; SIP §4.5/§5 updated); tested through the real consensus pipeline on simnet
  - [x] Step 5: tests beyond unit level
    - [x] 5a `f21ba68f` (2026-11-10): deterministic fuzzing of decoder, checks, PoW gate, P2P and RPC conversion; finding: the parent's cached hash field was the only free byte range, now normalized at both decode edges
    - [x] 5b `abffef04` (2026-11-10): two nodes, 240 blocks (half merged-mined) relayed through the P2P conversion, pruning proof with 319 merged-mined headers validated; a node without merged mining rejects block and proof; full suite 556 passed
    - [x] 5c (2026-11-10, sedra-rusty `9248ee20` devnet-only `--devnet-aux-pow-activation`; harness `tools/e2e-merged-mining/`): two Sedra and two Kaspa devnet nodes, Miningcore, CPU stratum miner; 401 of 401 merged-mined SDR blocks accepted, relayed to the second node, credited to the miner's SDR address. Found and fixed: a blue-work sign bug in the shared aux serializer (also latent for ZKAS in production, fixed on Miningcore `dev` `18862898`), the aux wallet host defaulting to the production ZKAS wallet IP, unrecognized Sedra test-network addresses
  - [x] Pool side (Miningcore branch `sedra-merged-mining`, 2026-11-10): serializer checked against the node's interop vector, several aux chains per parent (KAS jobs carry ZKM1 and SDM1), per-chain miner addresses, aux pool `kaspa1-sedra` with its own wallet, display of every aux chain, one payout-limit field per aux chain. The separate wallet exists (2026-11-10, its own wallet daemon); the pool configuration carries it as a disabled entry until go-live
- [ ] Unit tests and consensus tests (#11)
- [ ] Merged-mining support in a reference pool (#12)
- [ ] Network resilience in the node code: more seeders and fallback peers from independent operators; peer memory ("parents") design ([SIP-0002](proposals/SIP-0002-network-resilience.md), #30)

## Phase 3: Public testnet

- [ ] Launch a public testnet with merged mining, with instructions so anyone can run a node and test (#13)
- [ ] Fix issues, publish release candidates (#14)

## Phase 4: Mainnet activation

- [ ] Announce the activation point, agreed jointly with the Sedra team, with notice as short as the operators can safely upgrade (#15; decided 2026-11-09, Q33)
- [ ] Release with checksums and build instructions (#16)
- [ ] Track upgrade status of pools, exchanges and explorers publicly (#17)
- [ ] Activation and follow-up (#18)
