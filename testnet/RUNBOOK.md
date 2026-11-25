# Sedra public testnet: operator runbook

| | |
|---|---|
| Status | Prepared 2026-11-20, **not launched**. Launch only after the Sedra team agrees on Q51 (duration, pass criteria) and Q52 (which chain); see section 1. *Update 2026-11-25:* the Sedra team agreed in writing on 2026-11-24 (Q51, SIP-0003 as it stands); the fresh chain means Q52 no longer holds up the launch. Proposed start 2026-12-01, not announced yet ([OVERVIEW.md](OVERVIEW.md) D4). |
| Operator | Nec |
| Process | [SIP-0003](../proposals/SIP-0003-public-testnet.md); design and gaps in [DESIGN.md](DESIGN.md); participant side in [GUIDE.md](GUIDE.md) |
| Kit | sedra-rusty branch `testnet-kit`, directory `contrib/testnet/` (tools, units, pool config, dry-run scripts) |
| Report | [PASS-REPORT-TEMPLATE.md](PASS-REPORT-TEMPLATE.md) |

Everything here is for the testnet only. No mainnet node, wallet or pool is touched; a production machine is
never a peer; the testnet pool never shares a host role, database or wallet with the production pool.

## 1. Go / no-go before launch

| Check | How | Must be |
|---|---|---|
| Q51 agreed | Sedra team's answer in QUESTIONS.md | Duration and criteria agreed (or changed by them) in writing |
| Q52 answered | Sedra team's answer | Decides 3.1: fresh chain from genesis, or join an existing testnet-10 chain |
| Live Go/Rust parity on testnet-10 (Q47 condition) | Dry run (section 9) or a launch rehearsal: Go sedrad v2.0.0 follows a Rust-mined testnet chain | Go node accepts every native block of the Rust node; recorded with hashes |
| Kaspa testnet-10 still up, format unchanged | `curl -s https://api-tn10.kaspa.org/info/kaspad`; one tip block's header version and coinbase version | Header v2, coinbase v1 (as on 2026-11-19, tested in `sedra_kaspa_tn10_parent_hashing_test`). A change means a parent-decoder release first (SIP-0001 §4.6) |
| Hosts ready | Section 2 | All listed services running and reachable |
| Announcement agreed | Sedra team asked to announce (Q48) | Their answer recorded; the announcement names the activation score |

If any check fails: no launch. Record why in #13.

## 2. Infrastructure

Where it runs: decided 2026-11-24 ([HOSTING.md](HOSTING.md)): seed2 on a rented netcup VPS in the EU, everything else at home. SIP-0003 §6: two seed nodes on one physical host are not
independent; a second location is better.

| Role | Software | Ports | Notes |
|---|---|---|---|
| seed1 | testnet release, `systemd/sedra-testnet-node.service` | P2P 22211 open to the internet, gRPC 22210 localhost | `--externalip` set; `MemoryMax=6G` |
| seed2 | same, second host or location | same | |
| old-go | unmodified Go sedrad v2.0.0, `systemd/sedrad-go-testnet.service` | P2P 22231, RPC 22230 localhost | never upgraded during the test |
| Kaspa TN10 node | upstream rusty-kaspa, the version Kaspa runs on testnet-10 (2.1.0 on 2026-11-19), `--testnet --netsuffix=10 --utxoindex` | its defaults (16210/16211) | disk and memory need **Unknown**: measure during sync before launch |
| testnet pool | Miningcore branch `sedra-merged-mining`, `pool/miningcore-testnet.json` | stratum 15555 public, API localhost | own Postgres database; `genesisHash` set for both aux chains (see 2.1) |
| private ZKas test node (D11, since 2026-11-25) | zkasd built from zkas-rusty `zkas-v1.0.14-1-g312c6fb7`, `--testnet --netsuffix=10`, no DNS seeding, no outside peers | gRPC localhost/LAN only | a ZKas test chain for the pool only; never connected to a public ZKas network |
| wallets | Go sedrawallet v2.0.0 `--testnet` (pool and faucet, separate keys files), Kaspa TN10 wallet for the pool | localhost only | testnet keys only; never a key that exists on mainnet |
| monitor | `sedra-testnet-monitor`, `systemd/sedra-testnet-monitor.service` | none | reaches seed2 through an SSH tunnel, old-go through `sedractl://`; with `--zkas zkas=grpc://192.168.0.28:16820` (D11) also the private ZKas node: `zkas.csv`, `zkas_blocks.csv`, `shared_parents.csv` |
| status page | `status_page.py`, `systemd/sedra-testnet-status.{service,timer}` (every minute) | HTTPS 443 (and 80 for the redirect and the certificate) on the web host | on the monitor host; reads the monitor's CSVs, writes `/var/www/sedra-testnet` and uploads it with `--publish` over the one SSH link to the VPS, where Caddy (`web/Caddyfile`) serves https://testnet.puddlepool.com; needs no node access. Set the seed and pool addresses in the unit at launch |

