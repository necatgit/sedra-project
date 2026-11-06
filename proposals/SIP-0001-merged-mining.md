# SIP-0001: Merged mining of Sedra with Kaspa

| | |
|---|---|
| Status | **Draft for review** (first full draft, 2026-11-06). Not final, not scheduled, not agreed with the Sedra team |
| Author | Nec |
| Created | 2026-11-05 |
| Type | Consensus (hard fork) |
| Discussion | Issue #6 (draft), #8 (public comment, later) |
| Based on | [research/0001](../research/0001-relaunch-review.md), [0002](../research/0002-zkas-auxpow.md), [0004](../research/0004-rust-path.md), [0005](../research/0005-test-coverage.md) |

Labels used for claims: **Verified** (checked in code or data, see the referenced research), **Inferred** (reasoned,
could be wrong), **Unknown**. Design choices are marked **Proposed**: they are what this draft suggests and are open for
discussion.

## 1. Summary

Allow a Sedra block to be valid either through its own proof of work, as today, **or** through an *auxiliary proof of
work* (AuxPoW): a Kaspa block header whose coinbase commits to the Sedra block and whose kHeavyHash meets Sedra's
difficulty target. Kaspa miners can then mine Sedra at no extra cost. Emission, supply, block rate, addresses and
transactions do not change.

## 2. Motivation

- Sedra and Kaspa use the same proof of work (kHeavyHash, **Verified** in research 0004), so they compete for the same
  machines. Almost all of that hashrate goes to Kaspa, which leaves Sedra with a small share.
- A small hashrate makes a chain cheaper to attack and less attractive to miners, pools and exchanges.
- Merged mining lets a Kaspa miner earn SDR as well, without giving up any KAS. ZKas already does this with Kaspa
  (**Verified**, research 0002).

### What merged mining does and does not give (read this first)

- It **does not** make Sedra "secured by Kaspa". The design below checks that enough kHeavyHash work was done and bound
  to the Sedra block; it does not check that the parent is a real, accepted Kaspa block (**Verified** for the ZKas
  design this follows, research 0002). Sedra is as secure as the hashrate that chooses to mine it.
- Because merged mining costs Kaspa miners nothing extra, a large Kaspa pool could also dominate Sedra at no cost
  (**Inferred**). This is the known trade-off of merged mining; section 8 discusses it.
- It only helps if Kaspa pools add Sedra support. At first that is one pool (PuddlePool, run by the author). Whether
  others follow is **Unknown**.

## 3. Prerequisite: the Rust node

The rule change needs a node that can carry and check AuxPoW proofs. Sedra's current node (sedrad, Go) is a copy of
Kaspa's Go node v0.12.15, which Kaspa no longer maintains (**Verified**, research 0004). This proposal therefore builds
on the Sedra Rust node based on rusty-kaspa v1.0.1 that this project develops in step 1 (milestones M1-M9).

Status on 2026-11-06 (**Verified**, evidence in `research/archive/`): the Rust node carries Sedra's network, block
rewards and both v2.0.0 relaunch rules, validates 2001 real Sedra blocks, connects to Sedra's Go node over protocol
version 5, and mines blocks that the Go node accepts and vice versa. Full sync against the live network (M5),
UTXO/supply parity (M7) and a seven-day run next to Go nodes (M9) are still open. **This SIP cannot activate before
step 1 is complete and the Rust node is in use by the network.**

## 4. Specification (Proposed)

The mechanism follows ZKas's current ("bound", post security fork) AuxPoW design (research 0002), with Sedra's own tag
and domain strings so the two chains cannot be confused.

### 4.1 The proof

