# 2026-11-27: The test chain is running

The Sedra public testnet chain started from genesis on **Friday 2026-11-27 at 10:00:00 UTC**, as planned
([testnet/OVERVIEW.md](../testnet/OVERVIEW.md) D4), with the published node release
[`sedra-v0.2.0-testnet.1`](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.2.0-testnet.1). Live status:
<https://testnet.puddlepool.com>.

## What happened (UTC)

| Time | Event | Label |
|---|---|---|
| 10:00:00 | A one-time timer on the operator host restarted seed1 in mining mode (`--enable-unsynced-mining`) | **Verified** (systemd journal of the launch unit) |
| 10:00:16 | The native miner started; it mines to the faucet wallet | **Verified** (same journal) |
| 10:10-10:17 | Automated check, three runs: all ten testnet services active; seed1, seed2 (the VPS) and the unchanged Go node (sedrad v2.0.0) on the same tip, DAA score 3,373, then 3,820, then 4,290; miner 0 rejected blocks; public status page under a minute old | **Verified** (check output) |
| 10:41:05 | seed1 restarted without `--enable-unsynced-mining` now that the tip is recent ([RUNBOOK §3.3](../testnet/RUNBOOK.md)); miner back at 10:41:32, all nodes again on one tip | **Verified** (operator check after the restart) |

## Block rate

The first half hour ran faster than one block per second: the chain starts at the genesis difficulty, and the
difficulty adjusts over a window of past blocks. DAA score on the operator's status data (local `status.json`):

| Time (UTC) | DAA score | Rate since previous row |
|---|---|---|
| 10:16:52 | 4,421 | |
| 10:21:57 | 4,980 | 1.83 per second |
| 10:27:03 | 5,348 | 1.20 per second |
| 10:32:08 | 5,689 | 1.12 per second |
| 10:37:38 | 6,007 | 0.96 per second |

A separate measurement on the public status page, 10:29:36-10:34:45, gave 308 DAA in 309 s (1.00 per second). So the
rate has settled near the target. **Inferred** from these numbers at one block per second: the chain is about one hour
ahead of the plan, so the self-parent ban starts (DAA 172,800) about **2026-11-29 09:00 UTC** and merged mining
switches on (DAA 345,600) about **2026-12-01 09:00 UTC**, still on the announced day. The status page shows a live
estimate; in the first hour its rate-based estimates were skewed by the fast start.

## Still open

- **Seed1 and pool addresses** are not public yet (the guide lists seed2, `62.83.121.25:22211`); they will be posted
  in [#13](https://github.com/necatgit/sedra-project/issues/13) once they are open to the public.
  *Correction 2026-11-27 (later the same day):* seed1 will not be published (it runs on the operator's home
  network); the pool address follows once there is public access that does not expose that network.
- **Pool with a real GPU miner:** in the rehearsal the pool rejected shares as "low difficulty" after a difficulty
  change with CPU miners (cause **Unknown**), and no real GPU miner has mined at the testnet pool yet. This is planned
  before activation.
- Activation, the ban start and the old Go node dropping off have not been seen on the real hosts yet; they come on
  about 11-29 and 12-01.

## What this does NOT mean

- It does not mean merged mining works on the testnet: it is not switched on until DAA 345,600 (about 12-01).
- It does not mean any of the eight pass criteria of [SIP-0003](../proposals/SIP-0003-public-testnet.md) is met; the
  test runs at least two weeks after activation and ends with a public report.
- Nothing changes on Sedra mainnet: no date, no change to supply, balances or rewards. Testnet coins have no value.
- The dates above are estimates from the block rate, not promises.
