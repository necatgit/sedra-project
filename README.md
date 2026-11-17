# Sedra project: merged mining and a second node

The public home of the work: research, decisions, roadmap, proposals, questions and answers, release notes and
updates. Code lives in [sedra-rusty](https://github.com/necatgit/sedra-rusty) (the Rust node). This repository was
called `sedra-merged-mining` until 2026-11-15; old links redirect here.

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
draft: reviewed by Nec on 2026-11-09 and open for public comment. The plan for the public testnet that has to come
before any activation is [SIP-0003](proposals/SIP-0003-public-testnet.md) (draft, open for public comment in [necatgit/sedra-sips](https://github.com/necatgit/sedra-sips) since 2026-11-17).

## How to follow along

- **[ROADMAP.md](ROADMAP.md)**: phases, current status and target dates
- **[updates/](updates/)**: dated progress updates, newest first
- **[research/](research/)**: findings with evidence anyone can check
- **[QUESTIONS.md](QUESTIONS.md)**: open questions, who was asked, and the answers
- **[TIMELINE.md](TIMELINE.md)**: how long each milestone took from the start, and how much AI work went into it
- **[AGENTS.md](AGENTS.md)**: the working rules, including how claims are verified
- **Issues**: one issue per piece of work. Anyone can comment, ask questions or point out problems
- **Watch** this repository on GitHub to get notified of new updates and releases

## Who

Developed by **Nec** ([@necatgit](https://github.com/necatgit)).

**Disclosure:** Nec holds about 250M SDR (roughly 1% of circulating supply) and has a direct interest in Sedra
succeeding. This proposal creates no new coins for Nec: no premine, no developer fee. Nec will not sell SDR from the
public announcement of the activation date until 30 days after activation.

## How this project is built

This project is developed together with an AI, and that is stated openly.

**Claude** (an AI model by Anthropic, used through Claude Code) does most of the hands-on work: the research and code
reviews, the Rust node code and its tests, setting up and running the test environment, measuring, and writing the
documentation, proposals and progress updates. Commits it writes carry a `Co-Authored-By: Claude` line.

**Nec** leads the project: sets the goals and priorities, makes every decision that matters (such as the move to the
Rust codebase), reviews the results, talks to the Sedra team and the community, and provides the infrastructure:
the hardware, the test server, and the pool that runs Sedra and Kaspa nodes.

Because AI output can be wrong in the same confident tone as when it is right, the work follows strict checking rules
([AGENTS.md](AGENTS.md)):

- Expected values in tests come from Sedra's own Go code or from the real chain, never from the new code itself.
- Every new test is shown to fail when the rule it guards is deliberately broken.
- Findings are labelled Verified, Inferred or Unknown, with evidence anyone can re-check in [research/](research/).
- Nothing touches the live network, wallets or the pool's production systems without Nec's explicit approval.

How much time and AI work each milestone took is recorded in [TIMELINE.md](TIMELINE.md).

## Status

**Phase 2, step 1 is done: the Rust node is released and runs as a public node** (no fork, exactly Sedra mainnet's
current rules). It carries Sedra's network, block rewards and both v2.0.0 relaunch rules, checked against sedrad and
real Sedra blocks (M1-M4, M6, M8), synced the live chain with exactly the same state as the Go node (M5, M7), carries
the security fixes from later Kaspa releases (#29) and passed a seven-day run next to a Go node (M9, 2026-11-14:
10,064 checks, 0 alerts, 0 differences).

- **Releases:** [sedra-rusty v0.1.0](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.1.0) (2026-11-14)
  and [v0.1.1](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.1.1) (2026-11-15, docs and build script
  only). Signed tags, and the same bytes rebuilt on two machines; how to check: `docs/RELEASE.md` in sedra-rusty.
- **Public node:** P2P only, running since 2026-11-14; outside nodes have connected to it since 2026-11-15. It runs on the same physical host
  as Nec's pool PuddlePool, so it is an independent node but not independent hardware; a separate machine is still
  open ([SIP-0002](proposals/SIP-0002-network-resilience.md), #30).
- **Next:** the public testnet with merged mining ([SIP-0003](proposals/SIP-0003-public-testnet.md), #13).

**Step 2, the merged-mining fork, is implemented and tested but not active anywhere** (M10, branch `m10-auxpow`,
2026-11-10): the verifier, the proof as a header field, P2P and mining RPC, the activation gate (`never` on every
network) and the self-parent ban, tested by fuzzing, a two-node sync and an end-to-end run through a pool on a local
test network (401 of 401 merged-mined blocks accepted). Activation needs a date agreed with the Sedra team.

The merged-mining code runs only on local test networks; nothing in it is active on the live Sedra network. The
public node runs the released step-1 node, with the same rules as the Go node, and takes part in the live network like
any other node.
