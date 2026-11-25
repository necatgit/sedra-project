# Roadmap

Dates are targets, not promises. When one moves, the change and the reason go into [updates/](updates/).

Each item links to its GitHub issue, which holds the details and discussion. Phases are tracked as
[milestones](../../milestones).

Status: `[ ]` open · `[~]` in progress · `[x]` done · `[-]` dropped

## Phase 0: Research and planning

- [x] Set up the project repository (2026-11-05)
- [x] Review what the current mainnet release `2.0.0-relaunch` changed and how it was activated (#1, [research/0001](research/0001-relaunch-review.md))
- [x] Study the ZKas AuxPoW design (#2, [research/0002](research/0002-zkas-auxpow.md))
- [x] Find out whether one Kaspa block can carry commitments for both ZKas and Sedra (#3): yes, but only just
- [x] Decide the implementation path (#4): **Rust node based on rusty-kaspa v1.0.1**, in two steps ([research/0004](research/0004-rust-path.md), decided 2026-11-05)
- [x] Rough effort and timeline estimate (#5): actuals and remaining steps posted 2026-11-10 (mainnet activation not before January 2027, after the testnet report)
- [x] Publish the first full draft of SIP-0001 (#6): draft published 2026-11-06, reviewed by Nec 2026-11-09 (Q20, Q22, Q25, Q33 decided)

## Phase 1: Community and coordination

- [x] Contact the Sedra owner: support, repository access, infrastructure (#7, closed 2026-11-25; open questions continue in #19): questions sent 2026-11-05; all open questions resent as one list on 2026-11-16; the Sedra team's reply of 2026-11-17 (a draft for team approval) proposes answers by 2026-11-30, 2026-12-07 and 2026-12-14 ([QUESTIONS](QUESTIONS.md))
- [~] Open SIP-0001 for public comment (#8): open since 2026-11-09 in the public repository [necatgit/sedra-sips](https://github.com/necatgit/sedra-sips) (comments: sedra-sips#1); this repository is public since 2026-11-21, together with the [operator security advisory](research/0007-sedrad-v2.0.0-advisory.md)
- [ ] Reach out to pools, explorers and exchanges (#9): **for the Sedra team** (owner of the network and its contacts); Nec is not the owner and provides the technical information (SIP, node, test results) on request. Sedra team reply 2026-11-17 (draft): the team will ask its own pool and jsmining about merged mining (Q21) and the operators about their node versions (Q57)

## Phase 2: Implementation (current)

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
- [x] Security back-ports from later rusty-kaspa releases (#29, [research/0006](research/0006-security-backports.md), closed 2026-11-16): must-fix and should items merged 2026-11-06 (`sedra-rusty@9cb74efc`, 518 tests pass; upstream `48b63582` deliberately not applied, it rejects real Sedra proofs); the optional fixes merged after M9 and shipped in v0.1.0 (2026-11-14, release branch = `dev` + `optional-backports`, 521 passed, 0 failed)
- [x] M9: Seven-day soak next to Go nodes (#28, closed 2026-11-14): **passed**, 2026-11-07 07:20 to 2026-11-14 07:20 UTC, 10,064 checks, 0 alerts, 0 differences in supply or treasury
- [~] After M9: a public Rust node of this project as the first independent public Sedra node, on a machine separate from any pool ([SIP-0002](proposals/SIP-0002-network-resilience.md), #30): **running since 2026-11-14** (see below); still open: a machine separate from the pool
  - [x] Release preparation (2026-11-09, `sedra-rusty@a87436d9`): Sedra version string (`0.1.0 (rusty-kaspa v1.0.1, commit …)`), reproducible build (`contrib/reproducible/`, pinned toolchain, image and Debian snapshot), `docs/RELEASE.md`, README for outsiders. Two clones built identical binaries on one host. *Update 2026-11-14:* the container route was then run on two machines from the release tag, with identical checksums (release checklist step 4)
  - [x] The Go wallet daemon `sedrawallet` (sedrad v2.0.0) against the Rust node on a local devnet (2026-11-10, `wallet_test.sh` of the end-to-end harness, now in sedra-rusty `contrib/e2e-merged-mining/` on `m10-auxpow`): addresses, balance, CLI send and the daemon's `Send` as Miningcore's payout calls it all work; amounts and fees add up exactly. Operators keep the Go wallet binary and point `--rpcserver` at the Rust node (started with `--utxoindex`)
  - [x] Release v0.1.0 on 2026-11-14 following [release/v0.1.0-checklist.md](release/v0.1.0-checklist.md): `sedra-rusty` public, signed tag `sedra-v0.1.0`, identical rebuilds on two machines, [GitHub release](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.1.0) with rebuild issue sedra-rusty#1
  - [x] Release v0.1.1: tagged 2026-11-14, release published 2026-11-15 ([notes](release/v0.1.1-notes.md)): docs and a build-script exit code only, the node behaves exactly as 0.1.0; signed tag `sedra-v0.1.1`, identical rebuilds on two machines, [GitHub release](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.1.1)
  - [x] Public node: the former test VM runs the release as a P2P-only node (RPC on localhost) since 2026-11-14, 0.1.1 since 2026-11-15 18:11 UTC; first three outside nodes connected inbound on 2026-11-15. 24 h comparison with the Go node (2026-11-14 15:13 to 11-15 15:14 UTC): 1,439 checks, no difference. It runs on the same physical host as PuddlePool, so it is an independent node, not independent hardware
  - [ ] The public node on a machine separate from any pool

Step 2: the merged-mining hard fork.

- [x] M10: Port the AuxPoW verifier into the Rust node behind an activation point (#10, closed 2026-11-10), branch `m10-auxpow` of `sedra-rusty`
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
    - [x] 5c (2026-11-10, sedra-rusty `9248ee20` devnet-only `--devnet-aux-pow-activation`; harness: sedra-rusty `contrib/e2e-merged-mining/` on `m10-auxpow`, here in `tools/` until 2026-11-15): two Sedra and two Kaspa devnet nodes, Miningcore, CPU stratum miner; 401 of 401 merged-mined SDR blocks accepted, relayed to the second node, credited to the miner's SDR address. Found and fixed: a blue-work sign bug in the shared aux serializer (also latent for ZKAS in production, fixed on Miningcore `dev` `18862898`), the aux wallet host defaulting to the production ZKAS wallet IP, unrecognized Sedra test-network addresses
  - [x] Pool side (Miningcore branch `sedra-merged-mining`, 2026-11-10): serializer checked against the node's interop vector, several aux chains per parent (KAS jobs carry ZKM1 and SDM1), per-chain miner addresses, aux pool `kaspa1-sedra` with its own wallet, display of every aux chain, one payout-limit field per aux chain. The separate wallet exists (2026-11-10, its own wallet daemon); the pool configuration carries it as a disabled entry until go-live
- [x] Unit tests and consensus tests (#11, closed 2026-11-10: covered in M10 steps 2-5)
- [~] Merged-mining support in a reference pool (#12): implemented and tested in PuddlePool's Miningcore (branch, see M10 pool side); publishing it as a reference is planned with the testnet (SIP-0003 §4.5)
- [ ] Network resilience in the node code: more seeders and fallback peers from independent operators; peer memory ("parents and children") and opt-in "I am alive" announcements, design ([SIP-0002](proposals/SIP-0002-network-resilience.md), #30)

## Phase 3: Public testnet

- [~] Launch a public testnet with merged mining, with instructions so anyone can run a node and test (#13): plan drafted as [SIP-0003](proposals/SIP-0003-public-testnet.md) (2026-11-10): Q46-Q50 decided by Nec 2026-11-10; Q51 (duration, pass criteria) and Q52 asked of the Sedra team on 2026-11-10; Sedra team reply 2026-11-17 (draft): the two-week minimum and the criteria accepted as a starting checklist, subject to agreement before launch (Q51 partial), Q52 promised by 2026-12-14; SIP-0003 open for public comment since 2026-11-17 in [necatgit/sedra-sips](https://github.com/necatgit/sedra-sips) without waiting longer for the reply (copies in both repositories kept in sync); **testnet kit ready 2026-11-20** ([testnet/](testnet/README.md): participant guide, operator runbook, pass-report template, design; code, configs and scripts in sedra-rusty branch `testnet-kit`; private dry run on sedra-dev passed what it covered, [evidence](research/archive/2026-11-20-0013-testnet-dryrun.md)). Launch waited on the Sedra team's agreement (Q51, Q52); *update 2026-11-25:* the team agreed in writing on 2026-11-24 (SIP-0003 as it stands, fresh chain); proposed start 2026-12-01, not announced yet; public status page <https://testnet.puddlepool.com>; Kaspa TN10 payouts checked with the wallet daemon Miningcore uses ([evidence](research/archive/2026-11-20-0013-kas-tn10-payout-check.md)); hosts decided 2026-11-24 (seed2 on a rented EU VPS, the rest at home, [testnet/HOSTING.md](testnet/HOSTING.md)); **testnet release candidate `0.2.0-testnet.1` ready 2026-11-24** (activation 345,600, ban start 172,800, refuses mainnet; 566 tests passed and identical rebuilds on two machines; rehearsed on the real hosts and **published as a pre-release 2026-11-25**: [release](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.2.0-testnet.1), [checklist](release/v0.2.0-testnet.1-checklist.md), [go runbook](release/v0.2.0-testnet.1-go.md), [rehearsal](testnet/REHEARSAL.md))
- [~] Fix issues, publish release candidates (#14): first candidate `0.2.0-testnet.1` published as a pre-release 2026-11-25; rehearsal findings in #14

## Phase 4: Mainnet activation

- [ ] Announce the activation point, agreed jointly with the Sedra team, with notice as short as the operators can safely upgrade (#15; decided 2026-11-09, Q33)
- [ ] Release with checksums and build instructions (#16)
- [ ] Track upgrade status of pools, exchanges and explorers publicly (#17)
- [ ] Activation and follow-up (#18)
