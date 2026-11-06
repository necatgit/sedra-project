# Timeline and AI effort

How long each step took from the start of the project, and how much AI work went into it. Regenerated with `python tools/update_timeline.py <transcripts>`; see the notes at the end for what the numbers mean.

**Project start:** 2026-11-05 07:19 UTC (first message of the session in which the project began). **Last update:** 2026-11-06 18:21 UTC.

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
| (open) | 35 h 02 min | work since the last closed issue | 2 | 2 k / 4 k |

A phase counts **all** AI work between two closed issues, not only the issue in that row. For example, the first row includes the project setup (repository, rules, identity), and the M2 row includes setting up the test VM, the build fix for GCC 15 and the coverage measurement. Several issues closed in the same minute share one phase; their AI effort is counted on the first of them.

## AI usage in total

| | Tokens |
|---|---|
| Model calls | 799 (of which 242 by research agents) |
| Fresh input (new text read: messages, files, command output) | 4,403,635 |
| Output (text and code written by the AI) | 788,501 |
| Re-read from cache (the conversation so far, read again on every call) | 315,679,978 |

## Notes

- Times are wall-clock time since the project start, nights and pauses included, not working hours.
- "Closed" is the moment the GitHub issue was closed, which can be some time after the work itself was done.
- Model: Claude (Anthropic), used through Claude Code. Every model call re-reads the conversation so far from a cache; that is why the cache figure is so large. Fresh input and output reflect the actual work.
- Only token counts and timestamps are taken from the local transcripts; no conversation content is published.
- Not included: an earlier conversation about the idea before the project started, and the human time spent.
