# Dry run of the public testnet kit, 2026-11-20 (#13)

Evidence record. Labels: **Verified** (run, output quoted), **Inferred** (reasoned), **Unknown**.

## Setup

| | |
|---|---|
| Host | sedra-dev (test VM), approved by Nec 2026-11-20. Loopback only, data under `/data/testnet-dryrun` (deleted afterwards), ports 162xx and 222xx (nothing on the mainnet ports 221xx), `MemoryMax` per process (`systemd-run --user --scope`). sedra-dev's own services (`sedra-rusty`, `sedrad-dev`) stayed active throughout (checked before and after) |
| Sedra node | sedra-rusty `testnet-kit`, binary built from the tree committed as `3c06131b` (its version string shows the parent `71c08bea`, built before the commit), SHA256 `617a42ce769e7b55…`. `--testnet --aux-pow-activation-override=4000` |
| Nodes | A (mines, `--enable-unsynced-mining`), B (`--connect` A, as a participant), C (empty, started after activation, `--addpeer` A), old-go: unmodified Go sedrad **2.0.0** `--testnet` (`--connect` A) |
| Parent | private Kaspa testnet-10 chain from genesis on loopback, upstream kaspad **2.1.0** (`4863866f`), two nodes, no DNS seeding (a stand-in for Kaspa's public testnet-10) |
| Pool | Miningcore `sedra-merged-mining`, build `57944adc` (from its startup line), on the Windows host through SSH tunnels; config `contrib/testnet/dryrun/miningcore-dryrun.json` with `genesisHash` = testnet genesis; throwaway Postgres in WSL; payouts **disabled** |
| Miners | `sedra-testnet-miner` (native, 2 threads, about 2.3 MH/s) on A; the e2e stratum CPU miner (about 1.8 MH/s) on the pool with `a=<participant sedratest: address>` |
| Monitor | `sedra-testnet-monitor`, A as reference, B over gRPC, old-go over `sedractl://`, interval 20 s, depth 30 |
| Time | 2026-11-19 23:57 to 2026-11-20 00:12 UTC |

## Results

| What | Result | Label |
|---|---|---|
| Network | node A `getBlockDagInfo`: network `testnet-10`, genesis/pruning point `f896a3034873be1739fc4359236899fd3d65d2bc94f9780df0d0da3eb1cc4370`; the Go node reports `sedra-testnet-10` | Verified |
| Go/Rust parity on native blocks (Q47 condition) | old-go accepted every block of the Rust-mined chain up to DAA 4000 (4,000 native blocks): 31 of 31 agreement checks before activation present and on its selected chain | Verified (local chain; not yet a public one) |
| Activation at the score | first merged-mined block at DAA **4000** (`e7340aa3…f080`); merged-mined blocks below 4000: **0** | Verified |
| Pool before / after | Miningcore: 398 aux candidates rejected (`BlockInvalid`) from 01:06:55 to 01:10:24.415 local time, first `ACCEPTED` at 01:10:24.507. The last two rejections came 0.1 to 0.3 s before the first acceptance; that they were templates below DAA 4000 is **Inferred** (the candidate's DAA is not in the log) | Verified / Inferred |
| Blocks after activation (monitor, by 00:12 UTC) | 408: native 232, merged 176, red 0. Tags: `dryrun-native` 231, `dryrun-pool` 176, untagged native 1 (the control block below) | Verified |
| Per-miner address | pool database at about 00:11 UTC: 131 Sedra blocks (`e2e-sedra`, pending) credited to the participant's `sedratest:qpst007q…tfdgp`; all 4,485 Sedra share copies carry that address | Verified |
| Upgraded nodes agree | B: 39 of 39 checks present and on its selected chain, max lag 0 DAA; C (fresh): synced from scratch, IBD of 4,217 headers and blocks, same sink as A (`344180da…f0b2`) | Verified |
| Old node after activation | old-go log: `Rejected block d94654d9…1dea … block has invalid proof of work: ErrInvalidPoW`, then `Disconnecting from … 127.0.0.1:22211`. That block is merged-mined at DAA 4000 (monitor). old-go stayed at virtual DAA 4000 while A and B went on to 4408; agreement: first miss at the first check after activation (DAA 4042) | Verified |
| Self-parent ban | `sedra-testnet-miner --sdm1 --blocks 1` at DAA 4140: `block REJECTED: daa 4140 Reject(BlockInvalid)`, node A log `Validation failed for block 2032aa56…8e68: coinbase carries a merged-mining (SDM1) commitment`. The same command without `--sdm1`: `block accepted: daa 4140`. Accepted blocks with SDM1 in their own coinbase: 0 | Verified |
| Wallet | Go sedrawallet 2.0.0 against A: CLI send of 25 SDR (`5c9f7bb0…efef`), `faucet.sh` 10 SDR (`00bd86ca…d47c`) to the participant address; its balance afterwards 35.00000000. `faucet.sh` refused `sedra:qqq` (exit 2) | Verified |
| Resources | memory peak per scope: A 584 MB, B 472 MB, C 658 MB, old-go 931 MB, Kaspa nodes 252 / 222 MB, monitor 43 MB; disk A 43 MB, old-go 110 MB after 4,400 blocks | Verified |

The monitor summary at the end (`summary.py monitor --activation 4000 --reference A`, 00:12:05 UTC):

```
| UTC day | native | merged | red | total |
| 2026-11-19 | 1540 | 0 | 0 | 1540 |
| 2026-11-20 | 2694 | 176 | 0 | 2870 |
Merged-mined blocks below the activation score (must be 0): **0**.
Accepted with SDM1: 0; at or after the ban start (must be 0): **0**.
| A | 41 | 100.0% | 97.6% | 4408 | 0 | 1.0.1 |
| B | 41 | 100.0% | 97.6% | 4408 | 0 | 1.0.1 |
| old-go | 40 | 90.0% | 94.4% | 4000 | 408 | 2.0.0 |
| B | 39 | 39 | 39 | none |
| old-go | 36 | 31 | 31 | 4042, 2026-11-20 00:10:38 UTC |
```

(old-go's 90% reachability: the first four polls used gRPC, see finding 1. The synced share below 100% is the first
poll at DAA 0.)

## Findings, fixed in the kit

1. **The Rust gRPC client gets no answer from Go sedrad v2.0.0** (requests time out). The monitor now asks Go nodes
   through Go's own `sedractl` (`sedractl://HOST:PORT`). sedra-rusty `582be8a5`.
2. **Miningcore must be given the testnet `genesisHash`.** Its default for `coin: sedra` is the mainnet genesis
   (`SedraAuxPowSerializer.MainnetGenesisHash`), so every commitment would be for the wrong network. Found while
   writing the config (the devnet e2e run never hit it: the devnet genesis equals mainnet's). Set in both configs and
   documented. Not changed in Miningcore.
3. **Miningcore checks the `a=` address against the parent's network:** with a Kaspa devnet parent, a `sedratest:`
   address is refused (`Decoded address is of wrong network. Expected KaspaDev`). On the real testnet (Kaspa TN10 +
   `sedratest:`) both are testnet (**Inferred**, not run against TN10). The dry run uses a private Kaspa testnet chain.
4. **A node started with `--connect` accepts no inbound peers** (upstream behaviour). The runbook tells seeds and
   participants to use `--addpeer`.

## Not covered

- Pool payouts on either chain (payouts disabled; the Kaspa TN10 payout wallet is **Unknown**, runbook 2.1).
- A pruning proof with merged-mined headers (the chain stayed far below the pruning depth of 185,798).
- The ban start before activation: with activation 4000 the ban runs from genesis (4000 - 172,800 < 0), so only the
  "after" half was shown here; the "before" half is covered by the consensus tests on `m10-auxpow`.
- The public Kaspa testnet-10 as the parent, public seed nodes, outside participants, two weeks of running.

## What this does NOT mean

- It is not the public testnet and not a pass of any SIP-0003 criterion: one host, loopback, our own miners, 15 minutes.
- The Go/Rust parity seen here is on a short local chain; it does not answer Q52 (whether anyone runs testnet-10 and
  whether its rules match mainnet's).
- It does not schedule anything.