An `AuxPow` witness travels with a Sedra block header, **outside the header hash** (so it does not change the block
hash and can be stripped by a relaying peer without changing the block's identity):

| Field | Content |
|---|---|
| `parent_header` | A Kaspa block header (current Kaspa header format, see 4.6) |
| `parent_coinbase` | The parent block's coinbase transaction |
| `coinbase_merkle_branch` | Merkle path from the coinbase (leaf 0) to the parent's `hash_merkle_root` |

Serialization: Borsh, as in ZKas, so pools can reuse one serializer. Limits: branch length ≤ 64, serialized witness
≤ 256 KiB, nesting depth limited (ZKas values, **Verified** in research 0002).

### 4.2 The commitment

The parent's coinbase payload must contain the Sedra commitment **exactly once**:

```
"SDM1" || lowercase-hex( H("sedra_aux_bind1" || sedra_genesis_hash || nonce_free_header_hash) )
```

- `SDM1` (4 ASCII bytes) contains characters outside `0-9a-f`, so it can never appear inside another chain's hex
  commitment, and it differs from ZKas's `ZKMM`/`ZKM1` tags. (ZKas only looks for its own exact tags, **Verified**.)
- `H` is the block-hash hasher; `nonce_free_header_hash` is the Sedra header hash with the nonce set to 0.
- Binding Sedra's genesis hash prevents a commitment for another network (testnet, devnet) from being reused.
- Hex rather than raw bytes, because Kaspa's `getBlockTemplate` passes `extraData` as a UTF-8 string (**Verified** for
  ZKas). Total: 68 bytes.
- Zero or more than one `SDM1` occurrence: the proof is invalid.

### 4.3 Nonce binding

For an AuxPoW-accepted Sedra block, its header nonce must equal the first 8 bytes (little endian) of the parent header
hash. This gives each Sedra block exactly one valid witness. ZKas added this rule in a security fork after a solution
could be counted for two blocks (**Verified**, research 0002).

### 4.4 Validation (dual acceptance)

1. If the Sedra header's own kHeavyHash meets its target: valid as today. A missing or bad witness never invalidates
   a natively valid block.
2. Otherwise, after activation: the block is valid if all of these hold:
   - the witness decodes within the limits of 4.1;
   - the header nonce matches the nonce binding (4.3);
   - the parent coinbase contains exactly one `SDM1` commitment equal to the expected value (4.2);
   - the coinbase is leaf 0 under the parent's `hash_merkle_root` via the branch;
   - kHeavyHash(parent header) ≤ Sedra's target for this block (from the Sedra header's `bits`).
3. Otherwise the block is invalid (proof of work failure).

The parent's own difficulty, its parents, its DAA score and whether Kaspa accepted it are **not** checked. Section 2
explains what that means.

### 4.5 Self-parent ban

A Sedra block's own coinbase must not contain a valid `SDM1` commitment, otherwise one solution could count as both a
native Sedra block and the parent of another Sedra block (the ZKas double-credit bug, **Verified** research 0002).
Other chains' tags (for example ZKas's `ZKM1`, which Sedra blocks already carry when PuddlePool merge-mines ZKas on
Sedra) remain allowed.

### 4.6 Kaspa header format

The parent is a **current** Kaspa header. Kaspa moved to block version 2 with compressed parents after rusty-kaspa
v1.0.1 (**Verified**, research 0004), while Sedra's own headers stay on version 1. The Sedra node therefore needs
Kaspa's current header hashing for parents only. If Kaspa changes its header format again in a future hard fork, merged
mining stops working until Sedra updates its parent decoder; native Sedra mining continues regardless (dual acceptance).
How Sedra tracks Kaspa's header changes is an open question (section 10).

### 4.7 Block level and pruning proof

For an AuxPoW-accepted block, the block level used by the pruning proof is computed from the parent's kHeavyHash
value, as ZKas does (**Verified**). Pruning-proof validation applies the same dual rule.

### 4.8 What does not change

Emission schedule and total supply, block rate (1 block per second), GHOSTDAG parameters, difficulty adjustment
algorithm, addresses, transaction format, coinbase rewards and maturity. No coins are created for anyone by this
proposal: no premine, no developer fee.

## 5. Activation (Proposed)

