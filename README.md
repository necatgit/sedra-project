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

**Phase 2, step 1: a Rust node with exactly Sedra mainnet's current rules** (no fork yet). Research and the decision
to build on rusty-kaspa are done (#1-#4). The Rust node carries Sedra's network, block rewards and both v2.0.0
relaunch rules, checked against sedrad and real Sedra blocks (M1-M4, M6, M8). It has synced the live Sedra chain
from a Go node and holds exactly the same state (M5, M7). Next: a seven-day run next to Go nodes (M9). See [ROADMAP.md](ROADMAP.md) for details.

The merged-mining fork itself (step 2) has not been started. Nothing here affects the running Sedra network: all tests
run on a separate test machine, and the Rust node under test connects only to a local Go node.
