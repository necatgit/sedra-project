# Questions and answers

**The one list of every open question in this project.** Other documents (research, proposals, issues) may describe a
question in context, but they link here by ID instead of keeping their own lists.

Rules:
- Every new question gets the next free ID here first, with a link to where it came from.
- Questions are never deleted. Answered ones stay with their answer and its source; dropped ones say why.
- IDs never change, so links from other documents and commits stay valid.

Status: **Open** (not asked yet) · **Asked** (sent to someone, waiting) · **Investigating** (being worked on in this
project) · **Proposed** (a draft answer exists, not decided) · **Answered** · **Dropped**

Summary (2026-11-06): 38 questions; 5 answered, 13 asked and waiting, 15 open, 3 being investigated, 1 proposed,
1 split.

## A. Working with the Sedra team

| ID | Question | Source | Asked whom / when | Status | Answer and source |
|---|---|---|---|---|---|
| Q3 | Does the Sedra owner support the merged-mining fork, and should development happen in `sedracoin/sedrad` or a separate repository? | Owner letter; SIP-0001 §10 | Sedra owner, 2026-11-05 (direct message) | Asked | Acknowledged 2026-11-05: "Got it, I check later and give a response" |
| Q6 | Is there anyone else (developer, community manager, exchange contact) to talk to? | Owner letter | Sedra owner, 2026-11-05 | Asked | |
| Q7 | Who runs the seed nodes, DNS seeders (`sedra-seed-1/2/3`), api.sedracoin.com, the explorer, the website and the two fallback peers? | Owner letter; [research/0004](research/0004-rust-path.md) | Sedra owner, 2026-11-05 | Asked | |
| Q8 | Which exchanges list SDR, who has the contacts, and what have they said about delisting? | Owner letter | Sedra owner, 2026-11-05 | Asked | |
| Q9 | Which announcement channels are official, and can Nec post updates there? | Owner letter | Sedra owner, 2026-11-05 | Asked | |

## B. The v2.0.0 relaunch: treasury, supply and releases

