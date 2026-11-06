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
- [ ] Publish the first full draft of SIP-0001 (#6)

## Phase 1: Community and coordination

- [~] Contact the Sedra owner: support, repository access, infrastructure (#7): questions sent 2026-11-05
- [ ] Open SIP-0001 for public comment (#8)
- [ ] Reach out to pools, explorers and exchanges (#9)

## Phase 2: Implementation

Step 1: a Rust node with exactly Sedra mainnet's current consensus, running next to the Go nodes (no fork).
Code: `necatgit/sedra-rusty`, branch `dev`.

- [x] M0: Sedra's genesis hash reproduced with rusty-kaspa's hashing rules ([research/0004](research/0004-rust-path.md))
- [x] M1: Sedra network on rusty-kaspa v1.0.1 (#20, `sedra-rusty@7fa343ab`)
- [x] M2: Subsidy parity with sedrad (#21, `sedra-rusty@8aa3d981`, 813 vectors from sedrad)
- [ ] M3: Real Sedra headers decode and validate offline (#22)
- [ ] M4: P2P v5 handshake with a local Go node (#23)
- [ ] M5: Full sync from a local Go node (#24)
- [ ] M6: v2.0.0 rules behave exactly like Go (#25)
- [ ] M7: UTXO commitment and supply parity (#26)
- [ ] M8: Mining parity on an isolated test setup (#27)
- [ ] M9: Seven-day soak next to Go nodes (#28)

Step 2: the merged-mining hard fork.

- [ ] M10: Port the AuxPoW verifier into the Rust node behind an activation point (#10)
- [ ] Unit tests and consensus tests (#11)
- [ ] Merged-mining support in a reference pool (#12)

## Phase 3: Public testnet

- [ ] Launch a public testnet with merged mining, with instructions so anyone can run a node and test (#13)
- [ ] Fix issues, publish release candidates (#14)

## Phase 4: Mainnet activation

- [ ] Announce the activation point weeks in advance (#15)
- [ ] Release with checksums and build instructions (#16)
- [ ] Track upgrade status of pools, exchanges and explorers publicly (#17)
- [ ] Activation and follow-up (#18)