### 2.1 Pool settings that matter

- **ZKas aux entry (D11, 2026-11-25).** ZKas is merged next to Sedra under the same Kaspa testnet-10 parent:
  - `genesisHash` of the ZKas entry = `d5d97eecaa0bad6a4a05627bcb4d99aa22f1632458e18a7b2b30e2fd5b4c2f9b` (ZKas testnet genesis, zkas-rusty
    `consensus/core/src/config/genesis.rs`). Miningcore's default is the ZKas **mainnet** genesis
    (`KaspaAuxChain.cs:24-26`), the same trap as for Sedra.
  - On ZKas testnet, merged mining and the `ZKM1` rule are active from genesis (zkas-rusty `params.rs:1194-1195`).
    ZKas checks the parent's work against its own target and binds the commitment to its own genesis; the parent's
    network is not checked (**Inferred** from the code, shown at the rehearsal).
  - Pool and miner ZKas addresses are `zkastest:` (Miningcore checks them against the parent's network).
    **Known gap:** a ZKas address in the password (`a=zkastest:…`) is silently ignored; Miningcore only recognises
    `zkas:` there (`KaspaUtils.cs:272-307`). Use the username form `kaspatest:…+zkastest:…` (GUIDE §7). A fix is a
    Miningcore change and is asked first.
  - **Coinbase space:** Kaspa allows 204 bytes of payload. After the fixed part, the payout script and the node's
    `2.1.0/`, Miningcore adds `2.1.0.` before the pool tag; `ZKM1` takes 68 and `SDM1` 47 bytes. That leaves about
    **24 bytes** for the pool's own `extraData` (**Inferred** from verified constants; SIP-0001 §6 correction of
    2026-11-25). Keep the tag short.
  - **The pool's ZKas address must be shielded** (Orchard, `zkastest:p…`). ZKas testnet rejects a coinbase that pays
    a transparent address: with a Kaspa-style `zkastest:q…` address every merged block failed with "coinbase payout
    address is not a canonical Orchard address (required on a shielded network)" (zkas node log, 2026-11-25 12:15 UTC;
    rule in zkas-rusty `consensus/src/pipeline/body_processor/body_validation_in_context.rs`). **Verified**.
  - Getting a shielded address on a chain at genesis: zkas-walletd's `/api/wallet/create` refuses while the node's
    DAA score is 0 ("not connected to a node yet"), so the pool wallet is made with `/api/wallet/import` and a fresh
    random 32-byte seed, `birthday` 0. zkas-walletd runs on the pool host, `--network testnet --listen 127.0.0.1:8501`,
    its token and at-rest secret in the pool's secrets file; `walletPassword` of the ZKas entry is that token.
  - ZKas payouts (zkas-walletd, REST) on the test chain: **Unknown** whether they work; tried if cheap, otherwise
    "not shown" in the report (criterion 9).
- **No mainnet cross-checks.** Miningcore cross-checks block rewards against `api.kaspa.org` (KAS) and
  `api.sedracoin.com` (SDR) by default, both mainnet. Set `extra.rewardCrossCheckUrl` to `"off"` on the parent pool.
  The synthesized Sedra aux pool does not inherit that setting (`Program.cs` `ValidateConfig` @ `1a72553a`), so the
  config writes the Sedra aux pool out as its own entry (`id` `<parent>-sedra`, `enableInternalStratum` false,
  `rewardCrossCheckUrl` `"off"`). Fixing the inheritance is a Miningcore change and is asked first.

- `genesisHash` of the Sedra entry = `f896a3034873be1739fc4359236899fd3d65d2bc94f9780df0d0da3eb1cc4370` (testnet
  genesis, confirmed by the dry-run node 2026-11-20). Miningcore's default is the mainnet genesis; without the
  setting every merged-mined Sedra block fails the commitment check.
- Parent and aux addresses must be of the same network type: Miningcore checks the `a=` address against the parent's
  network. Kaspa TN10 + `sedratest:` match; a Kaspa devnet parent with `sedratest:` addresses is refused (dry run).
- Sedra wallet: `protobufWalletRpcServiceName` = `sedrawalletd.sedrawalletd`, its own port (8182), so it does not
  collide with a Kaspa wallet daemon on 8082.
