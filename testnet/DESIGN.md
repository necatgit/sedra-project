# Public testnet kit: gaps and design

| | |
|---|---|
| Status | **Approved by Nec 2026-11-20** and implemented (sedra-rusty `testnet-kit`, `582be8a5`); dry run done the same day (section 5). **Running since Fri 2026-11-27 10:00 UTC** (chain started from genesis on time, ([start report](../updates/2026-11-27-testnet-chain-started.md))); merged mining switches on about **Tue 2026-12-01**, the start day the Sedra team announced on 2026-11-26 ([#13](https://github.com/necatgit/sedra-project/issues/13#issuecomment-7192048626)); the earlier chain start (same release, same heights) was decided by Nec on 2026-11-26 ([OVERVIEW.md](OVERVIEW.md) D4); the Sedra team agreed in writing on 2026-11-24 to SIP-0003 as it stands (Q51), and the fresh chain makes Q52 no longer a condition ([OVERVIEW.md](OVERVIEW.md) D4). |
| Issue | #13 |
| Process | [SIP-0003](../proposals/SIP-0003-public-testnet.md) (the testnet), [SIP-0001](../proposals/SIP-0001-merged-mining.md) (the rules tested) |
| Code base | sedra-rusty `m10-auxpow` @ `ac98145` (merged mining, e2e harness in `contrib/e2e-merged-mining/`) |

This note lists what the local end-to-end harness (M10 step 5c) has and what a public testnet that anyone can join
still needs, and proposes the smallest set of changes that closes the gap. Labels: **Verified** (checked, evidence
given), **Inferred** (reasoned, could be wrong), **Unknown**.

## 1. What exists (checked 2026-11-20)

| Item | State | Evidence |
|---|---|---|
| Sedra test network | `sedra-testnet-10`, address prefix `sedratest`, P2P 22211, gRPC 22210, wRPC 17210/18210 | **Verified**: sedra-rusty `consensus/core/src/network.rs:44-65,244-248`@`ac98145`; Go sedrad `domain/dagconfig/params.go:361-421`@`4a1153d` (same name and ports) |
| Testnet genesis | Kaspa's old testnet genesis (timestamp `0x17c5f62fbb6` = 2021-10, bits `0x1e7fffff`), the same in Go and Rust | **Verified**: sedrad `domain/dagconfig/genesis.go:203-218`; SIP-0003 §4.2 |
| Testnet consensus parameters | Rust and Go agree on every parameter compared: 1 block/s, finality depth 86,400, merge depth 3,600, max block level 250, coinbase maturity 100, no difficulty reset, no treasury window on testnet | **Inferred** from reading both (Rust `consensus/core/src/config/params.rs:605-660`, Go `params.go:361-421`). Not a live parity check (Q47 asks for one) |
| DNS seeders | none on testnet, in Go and Rust | **Verified**: Rust `params.rs:606`, Go `params.go:367-369` |
| Merged-mining activation on testnet | `aux_pow_activation = never`; the only switch is `--devnet-aux-pow-activation=<DAA>`, which refuses any network except devnet | **Verified**: `params.rs:655`, `kaspad/src/args.rs:171-172,490-493` |
| Self-parent ban | from `activation - 2 x finality_depth`, i.e. 172,800 DAA (about 2 days) before activation on testnet; any well-formed `SDM1` commitment in a Sedra coinbase is rejected | **Verified**: `params.rs:340-347`, `consensus/src/pipeline/body_processor/body_validation_in_context.rs:107-109` |
| Release base | `m10-auxpow` does **not** contain the v0.1.0/v0.1.1 release commits on `main` (`git merge-base --is-ancestor origin/main origin/m10-auxpow` is false; 10 commits on `main` only, e.g. `2d3f878` "Release sedra-rusty 0.1.1") | **Verified** 2026-11-20 |
| Kaspa parent network | Kaspa testnet-10 is up: `kaspa-testnet-10`, kaspad `2.1.0`, synced, virtual DAA score 627,947,434, difficulty 2,315,278, hashrate 4.63e-05 TH/s (about 46 MH/s); tip block header version 2, coinbase transaction version 1, 61 parent levels | **Verified** 2026-11-20 via `https://api-tn10.kaspa.org/info/blockdag`, `/info/kaspad`, `/info/hashrate`, `/blocks/de91502b…f7aa?includeTransactions=true` |
| Pool | Miningcore branch `sedra-merged-mining` merge-mines Sedra next to a Kaspa parent (`additionalMergedMining`); payouts were disabled in the e2e runs | **Verified**: harness README, `config.e2e.json` |
| Miners | e2e CPU stratum miner (`contrib/e2e-merged-mining/miner`), the boot tool (`boot/`, mines N native blocks via gRPC); Go `sedraminer` v2.0.0 (`cmd/sedraminer`) | **Verified** (files exist); `sedraminer --testnet` against the Rust node **Unknown** (not run) |
| Wallet | Go `sedrawallet` v2.0.0 works against the Rust node (devnet, 2026-11-10) | **Verified**: harness README "Wallet test 2026-11-10" |

## 2. Gaps between the harness and a public testnet

| # | Gap | Why it matters | Size |
|---|---|---|---|
| G1 | No way to activate merged mining on testnet (devnet-only flag) | Without it nothing can be tested on `sedra-testnet-10` | small code |
| G2 | `m10-auxpow` lacks the v0.1.0/v0.1.1 release commits (reproducible-build fixes, version, docs) | SIP-0003 §4.5: the testnet node is a release built and verified like v0.1.0 | merge, docs |
| G3 | Parent hashing tested on 20 Kaspa **mainnet** blocks only | The parent is Kaspa **testnet-10** (kaspad 2.1.0). Format looks the same (header v2, coinbase v1) but that is Inferred until real TN10 blocks are run through the same test | small test |
| G4 | No seeders, harness nodes listen on loopback | Outsiders need reachable peers | infra + guide |
| G5 | Fresh chain from a 2021 genesis: a new node reports "not synced" and refuses templates until a recent block exists | Only the first node needs `--enable-unsynced-mining` for the first blocks (as the harness does) | runbook |
| G6 | No way to tell merged-mined from native blocks through RPC (`getBlock` carries no proof, by design) | Criterion 2 and the share-per-pool watch (SIP-0001 §8) need the count | small tool |
| G7 | No monitoring across nodes | Criteria 1, 3, 8 need "all upgraded nodes agree; old nodes stop at the first merged-mined block" with timestamps | small tool |
| G8 | No pool for testnet: Kaspa TN10 node, testnet Miningcore config, payouts never run | Criterion 5 (both coins paid) | config + Miningcore check, no code change planned |
| G9 | No faucet | People without miners need coins (SIP-0003 §4.4) | script |
| G10 | No guide, runbook, report template, issue template | SIP-0003 §4.5, §4.6 | docs |
| G11 | Ban-window test needs a block with an `SDM1` commitment in its own coinbase | Criterion 1 ("the ban starts 2 x finality_depth earlier") is only shown if a violating block is tried before and after the ban start | small tool option |
| G12 | Live Go/Rust parity on testnet-10 never run (Q47 condition) | SIP-0003 §4.2 chooses testnet-10 only if this passes | dry run |

Not gaps (the code already handles them): network isolation from mainnet and from Kaspa TN10 (different network
names `sedra-testnet-10` / `kaspa-testnet-10`, different ports, different address prefixes, the commitment binds the
Sedra testnet genesis hash; **Verified** in the code listed above), merged-mined blocks over P2P and in the pruning
proof (M10 step 5b).

## 3. Proposed design (smallest that closes the gaps)

### 3.1 Node release (G1, G2, G3)

- New sedra-rusty branch `testnet-kit` from `m10-auxpow`, with `main` (v0.1.1) merged in.
- **Activation:** the agreed score is written into `TESTNET_PARAMS.aux_pow_activation` in the testnet release, so
  every participant runs the same rule without a flag, exactly the way mainnet would get it. For dry runs and resets,
  the existing devnet flag is renamed `--aux-pow-activation-override=<DAA>` and allowed on devnet and testnet only
  (still refused on mainnet, with a loud warning on testnet). The guide never tells participants to use it.
- **TN10 parent vectors:** a test like `sedra_auxpow_parent_test` on about 20 consecutive real Kaspa TN10 blocks
  (headers from a TN10 node's `getBlock`, coinbases from api-tn10.kaspa.org).
- Version `0.2.0-testnet.N`, built reproducibly and signed like v0.1.x (`docs/RELEASE.md`). Cut only after the
  Sedra team agrees (Q51/Q52). *Update 2026-11-26:* cut after the team's yes of 2026-11-24 and published as
  [`sedra-v0.2.0-testnet.1`](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.2.0-testnet.1) (pre-release, 2026-11-25).

### 3.2 Chain and timing (G5, Q48)

- `sedra-testnet-10` from genesis, unless Q52 shows a live chain worth joining (then the activation score is set
  relative to that chain's DAA score at release time). *Update 2026-11-26:* fresh chain from genesis (RUNBOOK §3.1).
- Activation = launch DAA + 345,600 (about 4 days at 1 block/s). Ban start = activation - 172,800 (about day 2).
  So: days 0-2 native only, Go nodes join; day 2 ban starts; day 4 activation; first pruning point after activation
  about 2.15 days later (pruning depth 185,798), so criterion 4 can be tested from about day 7; earliest end day 18
  (two weeks after activation, Q51). **Inferred** from the parameters; real block rate depends on hashrate.
  *Update 2026-11-26:* chain start 2026-11-27 10:00 UTC: ban start about 11-29, activation about 12-01, criterion 4
  from about 12-03, earliest end about 12-15, report about 12-17 (OVERVIEW.md D4).

### 3.3 Infrastructure (G4, G8; Q49)

- Two Sedra seed nodes reachable from the internet on 22211, listed by host:port in the guide (`--addpeer`)
  (*2026-11-27, corrected the same day:* seed1 is `puddlepool.com:22211` and the pool `stratum+tcp://puddlepool.com:15555`; an earlier note here said seed1 would not be published and the pool address would follow later); one
  unmodified Go sedrad v2.0.0 `--testnet` node as the "old node" (criterion 3).
- One Kaspa TN10 node (upstream rusty-kaspa, the version TN10 runs) for the pool.
- One testnet Miningcore instance, separate database, separate host role from production, stratum on its own port,
  payouts on for both coins (Sedra via `sedrawallet --testnet`; Kaspa TN10 payout path to be checked in Miningcore,
  no code change planned; anything needed there is asked first).
- Where these run is Nec's decision (sedra-dev alone is one host, which SIP-0003 §6 warns about).

### 3.4 Tools in sedra-rusty `contrib/testnet/` (G6, G7, G9, G11)

- `testnet-monitor` (Rust, uses the repo's own gRPC client and `kaspa-pow`): polls a list of nodes every 60 s and
  writes CSV: DAA score, sink, sync state, peers per node; follows node 1's selected chain and asks every other node
  whether each sampled chain block (100 DAA deep) is a chain block there too (agreement, criterion 1/8); classifies
  every new block as native (its own kHeavyHash meets its target) or merged-mined (accepted although it does not),
  with the coinbase payload tag, so blocks per pool and per kind can be counted (criterion 2, SIP-0001 §8). A daily
  summary feeds the pass report.
- `testnet-miner` (the boot tool, generalized): native CPU miner over gRPC with `--extra-data`, so the ban test can
  submit a native block carrying a well-formed `SDM1` commitment before and after the ban start (G11).
- `faucet.sh`: sends a fixed amount with `sedrawallet send --testnet`; requests come in as GitHub issues.
- systemd unit templates for seed nodes (own data dir, `MemoryMax`), start scripts, the testnet Miningcore config.

### 3.5 Documents in sedra-project `testnet/` (G10)

`GUIDE.md` (participants), `RUNBOOK.md` (operator), `PASS-REPORT-TEMPLATE.md` (one section per SIP-0003 §3
criterion, each with its measurement and evidence slot), and an issue template for reports.

## 4. Decisions (Nec, 2026-11-20)

1. The design as proposed: hard-coded score in the testnet release plus the override flag, branch `testnet-kit` from
   `m10-auxpow` with v0.1.1 merged in. Merged from `dev` (which holds the v0.1.1 release content under the Git Flow
   rules of sedra-rusty; `main` differs from `dev` only in two documentation lines).
2. Where the infrastructure runs stays open in the runbook and is chosen at launch (*decided 2026-11-24*,
   [HOSTING.md](HOSTING.md)).
3. Private dry run on sedra-dev: yes, loopback only, own ports and data directory, `MemoryMax`, with a local Kaspa
   chain instead of a synced TN10 node.

## 5. What was built and what the dry run found

- sedra-rusty `testnet-kit`: `71c08bea` (merge of `dev`), `3c06131b` (override flag, TN10 vectors, tools), `582be8a5`
  (dry-run fixes, SEDRA.md). Full test suite on the tree of `3c06131b`: 112 suites, 561 passed, 0 failed, 25 ignored
  (**Verified** 2026-11-20).
- G3 closed: 20 real Kaspa TN10 blocks hash exactly as Kaspa reports (header v2, coinbase v1); a proof on a TN10
  parent binds to the Sedra testnet genesis (**Verified**, `sedra_kaspa_tn10_parent_hashing_test`).
- Dry run 2026-11-20 ([evidence](../research/archive/2026-11-20-0013-testnet-dryrun.md)): activation at the score,
  native and merged-mined blocks side by side, the upgraded nodes agreeing, the Go node falling off at the first
  merged-mined block, the self-parent ban, a fresh node, wallet and faucet: all as predicted. G12 partly: the Go node
  accepted 4,000 Rust-mined native testnet blocks.
- New gaps found and closed in the kit: the monitor cannot use gRPC with Go nodes (now `sedractl`); Miningcore needs
  `genesisHash` for the testnet; Miningcore refuses a `sedratest:` address when the parent is a Kaspa devnet; `--connect`
  disables inbound peers.
- Kaspa TN10 payouts: Go `kaspawallet` v0.12.23 works as Miningcore's wallet daemon on testnet-10 rules (**Verified**
  on a private chain 2026-11-20, [evidence](../research/archive/2026-11-20-0013-kas-tn10-payout-check.md)).
- Still open: a Kaspa TN10 node's disk and memory
  need (**Unknown**); pruning proof with merged-mined headers on a public chain; where the infrastructure runs.
  *Update 2026-11-26:* hosts decided 2026-11-24 ([HOSTING.md](HOSTING.md)); the TN10 node measured during its sync
  2026-11-25 (66 GB disk, RSS 5.5-6.4 GB, [REHEARSAL.md](REHEARSAL.md) 2.6). The pruning proof stays open (criterion 4).

## 6. Addition 2026-11-25: ZKas in the same coinbase (D11)

Nec decided that the testnet pool also merges ZKas under the same Kaspa testnet-10 parents, as the mainnet pool would
after activation. Reason: a Kaspa coinbase with both a ZKas and a Sedra commitment was never tested against real
nodes. The local end-to-end run of 2026-11-10 merged Sedra only, contrary to what SIP-0001 §9 said (corrected
2026-11-25). Design: a private ZKas test chain (zkas-rusty `zkas-v1.0.14-1`, `--testnet --netsuffix=10`, no outside
peers) used by the testnet pool only; ZKas aux entry in the testnet Miningcore config with the ZKas testnet genesis;
proposed criterion 9 in SIP-0003 and section 9 of the pass-report template. Nothing in the Sedra node changes.

## What this does NOT mean

- It does not launch a testnet. (*Corrected 2026-11-26:* this line said the launch waits for Q51 and Q52; the Sedra
  team agreed on 2026-11-24 and the start is 2026-12-01, OVERVIEW.md D4; the chain itself starts 2026-11-27.)
- It does not change SIP-0003's decisions (Q46-Q50); it implements them.
- Kaspa TN10 being up on 2026-11-20 does not mean it will stay up or keep its format during the test.
- Testnet coins have no value.
