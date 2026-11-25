# Sedra public testnet: overview for everyone involved

| | |
|---|---|
| Status | **Not launched** (2026-11-24). Node release `0.2.0-testnet.1` published as a [pre-release](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.2.0-testnet.1) 2026-11-25, after a rehearsal on the real hosts the same day ([REHEARSAL.md](REHEARSAL.md)). Waiting for the Sedra team's approved agreement (Q51) |
| For | The Sedra team, node runners, miners, pool operators, exchanges and wallet users, and anyone who wants to understand the test before reading the details |
| Details | [GUIDE.md](GUIDE.md) (participants), [RUNBOOK.md](RUNBOOK.md) (operator), [SIP-0003](../proposals/SIP-0003-public-testnet.md) (why and pass criteria), [SIP-0001](../proposals/SIP-0001-merged-mining.md) (the rules tested) |

Labels: **Verified** (checked, with evidence), **Inferred** (reasoned, could be wrong), **Unknown**.

## 1. In one paragraph

The testnet is a separate Sedra network with worthless test coins. It runs the merged-mining rules of SIP-0001 in
public before anyone decides anything about Sedra mainnet. It starts as a normal Sedra chain mined by CPUs ("native
phase"). About two days in, a safety rule starts (the self-parent ban). About four days in, merged mining switches
on: from then on, Kaspa testnet-10 miners working through a merge-mining pool also produce Sedra testnet blocks.
Native mining keeps working. The testnet then runs at least two more weeks, and ends with a dated public report
against eight pass criteria. **Nothing in it touches Sedra mainnet.**

## 2. Your questions, short answers

**Does the difficulty start low?** Yes. The chain starts from the testnet genesis block that is already in Sedra's
Go and Rust nodes. Its difficulty is very low: about 130,000 hashes per block on average (target bits `0x1e7fffff`,
**Inferred** from the genesis values). The first 2,641 blocks are mined at that genesis difficulty, so one CPU makes
them within minutes (**Verified** in the private dry run of 2026-11-20). After that, the difficulty adjusts on every
block so that the whole network makes about **one block per second**, whatever hashrate is present (window of 2,641
blocks, as on mainnet).

**How are blocks found?**
- *Native phase (launch to activation):* a miner asks its node for a block template and searches for a nonce until
  the block's own hash meets the Sedra target (kHeavyHash, like Kaspa). Any CPU works with the project's
  `sedra-testnet-miner`, or Sedra's Go `sedraminer --testnet`. In the dry run, two CPU threads made about 2.3 MH/s.
- *After activation:* a pool builds Kaspa testnet-10 block templates whose coinbase carries a commitment to a Sedra
  block (`SDM1`). Miners hash on Kaspa work as usual. When a share's hash meets the **Sedra** target, the pool sends
  the Sedra block to a Sedra node together with the Kaspa header as proof. When it also meets the **Kaspa** target,
  it is a Kaspa testnet block too. So the same work counts for both chains. Native CPU blocks remain valid next to
  merged-mined ones.
- *Difficulty after activation:* if merged miners bring much more hashrate than the CPUs, the Sedra difficulty rises
  and CPU miners find fewer blocks. That is expected and is part of what the test shows (**Inferred**).

**Can we check the blocks?** Yes, at three levels.
1. *Your own node:* its log shows every accepted block; its RPC answers DAA score, tip and individual blocks.
2. *The monitor* (`sedra-testnet-monitor`): asks several nodes every minute whether they have the same chain, and
   marks every block as **native** or **merged-mined** with its pool tag. Anyone can run it against their own node
   (GUIDE section 4). The operator posts a daily summary on issue #13.
3. *A public status page* (SIP-0003 §4.4): built 2026-11-24 (sedra-rusty `testnet-kit`,
   `contrib/testnet/status_page.py`). Refreshed every minute from the monitor's data, it shows the phase and the
   progress to the ban start and the activation, every node and whether it still has the same chain, native and
   merged-mined block counts, the share per pool tag and the most recent blocks, plus a `status.json` for scripts.
   **Verified** on a private loopback testnet on 2026-11-24. Restyled in the puddlepool.com look on 2026-11-25
   (sedra-rusty branch `testnet-status-ui` `71ff3e3`: TESTNET banner, countdowns, difficulty and hashrate, the eight
   pass criteria with live status, join guide, faucet and release links). Served at **https://testnet.puddlepool.com**
   by Caddy on the VPS (Let's Encrypt, set up 2026-11-25); VM 204 builds it and uploads it over its one SSH link.
   Since 2026-11-25 (`f924387`) it also shows the private ZKas test chain (D11) and proposed criterion 9: the monitor
   reads zkasd directly and pairs Sedra and ZKas blocks from one Kaspa parent by their nonce (on both chains a
   merged-mined block's nonce is the first 8 bytes of its parent's hash). Native/merged classification of ZKas blocks
   is **not yet checked** on real blocks (none exist yet).
   It is not a full explorer: no transactions or addresses.

**Do we need miners?** Yes, of two kinds.
- *Native (CPU) miners* from day one. Without them there are no blocks at all. The operator's seed node mines at
  launch; more CPUs make the chain more realistic.
- *Kaspa testnet-10 miners* (GPU or ASIC software that speaks Kaspa stratum) from activation on, at the testnet pool.
  Without them, merged mining cannot be shown (criterion 2). Kaspa testnet-10 itself had about 46 MH/s in total on
  2026-11-20 (**Verified**, api-tn10.kaspa.org). A few GPUs are enough; how many will join is **Unknown**.

**Do we need nodes?** Yes.
- *Two seed nodes* reachable from the internet (port 22211), ideally at two different places. The testnet has no
  DNS seeders, so everyone connects to these with `--addpeer`.
- *One unchanged Go node* (sedrad v2.0.0 `--testnet`), never upgraded, to show what happens to nodes that do not
  upgrade (criterion 3: it follows until the first merged-mined block, then stops).
- *One Kaspa testnet-10 node* for the pool (upstream Kaspa software).
- *Nodes run by outsiders:* not required for the chain to work, but criterion 7 asks for at least one participant
  outside this project.

**Do we need a pool?** Yes, one testnet pool for merged mining (Miningcore, separate from any production pool, own
database and wallets). It pays Kaspa testnet coins and Sedra testnet coins (criterion 5). Other pools may join.

**Can someone attack it?** Testnet coins are worthless, so there is little reason to, but it is possible: someone
with a strong Kaspa miner could mine a heavier chain from the same genesis and pull nodes onto it. The monitor would
show it; the reaction is in RUNBOOK §6 (pause, report, reset if needed). Accepted risk for a testnet.

## 3. What runs, and who runs it

| Part | Needed for | Runs it | Status |
|---|---|---|---|
| Testnet node release `0.2.0-testnet.1` | everyone who runs a node | this project builds, Nec signs | release candidate ready 2026-11-24, not published |
| Seed node 1 (also mines the first blocks) | the chain to exist | Nec | at home (D3); VM not set up yet |
| Seed node 2 | a second place to connect | Nec (volunteers welcome as extra seeds) | rented VPS (netcup, EU), hardened 2026-11-24, node not installed yet ([HOSTING.md](HOSTING.md)) |
| Unchanged Go node | criterion 3 | Nec | host not chosen |
| Kaspa testnet-10 node | the pool | Nec | at home on SSD (D3), VM not chosen; too big for a cheap VPS (Kaspa guidance: 8 cores, 16 GB RAM, 640 GB SSD), so at home on SSD; real testnet-10 need **Unknown** ([HOSTING.md](HOSTING.md) 1.2) |
| Testnet pool (Miningcore) + database + wallets | merged mining, payouts (criteria 2, 5, proposed 9) | Nec | config ready; Kaspa testnet payout path checked on a private chain; ZKas aux entry added 2026-11-25 (D11) |
| Private ZKas test node (pool only) | criterion 9 (proposed) | Nec | VM 206, next to the Kaspa node; being set up 2026-11-25 |
| Monitor + daily summary | evidence for criteria 1, 2, 3, 8 | Nec | ready (dry run) |
| Faucet (test coins on request) | people without miners | Nec, by hand from GitHub issues | ready (dry run) |
| Public status page | anyone checking blocks | Nec | https://testnet.puddlepool.com: Caddy with HTTPS on the VPS since 2026-11-25; page built on VM 204 and uploaded every minute |
| Announcement | people knowing it exists | the Sedra team, if they agree (Q48) | waiting |

## 4. Decision points

| # | Decision | Who decides | Status (2026-11-24) |
|---|---|---|---|
| D1 | Duration (at least two weeks after activation) and the eight pass criteria | Sedra team (Q51) | Conditional yes in an unapproved working draft (2026-11-23); an approved yes is awaited |
| D2 | Which chain: fresh chain from the existing testnet genesis | Nec (Q47, Q52) | Decided: fresh chain. Q52 (does anyone run the old one) stays open as information |
| D3 | Where the seeds, Go node, Kaspa node and pool run (one host, a rented second place, or a volunteer's seed) | Nec | **Decided 2026-11-24** ([HOSTING.md](HOSTING.md)): seed2 (and later a public mainnet node and the status page) on a rented netcup VPS 1000 G12.5 in the EU, outside the home network; seed1 (mining), the old Go node, the Kaspa testnet-10 node, the pool and the monitor at home. VPS delivered and hardened 2026-11-24; seed2 not installed yet |
| D4 | Start date | Nec, with the Sedra team | Proposed Tue 2026-12-01; not agreed, not announced |
| D5 | Activation and ban scores | design (RUNBOOK 3.1) | Decided: activation DAA 345,600, ban start 172,800, built into the release |
| D6 | Publish the release (tag, signature, pre-release) | Nec, after D1 | Prepared; the go steps are in [release/v0.2.0-testnet.1-go.md](../release/v0.2.0-testnet.1-go.md) |
| D7 | Who announces, and the text | Sedra team (Q48), text from Nec | Waiting; the announcement must say: test network only, no mainnet date, no change to supply |
| D8 | Public status page or explorer (promised in SIP-0003 §4.4) | Nec | Decided 2026-11-24: a status page from the monitor's data (built), served at https://testnet.puddlepool.com (2026-11-25); a full explorer is not planned |
| D9 | Pause, fix, reset during the test | Nec, and the Sedra team if they take part | Rules set in RUNBOOK §6: a consensus failure pauses the test, the fix is re-tested, the two-week clock restarts (also the Sedra team's condition in its 2026-11-23 draft) |
| D10 | Pass or fail, and what follows | the report, then the Sedra team and Nec together | After the test. A mainnet date is only discussed after a passed report |
| D11 | ZKas in the same coinbase as Sedra, as the mainnet pool would do it | Nec | Decided 2026-11-25: yes. The testnet pool also merges a **private ZKas test chain** (pool only, not a public network) under the same Kaspa testnet-10 parents. Proposed as an extra criterion 9 in SIP-0003, beyond the eight the Sedra team accepted. Reason: this combination was never tested against real nodes (SIP-0001 §9, corrected 2026-11-25) |

## 5. Step by step

Dates are the proposal for a 2026-12-01 start; if D1 or D4 moves, every later date moves by the same amount.
"Day N" counts from the launch.

### Before launch

| Step | Sedra team | Nec (operator) | Participants |
|---|---|---|---|
| 1. Agreement | Approve the duration and the criteria (D1), say whether you announce (D7) | Choose the hosts (D3) | - |
| 2. Release | - | Sign and publish `0.2.0-testnet.1` (D6) | - |
| 3. Rehearsal (proposed 11-30) | - | Start everything on the real hosts without announcing, stop, wipe | - |
| 4. Readiness check | - | RUNBOOK §1: Kaspa testnet-10 up and unchanged, hosts reachable, release verified | Optional: download and verify the release (GUIDE §3) |

### Launch day (proposed 12-01)

| Step | Who | What happens |
|---|---|---|
| 5. First blocks | Nec | Seed 1 starts and mines the first blocks to the faucet wallet. The 2,641 low-difficulty blocks come within minutes, then the chain settles at about one block per second |
| 6. Network up | Nec | Seed 2, the Go node, the Kaspa node, the pool and the monitor start; the monitor shows all nodes on the same chain |
| 7. Announce | Sedra team (if agreed), Nec on #13 | The guide link, seed addresses, the release, the two scores (172,800 and 345,600) |
| 8. Join | Participants | Run a node (GUIDE §4), create a testnet wallet (§5), mine with a CPU (§6), ask the faucet for coins (§5) |

### Native phase (day 0 to about day 4)

| Step | What to watch |
|---|---|
| 9. Normal Sedra mining | Blocks at about one per second; the Go node follows the Rust nodes; wallets send and receive (criterion 6) |
| 10. Ban start (DAA 172,800, about day 2) | From here, a Sedra block whose own coinbase carries an `SDM1` commitment is invalid on upgraded nodes. Nec tests it once just before and once just after (criterion 1) |
| 11. Prepare merged mining | Kaspa miners set up: Kaspa testnet-10 address, Sedra testnet address, pool login (GUIDE §7) |

### Activation (DAA 345,600, about day 4)

| Step | What to watch |
|---|---|
| 12. Merged mining switches on | The first merged-mined Sedra block is accepted by every upgraded node (criteria 1, 2) |
| 13. Old node falls off | The unchanged Go node rejects the first merged-mined block and stops following. Expected (criterion 3) |
| 14. Both kinds of blocks | Native and merged-mined blocks side by side; the monitor counts them per pool tag |

### Running (at least two weeks after activation)

| Step | What happens |
|---|---|
| 15. Daily | Nec posts the numbers on #13: blocks native and merged, nodes up, agreement, alerts. Bad news is posted like good news |
| 16. Fresh node (from about day 7) | After the first pruning point above the activation, a new node syncs from scratch, including merged-mined headers (criterion 4) |
| 17. Payouts | The pool pays both coins to at least two test miners with different addresses (criterion 5) |
| 18. Problems | Anyone reports through the "Testnet report" issue template. A consensus failure pauses the test; the fix is re-tested and the two-week clock restarts |

### End (earliest about day 18, proposed report about 12-21)

| Step | Who | What |
|---|---|---|
| 19. Report | Nec | The pass report, criterion by criterion with evidence ([template](PASS-REPORT-TEMPLATE.md)), published on #13 and sent to the Sedra team |
| 20. Next step | Sedra team and Nec | Only if it passed: talk about a mainnet plan. A mainnet activation needs its own announcement, releases and coordination with pools and exchanges (SIP-0001) |
| 21. Wind-down | Nec | Seeds keep running at least one more week for late reports, then stop. Data stays archived |

## 6. What each group should know

- **Sedra team:** your part is D1, D7 and, if you like, running a node or a seed. Report anything you see on #13;
  a consensus failure pauses the test until it is fixed and re-tested (your condition in the 2026-11-23 working
  draft, and RUNBOOK §6).
- **Node runners:** use only the testnet release, always with `--testnet`. It refuses to start without it, so it
  cannot run on mainnet by accident. Keep the RPC port (22210) closed to the internet.
- **Miners:** CPU mining works from day one; GPUs and ASICs count only through merged mining after activation. Testnet
  coins have no value.
- **Pool operators:** you can run your own testnet pool from the published config; set the testnet `genesisHash`, use
  separate databases and wallets, never your production pool.
- **Exchanges, wallets, mainnet users:** nothing to do. Mainnet is not affected and no mainnet date exists.

## What this does NOT mean

- It does not launch the testnet or fix a date; the dates above are a proposal.
- The Sedra team's 2026-11-23 reply is an unapproved working draft; it is not counted as agreement.
- A passed testnet does not schedule merged mining on mainnet.
- Values marked Inferred (block counts, timings, how merged miners change the difficulty) are predictions, not results.
- Testnet coins have no value, now or later. There is no reward, airdrop or allocation for taking part.