- **Kaspa TN10 payouts** (criterion 5). **Checked 2026-11-20 on a private chain:** Go `kaspawallet` v0.12.23 as the
  daemon, kaspad 2.1.0 with testnet-10 (Crescendo) rules, `GetBalance` and `Send` called exactly as Miningcore calls
  them: two payouts accepted and mined, balances exact
  ([evidence](../research/archive/2026-11-20-0013-kas-tn10-payout-check.md)). Use v0.12.23 with `--testnet` on the
  pool's Kaspa host. Still to show on the public testnet: Miningcore itself paying. Background:
  - Miningcore pays KAS only through the gRPC service `kaspawalletd.kaspawalletd` (`GetBalance`, then `Send`;
    `KaspaPayoutHandler`, Miningcore `57944adc`). **Verified** in the code.
  - The candidate daemon is Go `kaspawallet start-daemon` from kaspanet/kaspad (Go node deprecated; the wallet is
    still released). Its release notes: v0.12.19 adapted the wallet gRPC interface to the Rust node's fee-estimation
    and RBF APIs; v0.12.21 "Crescendo compatibility" (payload hash, coinbase maturity); v0.12.23 "Toccata Prep"
    (updated proto) and a higher minimum fee rate. None mentions testnet-10. **Verified**:
    https://github.com/kaspanet/kaspad/releases, read 2026-11-20.
  - TN10 runs the same kaspad 2.1.0 as the Kaspa mainnet node our test vectors came from, with header v2 and
    coinbase v1 on both, so a wallet version that pays on mainnet should pay on TN10 with `--testnet`
    (**Inferred**, not run). Which `kaspawallet` version the production Kaspa host runs is not recorded in the
    repositories (**Unknown**).
  - Done for the private chain (above); the public run comes with the testnet.
  - Any Miningcore change for it is asked first (the miningcore repository is not changed by this kit).

## 3. Launch

### 3.1 Chain and activation score

- **Fresh chain** (if Q52 shows nobody runs testnet-10): launch DAA score = 0. Activation = **345,600** (about 4 days
  at one block per second after the first difficulty window), ban start = activation - 2 x 86,400 = **172,800**.
  The first 2,641 blocks are mined at genesis difficulty and come within minutes; the clock starts after that.
- **Existing chain:** activation = current virtual DAA score + 345,600 at release time.

### 3.2 Release

Prepared 2026-11-24 for the fresh chain (steps 1 and the test part of 2 done on sedra-rusty `release-0.2.0-testnet.1`;
*update 2026-11-25:* tagged, signed and published as a
[pre-release](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.2.0-testnet.1)): [release/v0.2.0-testnet.1-checklist.md](../release/v0.2.0-testnet.1-checklist.md), day-of steps in
[release/v0.2.0-testnet.1-go.md](../release/v0.2.0-testnet.1-go.md).

1. On `testnet-kit`: set `TESTNET_PARAMS.aux_pow_activation = ForkActivation::new(<score>)` with a `SEDRA:` comment,
   add the boundary test (score - 1 rejects a merged-mined block, score accepts; ban start - 1 accepts an `SDM1`
   coinbase, ban start rejects), set `sedra_release()` to `0.2.0-testnet.1`.
2. Full test suite, then build and verify reproducibly as in `docs/RELEASE.md`; signed tag `sedra-v0.2.0-testnet.1`
   on `testnet-kit` (never on `main`, which holds mainnet releases).
3. Publish binaries, `SHA256SUMS`, signature; fill the `<at launch>` values in GUIDE.md.

### 3.3 Start

1. seed1 with `--enable-unsynced-mining` (a fresh chain's genesis is from 2021, so the node reports "not synced"
   until it has a recent block). Mine the first blocks to the faucet wallet:
   `sedra-testnet-miner --rpc grpc://127.0.0.1:22210 --address <faucet address> --threads 2`.
   Restart seed1 **without** `--enable-unsynced-mining` once the tip is recent.
2. seed2 with `--addpeer=<seed1>` (not `--connect`: a node started with `--connect` accepts no inbound peers).
3. old-go, Kaspa TN10 node, pool, monitor. Check the monitor's first rows.
4. Announce: issue in #13 with the GUIDE link, the release, seed addresses, activation and ban-start scores; the Sedra
   team's channels if they agreed (Q48).

## 4. During the test

### 4.1 Daily

```
python3 contrib/testnet/summary.py /var/lib/sedra-testnet-monitor --activation <score> > summary-$(date -u +%F).md
journalctl -u sedra-testnet-monitor --since yesterday | grep ALERT
```

Post the day's numbers as a comment on #13 (blocks native and merged, share per tag, node availability, agreement,
alerts and what they were). Answer reports. Bad news is posted like good news.

### 4.2 Alerts and what they mean