| ID | Question | Source | Asked whom / when | Status | Answer and source |
|---|---|---|---|---|---|
| Q4 | (Collective question about the v2.0.0 relaunch) | [research/0001](research/0001-relaunch-review.md) | Sedra owner, 2026-11-05 | Split | Split into Q10-Q17 on 2026-11-06 to track each part separately |
| Q10 | The code calls the treasury "CLTV-timelocked with multi-year vesting", but the on-chain script is a plain 2-of-3 multisig. Is vesting enforced some other way, or is the description out of date? | [research/0001](research/0001-relaunch-review.md#questions-sent-to-the-sedra-owner-2026-11-05) Q1; #19 | Sedra owner, 2026-11-05 | Asked | |
| Q11 | Who holds the three treasury keys? | research/0001 Q2; #19 | Sedra owner, 2026-11-05 | Asked | |
| Q12 | About 1.997B SDR has left the treasury address (balance 32.93M on 2026-11-05); only ~228M of the outflows are visible. Where did the rest go, and is there a plan for the treasury? | research/0001 Q3; #19 | Sedra owner, 2026-11-05 | Asked | |
| Q13 | Can the explorer's transaction index ("Transactions not up to date") be repaired? | research/0001 Q4; #19 | Sedra owner, 2026-11-05 | Asked | |
| Q14 | Circulating supply is about 6.0B SDR above what the published code can have emitted, including the treasury. Where does the difference come from? | research/0001 Q5; #19 | Sedra owner, 2026-11-05 | Asked | |
| Q15 | Which commit and toolchain built the mainnet binaries? | research/0001 Q6; #19 | Sedra owner, 2026-11-05 | Asked | |
| Q16 | Can checksums for the release binaries and a signed `v2.0.0` tag be published? | research/0001 Q6; #19 | Sedra owner, 2026-11-05 | Asked | |
| Q17 | Who mined the blocks in the difficulty-reset and treasury windows (DAA ~53.63M), and were independent miners and nodes online? | research/0001 Q7; #19 | Sedra owner, 2026-11-05 | Asked | |
| Q26 | Was the subsidy-table change of 2025-04-08 (`e61214d`, entries from month 8 = DAA 36,558,000) retroactive, i.e. had the chain already passed that DAA score? If so, old coinbases follow a different table. | [research/0004](research/0004-rust-path.md#risks-and-open-questions) | — | Open | Needs chain data (a coinbase at DAA ≈ 36.6-39M) or an answer from the team |
| Q29 | Why did only 163 of 200 (window 1) and 400 of 454 (window 2) DAA scores carry a treasury output? | research/0001; research/0004 | — | Investigating | Likely because only chain blocks' coinbases enter the UTXO set (developer comment in sedrad `params.go`); not counted on chain yet, because those blocks are pruned |

## C. The merged-mining proposal (SIP-0001)

| ID | Question | Source | Asked whom / when | Status | Answer and source |
|---|---|---|---|---|---|
| Q1 | Can one Kaspa block carry merged-mining commitments for both ZKas and Sedra? | #3 | — (research) | Answered | Yes, but only just: ~145 bytes free, two 68-byte commitments leave ~9 bytes for the pool tag, a third never fits. [research/0002](research/0002-zkas-auxpow.md) |
| Q18 | Should Sedra coordinate a shared commitment format with ZKas, or use a shorter commitment, to save coinbase space for pools? | [SIP-0001 §10](proposals/SIP-0001-merged-mining.md#10-open-questions) Q2; research/0002 | — | Open | |
| Q20 | How does Sedra keep up with future Kaspa header format changes, which would stop merged mining until Sedra updates? | SIP-0001 §4.6 and §10 Q3; research/0002 | — | Open | |
| Q21 | Which Kaspa pools besides PuddlePool would add Sedra merged mining? | SIP-0001 §10 Q4; research/0002 | — | Open | |
| Q22 | Do Sedra holders accept that merged mining lets a large Kaspa pool dominate Sedra at no extra cost, and is any mitigation wanted? | SIP-0001 §8 and §10 Q1; research/0002 | — | Open | |
| Q23 | How does Sedra's difficulty adjustment react when large merged hashrate joins or leaves suddenly? | SIP-0001 §8; research/0002 | — | Open | To be measured on the public testnet |
| Q24 | Should Sedra's self-parent ban cover only Sedra's own tag, so Sedra blocks may keep carrying ZKas commitments? | research/0002 | — | Proposed | Yes: SIP-0001 §4.5 (draft, pending review) |
| Q25 | Could a pool put a raw-bytes commitment into the Kaspa coinbase instead of hex (it would save space)? Kaspa's `getBlockTemplate` only takes a UTF-8 string. | research/0002 | — | Open | |
| Q33 | How are the activation DAA score and the notice period decided, and with whom? | SIP-0001 §10 Q5 | — | Open | |

## D. Building the Rust node (technical)

| ID | Question | Source | Asked whom / when | Status | Answer and source |
|---|---|---|---|---|---|
| Q2 | Should AuxPoW be added to the Go node, or should Sedra move to the Rust codebase? | #4 | — (research + decision) | Answered | Rust, based on rusty-kaspa v1.0.1, in two steps; decided by Nec on 2026-11-05. [research/0004](research/0004-rust-path.md) |
| Q19 | Does Sedra's code hash Kaspa parent headers (current Kaspa block version 2) byte for byte as Kaspa does? | research/0002; SIP-0001 §8 | — | Open | To be tested with real Kaspa mainnet headers in M10 (#10). For Sedra's own headers this is answered: 2001 real blocks match (M3, #22) |
| Q27 | Does any archival Sedra node (full history from genesis) exist? Without one, rules before the pruning point can only be checked partially. | research/0004 | — | Open | |
| Q28 | Are `sedracoin/go-muhash` v1.0.1 and `sedracoin/go-secp256k1` v1.0.2 identical to Kaspa's originals? | research/0004 | — (research) | Answered | Yes, in code: no difference in any code file after normalising the module name; only `go.mod`, fuzz-test corpus and `.gitattributes` differ (2026-11-06). [Evidence](research/archive/2026-11-06-q28-q36/README.md) |
| Q30 | Are there other Go-vs-Rust differences near genesis besides the minimum difficulty window (2641 vs 150, fixed in M1)? | research/0004 | — | Open | |
| Q31 | Which rusty-kaspa fixes after v1.0.1 are security-relevant for a 1-block-per-second legacy node and must be back-ported? | research/0004 | — (research) | Answered | Four must-fix crash/validation fixes and several recommended ones; most hidden in large upstream commits, re-applied by hand. [research/0006](research/0006-security-backports.md), tracked in #29 (2026-11-06) |
| Q32 | Does PuddlePool's Miningcore Sedra integration work against the Rust node's gRPC interface? | research/0004 | — | Open | Partly: Sedra's own `sedractl` and `sedraminer` work against the Rust node (M4, M8) |
| Q34 | Why did one synthetic block in `bounded_merge_depth_test` get block level 3 with Sedra's genesis data? | M1 (#20), M3 (#22) | — | Open | Real Sedra blocks show no such anomaly (2001 blocks, M3) |
| Q35 | What causes the Rust node's warnings "Locally built proof for level N does not match the applied one" after accepting the Go node's pruning proof? | M5 (#24) | — | Investigating | Not the incomplete window (corrected 2026-11-06): 14 warnings per proof application, levels 0-13, with and without a complete window (154 = 11 × 14 in the first attempt). The applied proof is valid: the synced state is identical to the Go node's (M7). Only the Rust node's own rebuild of the lower levels differs. Update 2026-11-06: the Go proof's level 13 has a selected-tip blue score of 1998 < 2M inside the proof, which made upstream check 48b63582 reject it; points to the Go and Rust proof builders selecting slightly different blocks (Inferred). [Evidence](research/archive/2026-11-06-m5-m7/README.md), [proof checks](research/archive/2026-11-06-proof-checks/README.md) |
| Q36 | Does the inherited `isStaged()` bug in sedrad (checks `addedByIndex` twice, never `removedByIndex`) have any practical effect, and should it be fixed in the Go node? | [research/0005](research/0005-test-coverage.md) | — (research) | Answered | No practical effect: the only write to `removedByIndex` (`headers_selected_chain_store.go:56`) is always followed by one to `removedByHash`, so `isStaged()` still returns true. Redundant code, not a functional defect; fixing it is optional (2026-11-06). [Evidence](research/archive/2026-11-06-q28-q36/README.md) |
| Q37 | Does sedrad (Go) block its RPC while serving a syncing peer, and does it recover without a restart? Observed: a production node's RPC was frozen ~8 minutes until restarted | M5 (#24), [incident](research/archive/2026-11-06-m5-production-sync-incident/README.md) | — | Investigating | Observed 2026-11-06; cause not yet confirmed in the Go code |
| Q38 | Does the Rust node block its RPC in the same way when it serves a syncing peer? | M5 (#24), incident 2026-11-06 | — | Open | To be tested on the test VM, never against production |

## E. The public Sedra network

| ID | Question | Source | Asked whom / when | Status | Answer and source |
|---|---|---|---|---|---|
| Q5 | Do the public fallback peers (169.58.111.191, 169.58.126.141) serve incomplete DAA windows to syncing nodes, and were they themselves synced via headers proof? A fresh Go node synced from them has 2,039 of 2,641 window blocks for the pruning point; a long-running node has all 2,641. | M5 (#24) | — | Open | |
