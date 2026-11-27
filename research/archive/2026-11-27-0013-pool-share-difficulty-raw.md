# Testnet pool share difficulty: diagnosis and fix, 2026-11-27 (issue #13)

Raw evidence for the open rehearsal item R7 ("low difficulty" share rejections, [testnet/REHEARSAL.md](../../testnet/REHEARSAL.md)).
Never edited after publication. LAN addresses are left out: "the pool" is the testnet pool on the operator host
(stratum port 15555, reached over the home LAN), "the test PC" is this project's developer PC (WSL).

## Method

The CPU stratum test miner from the merged-mining end-to-end test (sedra-rusty `contrib/e2e-merged-mining/miner`,
branch `m10-auxpow`, the same tool as in the rehearsal) was copied and given logging only: a timestamp on every line
from the pool (`RX`), and for every share sent (`TX submit`) the difficulty the pool gave (`diff_given`), the
difficulty the miner actually worked to after its own rounding (`diff_worked`), and the share's real difficulty
(`share_diff`). It mined for 180 s to the pool's own testnet addresses (worker `.diag`), single-threaded, about
1.7 MH/s, while the pool log was read for the same minutes. Kaspa testnet-10 had about 28 MH/s at the time
(`https://api-tn10.kaspa.org/info/hashrate` = 2.79e-05 TH/s, 2026-11-27 ~13:00 UTC).

## Run 1: pool at Miningcore `sedra-merged-mining` 1a72553a (as deployed since 2026-11-25), 13:05:01-13:07:50 UTC

Miner log (WSL `/tmp/diag-run1.log`):

```
RX {"jsonrpc":"2.0","method":"mining.set_difficulty","params":[2.746540449147278E-05],"id":null}
TX submit id=101 job=244732 diff_given=0.00002746540449147278 diff_worked=0.000027 share_diff=0.000166
done: shares accepted 2516 rejected 0
```

One `set_difficulty` in the whole run; 2,516 shares sent, 3 of them with `share_diff` a hair below `diff_given`
(rounding at the boundary; the pool accepted all).

Pool log, same minutes:

```
[I] [kas-tn10-sdr-testnet] Difficulty 1.0 of kaspatest:qpunuwj0...a7rkx.diag is above the network difficulty 0.0: capped to 0.0 so every block is sent
Connection closed: kaspatest:qpunuwj0...a7rkx.diag [Duration: 2.8m | Valid Shares: 2516 | Invalid Shares: 0]
```

| Count in the pool log, 13:04:55-13:08:10 | Value |
|---|---|
| Kaspa testnet-10 parent blocks accepted | 89 |
| ZKAS test chain blocks accepted | 2,408 |
| Sedra merged blocks rejected (expected before activation, as in R7) | 114 |
| Lines with "Retarget" or "VarDiff" | 0 |

Cause (Verified by the numbers and the code): `KaspaJob.MaxShareDifficulty` caps the share difficulty at the easiest
chain in the job so that no block is dropped on the rig (Miningcore `src/Miningcore/Blockchain/Kaspa/KaspaJob.cs`,
commit 67391923). The easiest chain was the private ZKAS test chain: difficulty 131,072 hashes = 131,072 / 2^32 =
3.05e-5 in stratum units, times the pool's headroom 0.9 = 2.75e-5, the value sent. Every miner was pinned there and
vardiff never moved; a 500 MH/s GPU would send about 4,000 shares per second (**Inferred** from 500e6 / (2.75e-5 x 2^32)).

## Fix: Miningcore `sedra-merged-mining` 9dcab452

A per-chain setting `capShareDifficulty` (default `true`, so existing configs behave as before); the testnet pool sets
it `false` for the ZKAS chain. Regression test `MergedMining_AChainWithCapShareDifficultyOff_DoesNotLimit` and a
config default test; full suite 959 passed, 0 failed, 1 skipped (`dotnet test`, 2026-11-27). Built on the operator host
from `git archive 9dcab452` (`dotnet publish -c Release`, exit 0) and swapped in at about 13:33 UTC; old build kept as
`build-1a72553a`, old config as `miningcore.json.bak-1a72553a`.

## Run 2: after the fix, 13:34:06-13:36:52 UTC

```
RX {"jsonrpc":"2.0","method":"mining.set_difficulty","params":[0.0004619191275830475],"id":null}
TX submit id=101 job=431 diff_given=0.0004619191275830475 diff_worked=0.000462 share_diff=0.000529
done: shares accepted 156 rejected 0
```

| Count in the pool log, 13:34:00-13:37:00 | Value |
|---|---|
| Kaspa testnet-10 parent blocks accepted | 112 |
| ZKAS test chain blocks accepted | 156 |
| Sedra merged blocks rejected (before activation) | 138 |
| Lines with "Retarget" or "VarDiff" | 0 |

The share difficulty is 17 times higher and now follows the Sedra testnet's network difficulty (the cap working as
intended for Sedra: no Sedra block is dropped). Vardiff still does not move because the miner sits at that cap; the
Sedra testnet difficulty is low because only the operator's native CPU miner (~2.1 MH/s on the status page) mines it.

## Result for R7

- The "low difficulty" rejections of the rehearsal did **not** recur in 2 x 180 s (0 rejected of 2,672). Their cause
  stays **Unknown**; a likely candidate is the cap and vardiff pulling the difficulty in different directions between
  jobs (**Inferred**, not shown).
- The test miner rounds `1/difficulty` below difficulty 1 (`share_target` in its `main.rs`), which can make it work
  to a slightly lower difficulty than given; at the difficulties seen here the effect was 3 shares in 2,516, all
  accepted.

## What this does NOT mean

- It does not mean a real GPU miner works at the pool: no GPU miner was used.
- It does not mean the pool can take any hashrate: before activation every miner is still capped at the Sedra
  testnet difficulty, so a fast GPU sends many shares per second (**Inferred**).
- It does not explain the rehearsal's rejections; it only shows they did not come back in these runs.
