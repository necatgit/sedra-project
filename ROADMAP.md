# Roadmap

Dates are targets, not promises. When one moves, the change and the reason go into [updates/](updates/).

Status: `[ ]` open · `[~]` in progress · `[x]` done · `[-]` dropped

## Phase 0: Research and planning (current)

- [x] Set up the project repository (2026-11-05)
- [ ] Review what the current mainnet release `2.0.0-relaunch` changed and how it was activated
- [ ] Study the ZKas AuxPoW design (`consensus/core/src/auxpow.rs`, `consensus/pow/src/auxpow.rs` in zkas-rusty)
- [ ] Find out whether one Kaspa block can carry commitments for both ZKas and Sedra
- [ ] Decide the implementation path: add AuxPoW to the Go node (`sedrad`) or move Sedra to the Rust codebase
- [ ] Rough effort and timeline estimate
- [ ] Publish the first full draft of SIP-0001

## Phase 1: Community and coordination

- [ ] Contact the Sedra owner: support, repository access, infrastructure
- [ ] Open SIP-0001 for public comment
- [ ] Reach out to pools, explorers and exchanges

## Phase 2: Implementation

- [ ] Fork `sedrad`, implement AuxPoW validation behind an activation point
- [ ] Unit tests and consensus tests
- [ ] Merged-mining support in a reference pool

## Phase 3: Public testnet

- [ ] Launch a public testnet with merged mining
- [ ] Publish instructions so anyone can run a node and test
- [ ] Fix issues, publish release candidates

## Phase 4: Mainnet activation

- [ ] Announce the activation point weeks in advance
- [ ] Release with checksums and build instructions
- [ ] Track upgrade status of pools, exchanges and explorers publicly
- [ ] Activation and follow-up
