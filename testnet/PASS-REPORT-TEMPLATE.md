# Public testnet report: merged mining on the Sedra testnet (template)

<!--
Template for the dated report SIP-0003 §4.6 asks for. Copy to research/NNNN-public-testnet-report.md when the testnet
ends; raw monitor summaries and logs go to research/archive/. One section per exit criterion of SIP-0003 §3, in its
order and with its wording. If the Sedra team changed the criteria (Q51), use their version here and say so in the
header. Every result is Verified (evidence a reader can check), Inferred (from what) or Unknown. Fill every
"Result" line with PASS, FAIL or NOT SHOWN; never leave one out.
-->

| | |
|---|---|
| Status | Draft / Final, YYYY-MM-DD |
| Issue | #13 |
| Criteria | SIP-0003 §3 as agreed with the Sedra team on YYYY-MM-DD (Q51), or: SIP-0003 §3 unchanged |
| Node release | sedra-rusty `sedra-v0.2.0-testnet.N` (commit, SHA256 of the binary) |
| Pool | Miningcore `sedra-merged-mining` @ commit; config: `contrib/testnet/pool/miningcore-testnet.json` @ commit |
| Parent network | Kaspa testnet-10, kaspad version(s) seen during the test |
| Chain | sedra-testnet-10, fresh from genesis / joined existing chain (Q52) |
| Launch | YYYY-MM-DD HH:MM UTC, DAA score |
| Ban start | DAA score, YYYY-MM-DD HH:MM UTC (first block at or above it) |
| Activation | DAA score, YYYY-MM-DD HH:MM UTC; first merged-mined block: hash, DAA |
| End | YYYY-MM-DD, days after activation: N (minimum 14) |
| Nodes in the monitor | names, operator (this project / Sedra team / others), version |

## Summary

| # | Criterion (SIP-0003 §3) | Result |
|---|---|---|
| 1 | Activation at the announced DAA score without a split among upgraded nodes; the self-parent ban starts `2 x finality_depth` earlier | |
| 2 | Merged-mined and natively mined blocks side by side, accepted by every upgraded node | |
| 3 | Old nodes behave as predicted: before activation they follow the chain, after it they reject merged-mined blocks and stop following | |
| 4 | A node started from scratch after activation syncs, including the pruning proof with merged-mined headers | |
| 5 | A pool pays both coins correctly (Kaspa testnet coins and Sedra testnet coins) and per-miner addresses work | |
| 6 | Wallets: the Go `sedrawallet` sends and receives | |
| 7 | At least one participant outside this project runs a node or mines, and reports what they saw | |
| 8 | At least two weeks after activation without a consensus failure; every problem found is fixed and re-tested | |
| 9 | *Proposed addition (2026-11-25), beyond the eight criteria the Sedra team accepted:* one Kaspa testnet-10 coinbase with both a ZKas and a Sedra commitment; both aux chains accept, no tag interference, no double credit | |

Overall: PASSED / NOT PASSED. One sentence why.

## 1. Activation without a split; ban start

- **Activation:** upgraded nodes in the monitor, and for each: checks of reference chain blocks between activation
  - 1,000 and activation + 10,000 DAA, misses (must be 0). Source: `agreement.csv`, summary of YYYY-MM-DD.
- **Ban start:** native block with an `SDM1` commitment before the ban start: hash, DAA, accepted (miner output, node
  log). Same after the ban start: DAA, rejected with `CoinbaseCarriesMergeMiningCommitment` (node log line). Summary:
  accepted SDM1 blocks at or after the ban start = 0.
- Evidence:
- Result:

## 2. Merged-mined and native blocks side by side

- Blocks after activation: native N, merged N, red N (summary table per day).
- Share per coinbase tag (pool), largest share and when (SIP-0001 §8 asks to watch it).
- Merged-mined blocks below the activation score (must be 0).
- Every upgraded node agrees (criterion 1 table).
- Difficulty when merged mining started and stopped (SIP-0001 §8 "difficulty swings": measured how?).
- Evidence:
- Result:

## 3. Old nodes

- Old nodes observed: Go sedrad v2.0.0 (who ran it, how many).
- Before the first merged-mined block: reference chain blocks checked, missed (must be 0).
- First miss: DAA and time, compared with the first merged-mined block (must match).
- After: what the old node did (stuck at which DAA, log lines, did it ban peers, did it keep running).
- Behaviour around the ban-test block (accepted by old nodes? any effect?).
- Evidence:
- Result:

## 4. Fresh node after activation

- First pruning point above the activation score: hash, DAA, time.
- Fresh node: start time, empty data dir, peers used, sync duration, pruning proof accepted (log line), number of
  merged-mined headers in the proof if known, sink agreeing with seed1 afterwards.
- Evidence:
- Result:

## 5. Pool payouts, per-miner addresses

- Test miners: N, each with its own `kaspatest:` and `a=sedratest:` address.
- Sedra payouts: transaction IDs, amounts, matching the pool's PPLNS accounting; Kaspa TN10 payouts: same.
- A login without `a=`: what happened to its Sedra share (expected: unclaimed, not paid to someone else).
- Evidence:
- Result:

## 6. Go sedrawallet

- Wallet version, node it ran against.
- Received: transaction ID, amount; sent: transaction ID, amount, fee; balances before and after match.
- Evidence:
- Result:

## 7. Outside participants

- Participants outside this project (GitHub handle or "anonymous"): what they ran, their issue links.
- Evidence:
- Result:

## 8. Two weeks without a consensus failure; problems fixed and re-tested

- Days after activation: N. Daily summaries: links.
- Consensus failures (upgraded-node misses, invalid blocks that should be valid or the reverse): list or "none".
- All problems found during the test, each with: issue, cause, fix (commit / release), re-test (how, result).
- Evidence:
- Result:

## 9. Triple coinbase: Kaspa parent with ZKas and Sedra commitments (proposed addition)

- Setup: the testnet pool merges ZKas (a private ZKas testnet chain for the pool only, its own genesis) and Sedra
  under Kaspa testnet-10 parents; ZKas build and version; the pool's `extraData` length and the payload length.
- Shown: Kaspa testnet-10 coinbases carrying exactly one `ZKM1` and one `SDM1`; ZKas blocks and Sedra blocks accepted
  from the same parent work (block hashes on both chains, the parent hash they share); the payload stays within
  Kaspa's 204-byte limit.
- No interference: no block rejected on either chain because of the other chain's tag (node logs, pool logs).
- Shared parents as measured: the monitor's `shared_parents.csv` (Sedra and ZKas block with the same nonce, i.e. the
  same Kaspa parent prefix), count and first pair; the status page shows the same count.
- No double credit: per share and per chain, one credit only, in the pool's accounting.
- ZKas payouts: transaction IDs, or "not shown" if the ZKas wallet daemon was not run on the test chain.
- Evidence:
- Result:

## Open items and things not shown

List everything a reader might assume was tested but was not (for example: Kaspa mainnet as the parent, ZKas on a
public ZKas network rather than a private test chain, a large pool joining and leaving).

## Corrections

Dated notes if anything in this report is corrected later. Never rewrite a published result silently.

## What this does NOT mean

- Passing the testnet does not schedule merged mining on mainnet. A mainnet activation date is chosen with the Sedra
  team after this report (SIP-0001 §5), if at all.
- It does not mean Sedra inherits Kaspa's security (SIP-0001 §2).
- Testnet hashrate, pools and participants say little about who would merge-mine on mainnet.
- Testnet coins have no value.
