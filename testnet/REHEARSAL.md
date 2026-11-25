# Testnet rehearsal (planned 2026-11-30)

| | |
|---|---|
| Status | Planned. seed2 installed and running 2026-11-25; the home VMs do not exist yet |
| Release | `sedra-v0.2.0-testnet.1`, signed by Nec 2026-11-25, **not pushed** until the rehearsal passed ([go runbook](../release/v0.2.0-testnet.1-go.md)) |
| Goal | Start the whole testnet once on the real hosts with the signed binary, check every part, then stop and wipe it. Nothing is announced |
| Overview | [OVERVIEW.md](OVERVIEW.md) step 3; operator details [RUNBOOK.md](RUNBOOK.md) §2-§3; hosts [HOSTING.md](HOSTING.md) |

Labels: **Verified** (checked, with evidence), **Inferred**, **Unknown**.

## 1. Hosts (decided by Nec 2026-11-25)

| Role | Host | State |
|---|---|---|
| seed2 (no mining) | netcup VPS (HOSTING.md) | **Installed 2026-11-25** (see 2.1) |
| seed1 (mines the first blocks), old Go node, testnet pool with its database and wallets, monitor, status page, faucet | a **new home VM** that Nec creates | not created |
| Kaspa testnet-10 node (for the pool) | a **separate new home VM on SSD** that Nec creates | not created; must be synced before 11-30 |
| Router | TCP 22211 forwarded to seed1 (Nec) | not done |

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

1. Create the home VM for seed1 and the rest: Ubuntu 24.04 or 26.04, about 4 cores, 8 GB RAM, 100 GB on SSD; add
   the AI's SSH key as for the other VMs.
2. Create the Kaspa testnet-10 VM on SSD: Kaspa's guide asks for about 8 cores, 16 GB RAM, 640 GB SSD (HOSTING.md
   1.2; the real need on testnet-10 is **Unknown** and measured during the sync).
3. Forward TCP 22211 on the router to the seed1 VM.
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
| R10 | Stop everything, wipe every testnet data directory (seed1, seed2, old-go, pool database, monitor, status state) | clean state for 12-01; the wallets' keys are kept |

The rehearsal does not reach the ban start or the activation (that takes days); those were shown in the private dry
run of 2026-11-20 with a short override and are part of the public test itself.

**If the rehearsal fails:** the tag is not pushed, the fault is fixed, and a new release (`0.2.0-testnet.2`) goes
through the release steps again; the launch moves. **If it passes:** on Nec's go, push the tag and publish the
pre-release (go runbook steps 4-5), fill the GUIDE's seed and pool values, send the post text to the owner.

## What this does NOT mean

- The rehearsal is not the launch, and nothing from it is announced.
- A passed rehearsal shows the hosts and the setup work; it is not a pass of any SIP-0003 criterion.
- seed2 running now does not mean the testnet runs: it is a single node at genesis until the rehearsal.
