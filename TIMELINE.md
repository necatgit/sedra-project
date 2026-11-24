# Timeline and AI effort

How long each step took from the start of the project, and how much AI work went into it. Regenerated with `python tools/update_timeline.py <transcripts>`; see the notes at the end for what the numbers mean.

**Project start:** 2026-11-05 07:19 UTC (first message of the session in which the project began). **Last update:** 2026-11-24 13:03 UTC.

## Milestones and closed issues

| Closed (UTC) | Since start | Issue | AI calls in this phase | Fresh tokens (in / out) |
|---|---|---|---|---|
| 2026-11-05 20:45 | 13 h 26 min | #1 Review the 2.0.0-relaunch release | 181 | 1,017 k / 184 k |
| 2026-11-05 20:45 | 13 h 26 min | #2 Study the ZKas AuxPoW design | 0 | 0 k / 0 k |
| 2026-11-05 20:45 | 13 h 26 min | #3 Can one Kaspa block carry both ZKas and Sedra commitments? | 0 | 0 k / 0 k |
| 2026-11-05 21:14 | 13 h 55 min | #4 Decide the implementation path: Go node or Rust codebase | 94 | 317 k / 88 k |
| 2026-11-05 23:04 | 15 h 45 min | #20 M1: Sedra network on rusty-kaspa v1.0.1 (genesis, names, prefixes, ports, subsidy table, params) | 82 | 106 k / 68 k |
| 2026-11-06 07:03 | 23 h 44 min | #21 M2: Subsidy parity with sedrad at every month boundary | 88 | 547 k / 72 k |
| 2026-11-06 07:51 | 24 h 32 min | #22 M3: Decode and validate real Sedra headers offline | 21 | 32 k / 23 k |
| 2026-11-06 08:25 | 25 h 06 min | #23 M4: P2P v5 handshake with a local Go sedrad | 30 | 46 k / 27 k |
| 2026-11-06 08:48 | 25 h 29 min | #25 M6: v2.0.0 rules (difficulty reset, treasury outputs) behave exactly like Go | 37 | 80 k / 54 k |
| 2026-11-06 09:04 | 25 h 45 min | #27 M8: Mining parity on an isolated test setup | 19 | 26 k / 20 k |
| 2026-11-06 17:21 | 34 h 02 min | #26 M7: UTXO commitment and supply parity with the Go node | 228 | 2,221 k / 242 k |
| 2026-11-06 18:20 | 35 h 01 min | #24 M5: Full sync from a local Go node, then follow the tip | 17 | 11 k / 5 k |
| 2026-11-09 09:09 | 97 h 50 min | #6 Publish the first full draft of SIP-0001 | 493 | 2,040 k / 400 k |
| 2026-11-10 18:52 | 131 h 33 min | #10 M10 / Step 2: Port the AuxPoW verifier into the Rust Sedra node behind an activation point | 847 | 2,365 k / 745 k |
| 2026-11-10 18:52 | 131 h 33 min | #11 Unit and consensus tests for AuxPoW | 0 | 0 k / 0 k |
| 2026-11-10 18:53 | 131 h 34 min | #5 Effort and timeline estimate | 0 | 0 k / 0 k |
| 2026-11-14 10:47 | 219 h 28 min | #28 M9: Seven-day soak next to Go nodes | 381 | 1,399 k / 339 k |
| 2026-11-16 08:30 | 265 h 11 min | #29 Security back-ports from later rusty-kaspa releases (Q31) | 496 | 1,696 k / 480 k |
| (open) | 461 h 44 min | work since the last closed issue | 2028 | 11.8 M / 1,593 k |

A phase counts **all** AI work between two closed issues, not only the issue in that row. For example, the first row includes the project setup (repository, rules, identity), and the M2 row includes setting up the test VM, the build fix for GCC 15 and the coverage measurement. Several issues closed in the same minute share one phase; their AI effort is counted on the first of them.

## Per day

| Day (UTC) | AI calls | Fresh tokens (in / out) | What happened |
|---|---|---|---|
| 2026-11-05 | 399 | 1,505 k / 374 k | [first-research](updates/2026-11-05-first-research.md), [project-start](updates/2026-11-05-project-start.md) |
| 2026-11-06 | 479 | 3,103 k / 464 k | [full-sync-and-security](updates/2026-11-06-full-sync-and-security.md), [rust-node-progress](updates/2026-11-06-rust-node-progress.md) |
| 2026-11-07 | 252 | 1,445 k / 223 k | [soak-and-security-review](updates/2026-11-07-soak-and-security-review.md) |
| 2026-11-08 | 17 | 53 k / 12 k | - |
| 2026-11-09 | 385 | 1,111 k / 301 k | - |
| 2026-11-10 | 764 | 1,851 k / 726 k | [merged-mining-node-and-pool](updates/2026-11-10-merged-mining-node-and-pool.md) |
| 2026-11-11 | 101 | 376 k / 65 k | - |
| 2026-11-13 | 111 | 363 k / 91 k | - |
| 2026-11-14 | 221 | 1,100 k / 242 k | - |
| 2026-11-15 | 160 | 734 k / 162 k | - |
| 2026-11-16 | 556 | 1,256 k / 402 k | [first-release-and-public-node](updates/2026-11-16-first-release-and-public-node.md) |
| 2026-11-17 | 281 | 929 k / 219 k | - |
| 2026-11-18 | 303 | 1,629 k / 251 k | - |
| 2026-11-19 | 170 | 807 k / 155 k | - |
| 2026-11-20 | 310 | 2,996 k / 232 k | [testnet-kit](updates/2026-11-20-testnet-kit.md) |
| 2026-11-21 | 99 | 850 k / 75 k | - |
| 2026-11-22 | 178 | 1,398 k / 133 k | [week](updates/2026-11-22-week.md) |
| 2026-11-23 | 92 | 1,406 k / 85 k | - |
| 2026-11-24 | 164 | 831 k / 128 k | - |

## AI usage in total

| | Tokens |
|---|---|
| Model calls | 5,042 (of which 367 by research agents) |
| Fresh input (new text read: messages, files, command output) | 23,739,748 |
| Output (text and code written by the AI) | 4,341,988 |
| Re-read from cache (the conversation so far, read again on every call) | 1,288,732,263 |

## Notes

- Times are wall-clock time since the project start, nights and pauses included, not working hours.
- "Closed" is the moment the GitHub issue was closed, which can be some time after the work itself was done.
- Model: Claude (Anthropic), used through Claude Code. Every model call re-reads the conversation so far from a cache; that is why the cache figure is so large. Fresh input and output reflect the actual work.
- Only token counts and timestamps are taken from the local transcripts; no conversation content is published.
- Not included: an earlier conversation about the idea before the project started, and the human time spent.
- The same sessions also contain some work on Nec's pool PuddlePool (for example its solo pool on 2026-11-07); it is counted here too, so the figures are an upper bound for this project.
