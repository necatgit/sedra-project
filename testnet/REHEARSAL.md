# Testnet rehearsal (planned 2026-11-30)

| | |
|---|---|
| Status | Planned. seed2 (VPS), seed1 + old-go + monitor + status page (home VM 204) installed and running 2026-11-25, at genesis, nothing mining; public status page live; Kaspa testnet-10 node syncing on VM 206 |
| Release | `sedra-v0.2.0-testnet.1`, signed by Nec 2026-11-25, **not pushed** until the rehearsal passed ([go runbook](../release/v0.2.0-testnet.1-go.md)) |
| Goal | Start the whole testnet once on the real hosts with the signed binary, check every part, then stop and wipe it. Nothing is announced |
| Overview | [OVERVIEW.md](OVERVIEW.md) step 3; operator details [RUNBOOK.md](RUNBOOK.md) §2-§3; hosts [HOSTING.md](HOSTING.md) |

Labels: **Verified** (checked, with evidence), **Inferred**, **Unknown**.

## 1. Hosts (decided by Nec 2026-11-25; home part moved to VM 204 the same day)

| Role | Host | State |
|---|---|---|
| seed2 (no mining) | netcup VPS (HOSTING.md) | **Installed 2026-11-25** (see 2.1) |
| seed1 (mines the first blocks), old Go node, testnet pool with its database and wallets, monitor, status page, faucet | **VM 204** (`sedra-rusty`, next to the public mainnet node and its Go reference node): own user `sedratn`, own directory `/data/testnet`, own ports, every testnet service niced with `MemoryMax`. If the mainnet node or its RPC ever lags, the testnet part moves to its own VM | seed1 and old-go running (2.4) |
| Kaspa testnet-10 node (for the pool) | **VM 206 `kaspa-tn10`** (Ubuntu 26.04, 6 cores, 12 GB, 150 GB on `nvme-dev` with discard, CPU type host) | created by Nec 2026-11-25; node installed 10:04 UTC, **synced 12:10 UTC** (2.6) |
| Private ZKas test node (D11) | VM 206, next to the Kaspa node | running since 2026-11-25 11:24 UTC; first merged-mined blocks 12:19 UTC (2.7, 2.8) |
| Router | TCP 22211 forwarded to seed1 on VM 204 (Nec) | done 2026-11-25; reachable from the internet (tested from the VPS) |

Not used for any of it: the public mainnet Rust node VM and the production pool's VMs.

## 2. Before 11-30

### 2.1 seed2 (done 2026-11-25)

- The release archive copied to the VPS, `sha256sum -c SHA256SUMS`: archive and `kaspad` OK. Installed as
  `/opt/sedra-testnet/kaspad` (`c0e0d23d…`), `kaspad --version` = `0.2.0-testnet.1 (rusty-kaspa v1.0.1, commit
  24511407f157)`. **Verified** 2026-11-25.
- systemd unit from the kit (`sedra-testnet-node.service`): user `sedra`, data in `/var/lib/sedra-testnet`,
  `MemoryMax=6G`, `--externalip` set, no `--addpeer` yet (seed1 dials seed2), no mining. Active since 2026-11-25
  08:29 UTC; P2P on 0.0.0.0:22211, gRPC on 127.0.0.1:22210 only. **Verified** (`ss -ltnp`).
