# Sedra merged mining

An open proposal and development effort to let **Sedra (SDR)** be **merged-mined with Kaspa (KAS)**, the way ZKas
already is. Kaspa miners would then secure Sedra with the same work they already do, at no extra cost.

Everything about this project happens in the open: the plan, the proposals, the code, the timeline and the
problems along the way.

## Why

Sedra uses kHeavyHash, the same proof-of-work as Kaspa, so it competes with Kaspa for the same ASICs. Most of that
hashrate goes to Kaspa, which leaves Sedra with a small hashrate. A small hashrate makes a chain cheaper to attack
and less attractive to miners, pools and exchanges.

Merged mining lets a Kaspa miner earn SDR as well without giving up any KAS. Sedra blocks can then be secured by
Kaspa-level work, while normal Sedra mining keeps working as before.

## What would change (draft)

| Area | Plan |
|---|---|
| Block validity | A block is valid if its own proof-of-work meets the target **or** it carries a valid AuxPoW proof from a Kaspa block that commits to it ("dual acceptance", the same design as ZKas) |
| Emission / supply | **No change** |
| Difficulty adjustment | No change planned; to be tested against merged-mining hashrate swings |
| Treasury | Not part of this proposal |

The full specification is in [proposals/SIP-0001-merged-mining.md](proposals/SIP-0001-merged-mining.md). It is a
draft until the feasibility study is done.

## How to follow along

- **[ROADMAP.md](ROADMAP.md)**: phases, current status and target dates
- **[updates/](updates/)**: dated progress updates, newest first
- **Issues**: one issue per piece of work. Anyone can comment, ask questions or point out problems
- **Watch** this repository on GitHub to get notified of new updates and releases

## Who

Developed by **Nec** ([@necatgit](https://github.com/necatgit)).

<!-- TODO before going public: holder disclosure. Nec holds SDR; state it here plainly (amount optional). -->

## Status

**Phase 0: research and planning.** No consensus code has been written yet. Nothing here affects the running
Sedra network.