- Activation by DAA score, `aux_pow_activation_daa_score`, an open-ended rule ("from DAA score X on"), using the same
  pattern as the v2.0.0 rules (research 0001).
- The DAA score is chosen and announced only after a public testnet, with several weeks of notice.
- A new P2P protocol version carries the witness field. After activation, nodes that do not understand AuxPoW (today's
  Go nodes) cannot validate merged-mined blocks and must be replaced by the Rust node. Before activation, the Rust node
  keeps protocol version 5 for compatibility with Go nodes.
- The release that contains the rule is signed, reproducibly built and published with checksums.

## 6. Pools and miners

- Kaspa nodes need no change; the commitment goes into the pool's `extraData` (**Verified** for ZKas).
- Space: Kaspa allows 204 bytes of coinbase payload; about 145 remain for the pool. `SDM1` and `ZKM1` together use
  136 bytes, leaving about 9 bytes for the pool's own tag. A third chain does not fit (**Inferred**, arithmetic from
  verified constants, research 0002).
- Pools need per-chain logic: a Sedra template subscription, a per-share check against Sedra's target, proof building
  and submission. PuddlePool's Miningcore supports one auxiliary chain per pool today and needs multi-aux support
  (milestone, issue #12).

## 7. Backwards compatibility

This is a hard fork. After activation, nodes without AuxPoW support reject merged-mined blocks and end up on a separate
chain. Every node operator, pool, exchange and explorer must move to the new release before activation. Natively
mined blocks remain valid on both sides until the first merged-mined block appears.

## 8. Security considerations

- **Free hashrate cuts both ways (Inferred).** Merged mining attracts hashrate, but a large Kaspa pool could dominate
  Sedra at no cost. Mitigations (for example checkpoints) are possible but have their own trust costs. This draft
  proposes none and asks for discussion.
- **Difficulty swings (Unknown).** Sedra's difficulty adjustment has no merged-mining logic (as in ZKas). How fast it
  reacts when a large pool joins or leaves has not been measured; the testnet must test it.
- **Witness outside the hash.** Peers can strip or replace the witness. Native proof of work is checked first, and a
  missing witness is treated as a proof-of-work failure, not as a permanently invalid block (ZKas behaviour, **Verified**).
- **Denial of service.** Size, branch and nesting limits as in 4.1. ZKas needed several hardening rounds after launch
  (double credit, oversized witness, decoder crash, nesting; **Verified**). A Sedra implementation must include these
  from the start and be fuzzed.
- **Cross-implementation hashing.** Sedra must hash Kaspa parent headers exactly as Kaspa does. Test vectors from real
  Kaspa mainnet blocks are required.

## 9. Reference implementation and tests

Not written yet. Planned in the Rust node (`necatgit/sedra-rusty`), milestone M10 (#10), porting about 1,200 lines of
ZKas's AuxPoW core. Required tests: valid and invalid proofs, every rule in 4.4 broken one at a time, nonce binding,
exactly-once and self-parent rules, size limits, real Kaspa headers as parents, the activation boundary, and fuzzing of
the decoder. As in step 1, each test must be shown to fail when its rule is broken.

## 10. Open questions

1. Is the free-hashrate trade-off (section 8) acceptable to Sedra holders, and is any mitigation wanted?
2. Should Sedra coordinate a shared commitment format with ZKas, to save coinbase space for pools?
3. How does Sedra keep up with future Kaspa header changes (4.6)?
4. Which Kaspa pools besides PuddlePool would support Sedra?
5. How should the activation DAA score and the notice period be decided, and with whom?
6. Does the Sedra team support this proposal (asked 2026-11-05, see QUESTIONS.md Q3)?

## What this does NOT mean

- It does not mean merged mining will happen, or when. Nothing is scheduled.
- It does not mean the Sedra team has agreed. They have been asked; no answer yet.
- It does not mean Sedra would inherit Kaspa's security.
- It does not change emission or supply, and it does not create coins for the author.
- It says nothing about prices, listings or adoption.