- From outside (this project's PC): TCP 22211 reachable, 22210 not. **Verified** 2026-11-25.
- Until seed1 exists the node sits at genesis with no peers. That is expected.

### 2.2 Nec

1. ~~Create the home VM for seed1 and the rest~~: VM 204 is used instead (decided 2026-11-25).
2. ~~Create the Kaspa testnet-10 VM on SSD~~: done 2026-11-25 (VM 206). Sized at 150 GB rather than Kaspa's
   general 640 GB: the production Kaspa mainnet node uses 36 GB inside its VM (measured 2026-11-23), so 150 GB is
   **Inferred** to be enough for testnet-10; measured during the sync.
3. ~~Forward TCP 22211 on the router to VM 204 (seed1)~~: done 2026-11-25.
4. Tell the AI when the VMs are up.

### 2.3 AI, once the VMs are up (each host-changing step reported)

1. Kaspa VM first (the sync takes longest): upstream rusty-kaspa, the version testnet-10 runs (2.1.0 on 2026-11-25,
   `api-tn10.kaspa.org/info/kaspad`), `--testnet --netsuffix=10 --utxoindex`; record disk and memory during the
   sync.
2. Home VM: the signed release as seed1 (`--addpeer=<seed2>:22211`, `--externalip`), unchanged Go sedrad v2.0.0 as
   old-go, testnet tools built from the tag (`contrib/testnet/build_tools.sh`), Miningcore branch
   `sedra-merged-mining` with its own Postgres and `pool/miningcore-testnet.json` (testnet `genesisHash`), wallets
   (Go sedrawallet `--testnet`, Go kaspawallet v0.12.23 `--testnet`) with new testnet-only keys, the monitor with an
   SSH tunnel to seed2's RPC, the status page and its timer.
3. Nothing mines and nothing is announced before the rehearsal.

### 2.4 seed1 and old-go on VM 204 (done 2026-11-25)

- seed1: the verified release `kaspad` (`sha256sum -c` OK, `0.2.0-testnet.1 … 24511407f157`) as
  `sedra-testnet-seed1.service`: P2P 0.0.0.0:22211, gRPC 127.0.0.1:22210, `--externalip` from the home DynDNS name (as
  the mainnet node does), `--addpeer` seed2, `Nice=10`, idle IO class, `MemoryMax=4G`. Connected to seed2 at once.
  **Verified** (log: "P2P Connected to outgoing peer … :22211").
- old-go: unchanged Go `sedrad` v2.0.0 `--testnet` as `sedra-testnet-oldgo.service`, P2P and RPC on localhost
  (22231/22230), dialling seed1, `MemoryMax=3G`. Go sedrad needs a writable home directory for its default config;
  the service user got `/data/testnet/home`. Connected to seed1; `GetBlockDagInfo`: `sedra-testnet-10`, block count 1,
  DAA 0. **Verified**.
- The mainnet node and the Go reference node on the same VM stayed active.

### 2.5 Link, monitor and status page (done 2026-11-25)

- VPS: Nec created user `testnetlink` whose only key (from VM 204) is limited to `restrict`, a port forward to
  seed2's localhost gRPC (`permitopen="127.0.0.1:22210"`) and a write-only upload into `/var/www/sedra-testnet`
  (`rrsync -wo`). Tested from VM 204: forward works, upload works, a shell command and a read are refused.
  **Verified**.
- VM 204: `sedra-testnet-link.service`, ONE long-lived SSH connection to that user (forward 127.0.0.1:22220 → seed2's
  22210, ControlMaster socket for the uploads), reconnecting at most once a minute (the home router blocked port 22
  to the VPS after many connections on 2026-11-24).
- Testnet tools built on VM 204 from `testnet-kit` `0b4cadf1`; `sedra-testnet-monitor.service` polls seed1 (reference),
  seed2 (through the link) and old-go (`sedractl`) every 60 s. First rows: all three reachable, DAA 0, same sink =
  the testnet genesis `f896a303…`; "not synced" alerts are expected at genesis. **Verified**. (The Rust nodes report
  the network as `testnet-10`, the Go node as `sedra-testnet-10`: a naming difference between the two RPCs only.)
- `sedra-testnet-status.timer` writes the status page to `/data/testnet/www` every minute.
- Public page (2026-11-25, Nec's go): DNS `testnet.puddlepool.com` A/AAAA → the VPS (Nec); on the VPS nftables also
  allows 80/443 and Caddy 2.6.2 (Debian package) serves `/var/www/sedra-testnet` with `contrib/testnet/web/Caddyfile`
  (Let's Encrypt certificate, HSTS, CSP, no client IPs in the log). HTTPS checked from outside over IPv4 and IPv6.
  **Verified**. Since 2026-11-25 10:37 UTC VM 204 runs the restyled page (`testnet-status-ui` `71ff3e3a`; its 10
  tests pass there, Python 3.14) and uploads it every minute over the link (`--publish testnetlink@62.83.121.25:/`,
  no push while the link is down). First push checked from outside: HTTP 200, `status.json` served. **Verified**.
  Seed, pool and release links stay off the page until launch.

### 2.6 Kaspa testnet-10 node on VM 206 (started 2026-11-25)

- Hardened like the other VMs: SSH keys only (Nec's and the AI's), no root login, unattended security updates;
  nftables: SSH from the LAN, Kaspa P2P 16211 open, gRPC 16210 only from VM 204 (the future testnet pool).
- Node: upstream rusty-kaspa **v2.1.0**, built from source at the release tag (commit `01b532e8`, "Bump version to
  v2.1.0"), binary sha256 `5c6208b6…`; `kaspad 2.1.0`. Correction to the 11-20 records: the node used then,
  `4863866f`, is upstream `master` 12 commits after the v2.1.0 tag (`git describe`: `v2.1.0-12-g4863866f`), which also
  reports itself as 2.1.0. The release tag is used here.
- Service `kaspa-tn10`: `--testnet --netsuffix=10 --utxoindex --ram-scale=0.6`, data in `/var/lib/kaspa-tn10`,
  `MemoryMax=10G`. Started 10:04 UTC, found testnet-10 peers through Kaspa's DNS seeders, validated the pruning-point
  proof; block IBD ran about 11:48-12:10 UTC ("IBD with peer 157.90.7.39:16211 completed successfully" at 12:10 UTC, then
  blocks via relay). Measured every two minutes during the sync: disk 40% to 48% of 146 GB (66 GB used at the end),
  kaspad RSS 5.5-6.4 GB, never near the 10 GB cap. **Verified** 2026-11-25.

### 2.7 Private ZKas test node on VM 206 (D11, 2026-11-25)

- zkasd built from source: zkas-rusty `zkas-v1.0.14-1-g312c6fb7` (the local copy next to PuddlePool's Miningcore;
  the production ZKas node runs v1.0.14), `kaspad 2.0.1 (zkas-v1.0.14)`, sha256 `f9f23b5f…`. Service `zkas-testnet`:
  `--testnet --netsuffix=10` (ZKas testnet rules: merged mining and `ZKM1` from genesis), `--nodnsseed --outpeers=0`,
  P2P on 127.0.0.1:16821, gRPC 16820 reachable from VM 204 only (nftables), `MemoryMax=3G`. It never joins a public
  ZKas network. Reachable from VM 204 over gRPC. **Verified** 2026-11-25.
- First ZKas blocks come from the testnet pool's merged shares once the Kaspa testnet-10 node is synced; there is no
  native ZKas miner in the kit.
- The status-page monitor reads it since 2026-11-25 11:28 UTC (corrected the same day: this line first said 12:32 UTC,
  a local-time slip; `testnet-status-ui` `f9243875`, after a fix: the first
  version's RPC client rejected the network name `zkas-testnet-10`). Checked from VM 204: ZKas `ok`, DAA 0, sink =
  the ZKas testnet genesis `d5d97eec…`; the public `status.json` shows the ZKas node. **Verified**.
- Pool config with the ZKas aux entry and both units: sedra-rusty `testnet-kit` `45ab33b1`.

### 2.8 Testnet pool on VM 204 (2026-11-25)

- Miningcore branch `sedra-merged-mining` `1a72553a`, built on VM 204 (.NET 10, `-p:DisableGitVersionTask=true` because
  the source copy has no `.git`); service `sedra-testnet-pool` as `sedratn`, `Nice=10`, `MemoryMax=2G`, API on
  127.0.0.1:4100, stratum 15555 (LAN only: no router forward until launch). Own Postgres role and database
  `miningcore_testnet`. The filled config and all wallet secrets are in `/data/testnet/pool/secrets/` (mode 700,
  `sedratn`), not in any repository.
- Wallet daemons, all `127.0.0.1`, new testnet-only keys: Go kaspawallet v0.12.23 `--testnet` against the Kaspa node
  on VM 206 (8082), Go sedrawallet `--testnet` against seed1 (8182), zkas-walletd `--network testnet` against the ZKas
  node (8501, sha256 `116e056e…`). The Go wallets take their password on the command line, so it is visible in the
  process list of VM 204 (test keys only).
- Two config fixes found while starting it (RUNBOOK 2.1): the pool's ZKas address must be a shielded one, and the
  default reward cross-checks against the mainnet explorers are switched off. Template and units with both fixes:
  sedra-rusty `testnet-kit` `9273fc7e`.
- First run, 12:19 UTC: one single-thread CPU stratum miner (the e2e miner from `contrib/e2e-merged-mining`,
  1.76 MH/s) for 120 s with `kaspatest:…+zkastest:p….rig1` and `a=sedratest:…`. Result: 1,804 shares accepted, 0
  rejected; **82 Kaspa testnet-10 blocks** found by the pool (database `blocks`, status confirmed); **741 ZKas blocks
  accepted, 0 rejected** (pool log; ZKas node: no validation failure in that window). Every Sedra submission was
  refused with "node is not synced [IsInIbd]": the Sedra testnet is still at genesis and merged mining is not
  active before DAA 345,600, as planned. **Verified**.
- The status page classifies the ZKas blocks as merged (`status.json`: `zkas.blocks_all_time.merged` 677 at its
  12:19 UTC refresh, no native ones, as expected without a native ZKas miner). `shared_parents` stays 0 until Sedra
  merged blocks exist. Consistent with the pool's log; **the native direction is untested** (corrected the same day:
  this line first said "Verified"). A merged block fails its own PoW check whatever the classifier does, so "all
  merged" would come out the same even if the native check were wrong; what could go wrong, a native ZKas block
  counted as merged, needs a native ZKas block, and there is none. `zkas.synced` is false at DAA 740: ZKas blocks
  only come with pool shares, so its newest block is not recent.
- First payout cycle, 12:20 UTC: the pool paid **64 KAS** (testnet-10) to the miner's address through the Go
  kaspawallet daemon, capped by the matured part of its balance (log "Payout Settlement Completed", `payments` table:
  1 row, 64). **Verified** for Kaspa; Sedra and ZKas payouts are not shown yet. The ZKas blocks stay pending: the
  pool pauses ZKas block classification while the ZKas node reports "not synced", which it does while nobody
  mines that chain.
- Not checked yet: the byte layout of one parent coinbase (exactly one `ZKM1` and one `SDM1`, payload ≤ 204 bytes).
  Kaspa testnet-10 accepted the 82 blocks, which it would not with a payload over its limit (**Inferred**); the
  tag count is read from a block at the rehearsal (R11). These blocks and the ZKas test chain are wiped in R10.

## 3. The rehearsal (11-30)

| # | Step | Pass when |
|---|---|---|
| R1 | RUNBOOK §1 checks: Kaspa testnet-10 up, header v2 and coinbase v1; the Kaspa VM synced | all true |
| R2 | seed1 with `--enable-unsynced-mining`, CPU miner to the faucet wallet | the first 2,641 blocks within minutes, then about 1 block/s |
| R3 | seed2 sees seed1 and follows | seed2's DAA score close to seed1's; the monitor shows both agreeing |
| R4 | old-go joins | it follows the Rust chain (native blocks only at this point) |
| R5 | A participant node from outside (the AI's WSL, `--addpeer` both seeds) syncs | reaches the same sink; both seeds reachable on 22211 |
| R6 | Wallet: faucet sends to a second wallet | the transaction confirms |
| R7 | Pool: stratum reachable, a CPU stratum miner connects with `kaspatest:` + `a=sedratest:` | shares accepted on Kaspa testnet-10 (Sedra blocks only after activation, which is not reached in the rehearsal) |
| R8 | Status page and monitor | the page shows both seeds, old-go, the phase and recent blocks; data under five minutes old |
| R9 | Restart seed1 without `--enable-unsynced-mining` | it stays synced and keeps mining through the miner |
| R11 | ZKas (D11): the pool merges the private ZKas test chain next to Sedra | a Kaspa testnet-10 coinbase with exactly one `ZKM1` and one `SDM1`; ZKas blocks accepted from the pool's shares; payload within 204 bytes; no rejected block on either chain because of the other's tag |
| R10 | Stop everything, wipe every testnet data directory (seed1, seed2, old-go, pool database, monitor, status state, the ZKas test chain) | clean state for 12-01; the wallets' keys are kept |

The rehearsal does not reach the ban start or the activation (that takes days); those were shown in the private dry
run of 2026-11-20 with a short override and are part of the public test itself.

**If the rehearsal fails:** the tag is not pushed, the fault is fixed, and a new release (`0.2.0-testnet.2`) goes
through the release steps again; the launch moves. **If it passes:** on Nec's go, push the tag and publish the
pre-release (go runbook steps 4-5), fill the GUIDE's seed and pool values, send the post text to the owner.

## What this does NOT mean

- The rehearsal is not the launch, and nothing from it is announced.
- A passed rehearsal shows the hosts and the setup work; it is not a pass of any SIP-0003 criterion.
- seed2 running now does not mean the testnet runs: it is a single node at genesis until the rehearsal.
