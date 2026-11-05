# Roadmap

Dates are targets, not promises. When one moves, the change and the reason go into [updates/](updates/).

Each item links to its GitHub issue, which holds the details and discussion. Phases are tracked as
[milestones](../../milestones).

Status: `[ ]` open · `[~]` in progress · `[x]` done · `[-]` dropped

## Phase 0: Research and planning (current)

- [x] Set up the project repository (2026-11-05)
- [ ] Review what the current mainnet release `2.0.0-relaunch` changed and how it was activated (#1)
- [ ] Study the ZKas AuxPoW design (#2)
- [ ] Find out whether one Kaspa block can carry commitments for both ZKas and Sedra (#3)
- [ ] Decide the implementation path: add AuxPoW to the Go node (`sedrad`) or move Sedra to the Rust codebase (#4)
- [ ] Rough effort and timeline estimate (#5)
- [ ] Publish the first full draft of SIP-0001 (#6)

## Phase 1: Community and coordination

- [ ] Contact the Sedra owner: support, repository access, infrastructure (#7)
- [ ] Open SIP-0001 for public comment (#8)
- [ ] Reach out to pools, explorers and exchanges (#9)

## Phase 2: Implementation

- [ ] Fork `sedrad`, implement AuxPoW validation behind an activation point (#10)
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