| Alert | Meaning | Action |
|---|---|---|
| `node X unreachable` | process down or tunnel down | restart; note the gap in the report |
| `node X reports not synced` | lagging or isolated | check peers; a seed should never stay unsynced |
| `does not have reference chain block` for an **upgraded** node | split among upgraded nodes | stop and investigate: criterion 1 or 8 fails until explained |
| same for **old-go** before the first merged-mined block | old node split early | investigate (criterion 3: should follow until then) |
| same for **old-go** after the first merged-mined block | expected | record the first miss (criterion 3) |
| `reference chain reorg` | a chain block left the selected chain | normal for shallow reorgs; investigate if deep |

## 5. Criterion by criterion (how each is measured)

| SIP-0003 §3 | Measurement | Evidence for the report |
|---|---|---|
| 1. Activation without a split; ban starts 2 x finality_depth earlier | `agreement.csv`: upgraded nodes never miss a reference chain block around the activation score. **Ban test:** shortly before the ban start, one native block with `sedra-testnet-miner --sdm1 --blocks 1` (must be accepted); shortly after, the same (must be rejected with `CoinbaseCarriesMergeMiningCommitment`). `summary.py` lists accepted SDM1 blocks: none at or after the ban start | miner output with DAA scores; node log lines; summary table |
| 2. Merged-mined and native blocks side by side | `blocks.csv` kinds after activation; every upgraded node agrees | summary "Blocks" and "Share per tag" |
| 3. Old nodes follow before activation, stop after | old-go rows in `agreement.csv` and `nodes.csv`: present before the first merged-mined block, missing from it on | first miss (DAA, time) vs first merged block |
| 4. Fresh node syncs after activation, including the pruning proof with merged-mined headers | after the first pruning point above the activation score (pruning depth 185,798 DAA after activation, about 2.15 days), start a node with an empty data dir and `--addpeer` to a seed; it must sync and agree | sync log (pruning proof accepted), its sink agreeing with seed1 |
| 5. Pool pays both coins; per-miner addresses work | pool payouts to two test miners with different `a=` addresses | transaction IDs on both chains, Miningcore payments table |
| 6. Go sedrawallet sends and receives | GUIDE section 5 on the public testnet | transaction IDs, balances before and after |
| 7. At least one outside participant | issues with the "Testnet report" template | issue links |
| 8. Two weeks after activation without a consensus failure; every problem fixed and re-tested | daily summaries; no upgraded-node miss; every issue closed with a fix and a re-test | 14+ daily summaries, issue list |

The self-parent-ban test deliberately puts one `SDM1` block before the ban start. Old Go nodes accept such a block at
any time, so a violating block **after** the ban start would split old nodes early and blur criterion 3. Only the
upgraded nodes see the rejected one (it is refused at submission, never relayed). Predicted, **Inferred**.

## 6. Problems

- **Bug in the node, before activation:** fix, new testnet release, a later activation score if needed, announce.
- **Bug in a consensus rule after activation:** the fix is itself a rule change on the testnet: new release with its
  own activation of the fix, or a reset (6.1). Either way the two-week clock restarts (SIP-0003 §4.6).
- **Kaspa TN10 changes its header or coinbase format:** merged mining stops, native mining continues (SIP-0001 §4.6).
  Release a parent-decoder update; record it as evidence for Q20.
- **Security problem:** private handling per sedra-rusty `SECURITY.md`; publish after the fix.

### 6.1 Reset

A reset is a decision for Nec (and the Sedra team, if they take part), announced in advance. Options:

1. **Same chain, later activation** (only if activation has not been reached): new release, new score.
2. **New chain with a new genesis** (a testnet genesis with a new payload, own network name): clean, but Go nodes
   cannot follow without a modified build, so criterion 3 can no longer be shown with unmodified software.
3. **Wipe and restart from the same genesis:** only if every known node wipes too; a node that keeps the old, heavier
   chain would pull new nodes onto it. Not recommended.

## 7. Ending

1. After at least 14 days after activation with criteria 1-8 checked, fill PASS-REPORT-TEMPLATE.md into
   `research/NNNN-public-testnet-report.md`, with the raw summaries in `research/archive/`.
2. Publish it on #13 and send it to the Sedra team. A mainnet activation date is chosen only with them, after the
   report (SIP-0001 §5).
3. Announce the end date; keep the seeds running at least one more week for late reports; then stop the services.
   The monitor data stays archived.

## 8. Dry runs

`contrib/testnet/dryrun/start.sh` runs the whole kit on one test host, loopback only, own ports and data directory,
`MemoryMax` per process, with `--aux-pow-activation-override` for a short timeline. Results of the first dry run
(2026-11-20, sedra-dev) are in `research/archive/2026-11-20-0013-testnet-dryrun.md`.

## What this does NOT mean

- It does not launch the testnet or set a date.
- The pass criteria are SIP-0003's proposal; the Sedra team may change them (Q51) and their version wins.
- A passed testnet does not schedule mainnet activation.
- Values marked Inferred (timings, predicted old-node behaviour) are predictions to be checked, not results.
