# Public testnet: where it runs (decision D3)

| | |
|---|---|
| Status | **Comparison done 2026-11-24, waiting for Nec's choice.** Nothing rented, nothing set up. Updated the same day: OVHcloud VPS-2 cannot be ordered in Europe, so netcup is now the suggestion; Leaseweb added (see the correction note in section 5) |
| Decision | D3 in [OVERVIEW.md](OVERVIEW.md) section 4 |
| Why it matters | [SIP-0003](../proposals/SIP-0003-public-testnet.md) §6: all of this project's machines share one physical host and one home network, so two seeds there are not independent. A second, independent place is needed for an honest pass report |
| Budget | About USD 100-200 for a year, prepaid is fine (Nec's own money; nothing comes from the Sedra project) |
| Plan | Testnet from about 2026-12-01 to the report about 12-21, wind-down a week later; then the rented machine can serve as a public **mainnet** Sedra node and seed peer for the rest of the year ([SIP-0002](../proposals/SIP-0002-network-resilience.md), network resilience) |

Labels: **Verified** (checked, with source and date), **Inferred** (reasoned, could be wrong), **Unknown**.
All prices were read on the providers' own pages on **2026-11-24** unless marked otherwise. Prices, stock and terms
change; check them again on the order page.

## 1. What goes where

| Role | Where | Why |
|---|---|---|
| seed1 (testnet release, mines the first blocks with the CPU miner) | home VM | Mining happens here only: both shortlisted providers forbid mining in their terms (section 3), even worthless testnet CPU mining |
| **seed2** (testnet release, no mining) | **rented VPS** | The independent second place. Listed in the guide as a seed |
| old-go (unchanged Go sedrad v2.0.0) | home VM | Needs no public port; only the monitor reads it |
| Kaspa testnet-10 node | home (SSD only) | Far too big for this budget, see 1.2 |
| Testnet pool (Miningcore + Postgres + wallets) | home VM | Needs the Kaspa testnet-10 node next to it; separate from production as RUNBOOK §2 requires |
| Monitor, faucet | home VM | The monitor reaches seed2 through an SSH tunnel (RUNBOOK §2), so seed2's RPC stays closed |
| After the testnet: public mainnet Sedra Rust node (seed peer) | the same VPS | SIP-0002: a reachable node outside the home network |

### 1.1 Size of the VPS roles

| Item | Value | Label and source |
|---|---|---|
| Mainnet Rust node (sedra-rusty v0.1.1, `--utxoindex`, pruning), data directory | **3.0 GB** | **Verified** 2026-11-24 15:25 UTC: `du -sh` of the public node's appdir on this project's Rust node |
| Same node, memory in use | **2.2 GiB** RSS, load average 0.04-0.16 | **Verified**, same time, `ps -o rss=` and `uptime` |
| Testnet node | Smaller than mainnet: same 1 block/s, pruning depth 185,798 blocks (about 2.15 days), and a new chain with little transaction history | **Inferred** from the parameters in [DESIGN.md](DESIGN.md) §3.2; GUIDE §2 says 2 cores, 4 GB RAM, 20 GB disk for a participant node |
| Both at once (testnet wind-down week plus the mainnet node) | about 5 GiB RAM, under 20 GB disk | **Inferred**: the two measurements above added, plus the OS |
| Traffic | A few GB per day at most per node | **Inferred**: 1 block/s, small blocks, a few dozen peers. Any plan with 1 TB/month or more is enough |
| Address | **IPv4 required**, IPv6 welcome | **Inferred**: Sedra peers and the seed lists in the guide use IPv4 |

| | Minimum | Comfortable |
|---|---|---|
| CPU | 2 vCPU (x86-64, the release binaries are x86-64) | 4 vCPU |
| RAM | 4 GB | 8 GB |
| Disk | 40 GB SSD or NVMe (never HDD: the node's random reads need SSD; **Inferred**, plus this project's own experience with a node on spinning disks) | 64-128 GB NVMe |
| Network | IPv4, 1 TB/month or unmetered | the same, 1 Gbps port |

**Ports on the VPS:** `22211/tcp` open (testnet P2P), later `22111/tcp` open (mainnet P2P), `22/tcp` for SSH with keys
only. Everything else closed, including every RPC port (22210, 23110, 17210, 18210): they listen on localhost only.

### 1.2 The Kaspa testnet-10 node does not fit the budget

- Kaspa's own hardware guide for current releases asks for at least **8 CPU cores, 16 GB RAM, 640 GB SSD** and about
  80 Mbit/s; preferred 12-16 cores, 32 GB RAM, 1 TB SSD, and pool operators are "strongly recommended" to go toward
  the preferred end. **Verified**: rusty-kaspa `docs/toccata-guide.md` @ `46bf884` (2026-06-21), read 2026-11-24.
  That guide is written for mainnet; testnet-10 runs the same software at the same block rate, so the need is
  **Inferred** to be similar. The real figure for testnet-10 is still **Unknown** (RUNBOOK §2: measure during sync).
- The cheapest VPS near that size on this list (netcup VPS 4000 G12.5: 12 vCore, 32 GB, 512 GB) costs €45.36 a month
  (€544 a year incl. 19 % VAT), about three times the whole budget. **Verified**, netcup.com, 2026-11-24.
- So it runs at home, on SSD (not the HDD pool), next to the testnet pool. Where exactly is Nec's call; measure its
  disk and memory during the sync before the rehearsal on 11-30.

## 2. Offers compared (2026-11-24)

Yearly cost is for one machine, prepaid or on a 12-month term. EU consumers pay the VAT of their own country on
these services (**Inferred**, EU one-stop-shop rules), so the "approx. per year" column adds 25 % VAT to the net price
and converts at the ECB rate of 2026-11-24, 1 EUR = 1.0963 USD (api.frankfurter.dev). Your real total depends on your
country and payment method.

| Provider and plan | Spec | Price as shown | Approx. per year | Notes |
|---|---|---|---|---|
| **OVHcloud VPS-2 (2027 range)** | 4 vCore, 8 GB, 75 GB NVMe, unlimited traffic, 1 Gbps | from €7.21/month excl. VAT on a 12-month commitment (15 % off) | **€108 ≈ USD 119** | Anti-DDoS and daily backup included. Terms allow blockchain consensus use, forbid mining (section 3). **Comfortable spec, but no European location orderable on 2026-11-24** |
| OVHcloud VPS-1 (2027 range) | 2 vCore, 4 GB, 40 GB NVMe, unlimited, 500 Mbps | from €3.81/month excl. VAT, 12 months | €57 ≈ USD 63 | Meets the minimum; tight during the week both nodes run |
| **netcup VPS 500 G12.5** (now suggested) | 2 vCore x86, 4 GB, 64 GB SSD, traffic included | €8.26/month incl. 19 % VAT on 12 months (€9.50 monthly) | **€104 ≈ USD 114** | Locations Vienna, Nuremberg, Amsterdam; minimum term 1, 12 or 24 months; DDoS protection. **Minimum spec** |
| netcup VPS 1000 G12.5 | 4 vCore x86, 8 GB, 128 GB SSD, traffic included | €14.50/month incl. 19 % VAT on 12 months | €183 ≈ USD 200 | At the top of the budget |
| netcup VPS 500/1000 ARM G12.5 | same as x86, NVMe, Ampere | same prices | same | ARM64: the testnet release is built for x86-64 only. Not recommended |
| RackNerd Black Friday 4 GB KVM | 4 vCPU, 4 GB, 60 GB SSD, 10 TB/month, 1 IPv4 | USD 47.98/year, renews at the same price | USD 48 (+ VAT **Unknown**) | 8 GB plan USD 94.98/year (6 vCPU, 140 GB, 20 TB). US company, budget host; EU locations offered at checkout not checked; mining/node terms **not checked**. Sale page counts down, so this price is short-lived |
| BuyVM Slice 2048 / 4096 | 1 core, 2 GB, 40 GB SSD / 1 dedicated core, 4 GB, 80 GB SSD; unmetered | USD 7.00 / 15.00 per month | USD 84 / 180 | 2 GB is below the minimum. Stock often sold out (**Inferred**, not checked); locations not checked |
| Leaseweb VPS 2 (Leaseweb Netherlands B.V.) | 6 vCPU, 16 GB, 200 GB NVMe, 30 TB/month, 10GE virtual port, 1 IPv4, DDoS protection, Amsterdam | €8.99/month excl. tax monthly; €8.09 on a 1-year term (-10 %) | €121 ≈ USD 133 | Best spec for the money, but its terms need Leaseweb's **prior written approval** for running a crypto currency system, and it sells to businesses only (section 3). Not usable without that approval |
| Contabo Cloud VPS 4 | 4 vCPU, 8 GB, 100 GB SSD, 200 Mbit/s port | €4.40/month excl. VAT "for the first 24 months" | about €66 | Cheapest on paper, but the price needs a 24-month term, the port is slow, and see section 4. **Not recommended** |
| Hetzner Cloud | - | The shared "Cost-Optimized" line shows "Currently not available" on hetzner.com/cloud | - | Excluded by its terms (section 3) |
| DigitalOcean, Vultr, Linode, Scaleway | - | not priced today | - | Not checked live; 8 GB plans there are known to cost well above USD 200 a year (**Inferred** from earlier prices) |
| Oracle Cloud free tier (Ampere A1) | up to 4 OCPU, 24 GB, ARM | free | 0 | ARM (no x86 release), and idle free instances can be reclaimed: unsuitable for a seed that must stay up (**Inferred**, terms not read today) |
| Home only (no VPS) | - | - | 0 | Not independent (SIP-0003 §6); the pass report would have to say so |

Sources (all read 2026-11-24): [OVHcloud VPS](https://www.ovhcloud.com/en-ie/vps/) and its configurator;
[Leaseweb VPS 2 configurator](https://www.leaseweb.com/en/configure/vc/product/entityKey/VPS02_2), its
[sales terms](https://a.storyblok.com/f/294754123306010/4a3d889a01/sales-terms-and-conditions-leaseweb-netherlands-b-v.pdf)
and [policies](https://a.storyblok.com/f/294754123306010/b87891dafa/policies-leaseweb-netherlands-b-v.pdf);
[netcup VPS](https://www.netcup.com/en/server/vps), [netcup ARM](https://www.netcup.com/en/server/arm-server),
[netcup deals](https://www.netcup.com/en/deals); [RackNerd Black Friday](https://www.racknerd.com/BlackFriday/);
[BuyVM KVM slices](https://buyvm.net/kvm-dedicated-server-slices/); [Contabo VPS](https://contabo.com/en/vps/);
[Hetzner Cloud](https://www.hetzner.com/cloud).

Caveats seen while checking:
- The OVHcloud configurator listed **"No location available at the moment"** under Europe for VPS-2 on 2026-11-24,
  both in an automated browser and in Nec's own browser: it cannot be ordered in Europe today.
- netcup shows prices with German VAT on its site; the netcup deals page may add Black Friday offers later this week.

## 3. Terms of service on crypto nodes

| Provider | What the terms say | Effect for us |
|---|---|---|
| OVHcloud | General Terms of Services (version 2025-01-17) §3: "crypto-currency mining ... [is] strictly prohibited. As an exception, the Client may use consensus mechanisms such as Proof of Stake for the purpose of verifying transactions made on a blockchain, provided that such use is not abusive ..." The VPS-specific terms (version 2025-04-10) add nothing on crypto. **Verified**, contract PDFs from ovhcloud.com/en-ie/terms-and-conditions/contracts/, read 2026-11-24 | A node that verifies and relays blocks without mining fits the stated exception (**Inferred**: the wording names Proof of Stake as an example of verification, Sedra is Proof of Work). No mining on the VPS |
| netcup | General T&Cs §5: "Operation of mining-services such as "Bitcoin", "Ethereum", "OneCoin" or "Monero"" is prohibited; nodes are not mentioned. **Verified**, netcup.com/en/terms-and-conditions, 2026-11-24 | A non-mining node is not named as forbidden (**Inferred**). No mining on the VPS |
| Leaseweb (Netherlands) | Sales Terms and Conditions `LSW_NL_B2B_V.1NOVEMBER2026` §7.4: Customer must not use the Services "for any cryptographic use applied to blockchains including cryptographic use for mining or to maintain a crypto currency system" unless Customer complies with Leaseweb's KYC requirements and Leaseweb "has granted specific prior written approval"; extra electricity costs of such use can be charged. "Customer" means a business entity or an internet professional, not a private individual acting as a consumer (definitions). The Policies of the same version add nothing on crypto. **Verified**, both PDFs linked from leaseweb.com, read 2026-11-24 | A Sedra seed node maintains a crypto currency system: only with Leaseweb's written approval, asked for before ordering. Ordering as a private person does not fit their terms |
| Hetzner | Cloud and vServer agreement: "Operating applications that are used to mine crypto currencies" is prohibited (**Verified**, hetzner.com/legal/cloud-server, 2026-11-24). In 2022 Hetzner said in public statements that running even one node breaks its terms (reported by The Block, Decrypt and others, August 2022) | Excluded: the stated position on nodes is a suspension risk for a seed |
| RackNerd, BuyVM, Contabo | not read today | **Unknown** |

## 4. Reliability and lock-in

- **OVHcloud:** large European provider with its own data centres; 12-month commitment renews automatically for
  the same duration unless renewal is switched off in the control panel (configurator text, 2026-11-24). The terms
  allow throttling to 1 Mbps "in cases of excessive use" (VPS terms) (**Verified**); a node uses little traffic.
- **netcup:** minimum term 1, 12 or 24 months; price changes need six weeks' notice and give a right to terminate
  (T&Cs §4) (**Verified**). The server location cannot be changed after setup (FAQ) (**Verified**).
- **Contabo:** Contabo disclosed unauthorized access to its own systems on 2026-11-14 and reset all VNC passwords
  (reported in the press; **Inferred**, Contabo's incident page not read). There are public customer reports of
  servers deleted over billing problems in 2026 (LowEndTalk, single reports). The low price needs a 24-month term.
  For a seed whose whole point is staying up, that is the wrong trade.
- **RackNerd:** very cheap and renews at the same price (sale page FAQ, **Verified**); budget host, so neighbours and
  support are the risk. A reasonable fallback if both European options fail.

## 5. Recommendation

**Correction 2026-11-24 (same day):** the first version of this section recommended OVHcloud VPS-2. Nec's own check
on the order page also showed no location available in Europe, so it cannot be ordered now. The primary choice
moves to netcup; OVHcloud stays the better option if VPS-2 comes back in stock. Leaseweb VPS 2 was checked as a
replacement and is not recommended without Leaseweb's written approval (section 3).

**Primary (now): netcup VPS 500 G12.5** (2 vCore x86, 4 GB, 64 GB SSD, 12-month term), Amsterdam or Nuremberg.
About **€104 (≈ USD 114) a year**. Meets the minimum spec. To stay inside 4 GB, the mainnet node starts only after the
testnet seed stops (no overlap week). If the budget allows, **netcup VPS 1000 G12.5** (4 vCore, 8 GB, 128 GB, about
€183 ≈ USD 200 a year) is the comfortable version and can also host the static status page (D8).

**Earlier primary, if it comes back in stock: OVHcloud VPS-2 (2027 range)**, 4 vCore, 8 GB RAM, 75 GB NVMe, unlimited traffic, **12-month commitment**,
in an EU data centre away from the operator's home network (for example Frankfurt or one of the French sites).
About **€108 (≈ USD 119) a year** including 25 % VAT. Why: the comfortable spec for the price; the only shortlisted
terms that explicitly allow using a server to verify a blockchain; anti-DDoS and daily backups included; a large
provider with low suspension risk; NVMe.

**Cheapest fallback:** RackNerd 4 GB Black Friday KVM (USD 48 a year), only after reading its terms on crypto nodes
and picking an EU location at checkout. **Leaseweb VPS 2** only if Leaseweb approves the use in writing first.

**Not recommended:** Hetzner (terms on nodes), Leaseweb without written approval (terms, business customers only), Contabo (reliability, 24-month lock-in), ARM plans (no ARM release),
free tiers (can be reclaimed).

## 6. What Nec does, and what Claude does after that

Nec (Claude never creates accounts, pays or enters payment data):
1. Sign up at the chosen provider and order the plan above with the 12-month term. Choose the image **Ubuntu 24.04
   LTS** (or 26.04 if offered; sedra-archive runs 26.04). Location: an EU data centre outside the home country.
2. Add Claude's SSH public key in the order form or the control panel, the same way as for sedra-dev and
   sedra-archive (a dedicated key for this host; Claude creates it and sends you the public half when you say go).
3. Note the server's IPv4 address and say "the box is up". Disable automatic renewal later if you do not want the
   second year.

Claude, after that:
1. Log in with the key, create user `nec` with sudo, disable password and root SSH login.
2. Firewall (nftables or the provider's firewall): allow 22/tcp, 22211/tcp; later 22111/tcp; drop everything else.
   Unattended security updates on.
3. Install the verified testnet release as seed2 with the systemd unit from the kit (`MemoryMax`), and the SSH tunnel
   from the home monitor. Then the rehearsal on 11-30 (OVERVIEW step 3).
4. After the testnet: the mainnet Rust node (verified release v0.1.1 or later), P2P 22111 public, RPC on localhost.

## What this does NOT mean

- Nothing has been rented or set up; the choice is Nec's.
- The prices are what the pages showed on 2026-11-24; they are not a quote, and the yearly totals depend on VAT and
  currency.
- "Allowed by the terms" is our reading of the published wording, not the provider's confirmation. A provider can
  still suspend a server; that is why there are two seeds.
- One VPS plus home is two places, not a decentralised network. Outside participants running seeds (criterion 7)
  still matter.
- The Kaspa testnet-10 node size is still unmeasured; the figure above is Kaspa's general guidance.
