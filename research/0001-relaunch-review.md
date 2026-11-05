# 0001: Review of the sedrad 2.0.0-relaunch release

| | |
|---|---|
| Issue | #1 |
| Date | 2026-11-05 (public API samples 15:20-15:35 UTC) |
| Reviewed | `github.com/sedracoin/sedrad`: `main` = `e61214d` (tag v1.0.2) to `relaunch/v2.0.0` = tag `v2.0.0` = `4a1153d`; public node `api.sedracoin.com` |
| Full report | [archive/2026-11-05-0001-relaunch-raw.md](archive/2026-11-05-0001-relaunch-raw.md) (all file:line references, commands and outputs) |
| Review | The treasury and supply findings were re-checked independently; see "Review notes" |
| Questions to the Sedra team | Sent to the Sedra owner on 2026-11-05, acknowledged the same day. **No answers yet.** This document will be updated with the answers, dated. |

Labels: **Verified** = checked in code or data, with a reference. **Inferred** = reasoned from evidence, could be wrong.
**Unknown** = not determinable from the sources.

## Summary

- **What the release changed (Verified).** 16 commits on top of `main`, with two consensus changes, both hard forks and
  both already in the past:
  1. A difficulty reset to genesis difficulty for DAA scores 53,625,512 to 53,628,152.
  2. A treasury allocation: an extra coinbase output to a fixed treasury address, 10M SDR per output in DAA window
     53,632,372 to 53,632,571 and 1M SDR per output in DAA window 53,633,267 to 53,633,720. According to the code
     comments this produced 163 × 10M + 400 × 1M = **2,030,000,000 SDR** (not independently counted, because those
     blocks are pruned).
- **Nothing is scheduled for the future (Verified).** The P2P protocol version (5), PoW and subsidy rules are unchanged,
  and the live block reward matches the published table.
- **Release hygiene (Verified).** The `v2.0.0` tag is unsigned. No binary checksums are published in the repository.
  Several commits, including one that cannot sync the chain, report the same version `2.0.0-relaunch`, so the version
  string cannot show which code mainnet runs.
- **The treasury has no on-chain timelock (Verified).** The code and commit messages describe the treasury as a
  "2-of-3, CLTV-timelocked multisig" with multi-year vesting. The script revealed on chain when the treasury spends is a
  plain 2-of-3 multisig, and its hash matches the address in the code. Any two of the three key holders can move the
  funds at any time. Vesting code exists in the wallet library but is not used by the wallet program.
- **Treasury balance (Verified): 32,931,757.98 SDR** on 2026-11-05. Compared with the 2.03B stated in the code, about
  **1.997B SDR has left the treasury address**. Only 16 outgoing transactions (228,322,485 SDR in total) are visible,
  because the public explorer reports its transaction index as out of date. Where the remainder went is **Unknown**.
- **Circulating supply vs published code (Verified arithmetic, cause Unknown).** The public node reports about 26.68B
  SDR in circulation. The published code, in every released version, can have created at most about 18.65B SDR by
  the current DAA score, or 20.68B including the treasury. The difference is about **6.0B SDR** (6,000,000,121 SDR at
  DAA 61,119,321). The published code does not explain it.

## What these findings do NOT mean

- They do **not** show that anyone acted improperly. The supply difference needs an explanation, and there may be a
  legitimate one: for example, an allocation documented elsewhere, a UTXO snapshot at the relaunch, or code that ran on
  the old chain but is not in the repository. The calculation could also be missing something; it is published in full
  in the archived report so anyone can check it.
- Moving funds from a 2-of-3 multisig is what that script allows. The finding is that the **description** (timelocked
  vesting) does not match the script.
- They do **not** mean mainnet runs code other than `4a1153d`, only that this cannot be proven from the version string.
- They do **not** mean the chain is unsafe today: all relaunch rules ended near DAA 53.63M.
- They say nothing about whether the merged-mining fork will happen or be supported by the Sedra team.

## Implications for the merged-mining fork (Inferred)

- Build on `v2.0.0` / `4a1153d`. Older code cannot follow mainnet, and every past rule (reset window, both treasury
  windows) must stay in the code forever or new nodes cannot sync.
- The activation pattern to reuse: a gate on the block's own DAA score, used by both block building and validation. For
  merged mining it is an open-ended "from DAA score X" rule, not a window.
- Do better than v2.0.0: bump the P2P protocol version so outdated nodes disconnect clearly, put the commit hash in the
  version string, sign the release tag and publish checksums.
- Merged mining changes header and PoW validation, which v2.0.0 never touched. There is no precedent for it in this
  code.

## Questions sent to the Sedra owner (2026-11-05)

Status is tracked in [QUESTIONS.md](../QUESTIONS.md) (Q4).

1. Is the treasury's vesting enforced some other way, or is the "CLTV-timelocked" description out of date?
2. Who holds the three treasury keys?
3. Where did the ~1.997B SDR that left the treasury go, and is there a plan for how the treasury is used?
4. Can the explorer's transaction index be repaired?
5. Where does the ~6.0B SDR difference between circulating supply and the published emission come from?
6. Which commit and toolchain built the mainnet binaries, and can checksums and a signed tag be published?
7. Who mined the blocks in the reset and treasury windows, and were independent miners online?

## Review notes

Re-checked independently on 2026-11-05 (outside the original review):

- Treasury balance: `GET https://api.sedracoin.com/addresses/sedra:pp8a4l47q0qjwlwgqvnmp5ppssk6zpn9hat58vaw6jkxkee2aqduue9252wc3/balance`
  returned `3293175798122500` seep (1 SDR = 10^8 seep); `/transactions-count` returned 16; `/info/health` returned
  `"Transactions not up to date"`.
- Treasury script: the redeem script in spending transaction `8b81111b...` has the form
  `OP_2 <key> <key> <key> OP_3 OP_CHECKMULTISIG` with no other opcodes, and its BLAKE2b-256 hash is
  `4fdafebe03c1277dc80327b0d021842da10665bf5743b3aed4ac6b672ae81bce`, equal to the script hash in
  `domain/dagconfig/params.go` at `4a1153d`.
- Supply: recomputed from the subsidy rules in `coinbasemanager.go` at `4a1153d` (500 SDR per DAA score before
  15,519,600, then the 192-entry monthly table, month = 2,629,800 DAA). The code pays only blocks that are added to the
  DAA count (`calcMergedBlockReward` returns 0 otherwise), and the genesis coinbase has no outputs, so this sum is an
  upper bound. Result at DAA 61,119,321: 18,651,819,421 SDR; supply 26,681,819,542 SDR; difference minus treasury:
  6,000,000,121 SDR. Using the older subsidy table for all blocks before the relaunch gives ~4.40B instead; it is
  unexplained in both cases. The v1.0.0 code differs from `main` only in that table.
- Not carried over from the full report: an inference from commit timestamps about who controlled block production
  during the treasury windows. It rests on unauthenticated timestamps, so it is a question (7 above), not a finding.
