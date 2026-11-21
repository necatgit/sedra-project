# Security advisory for Sedra node operators: sedrad v2.0.0

| | |
|---|---|
| Written | 2026-11-18; published 2026-11-21 (status last checked 2026-11-21, 07:30 UTC) |
| Affects | `sedracoin/sedrad` v2.0.0 (tag `v2.0.0` = `4a1153d`, the version Sedra mainnet runs); older sedrad versions use the same or older libraries (not checked one by one) |
| Severity | Denial of service: nodes can be stopped or slowed down from outside. **None of these problems lets anyone take coins directly or change the chain's rules** |
| Technical background | [research/0007](0007-go-node-security.md), [incident of 2026-11-06](archive/2026-11-06-m5-production-sync-incident/README.md), questions Q37, Q39, Q59 in [QUESTIONS.md](../QUESTIONS.md) |
| Evidence for this advisory | [archive/2026-11-18-sedrad-advisory-checks/](archive/2026-11-18-sedrad-advisory-checks/README.md) |
| Author | Nec (see the disclosure at the end) |

Labels: **Verified** = checked in code, by a tool or on a running node, with the output archived. **Inferred** =
interpretation, could be wrong. **Unknown** = not known.

This advisory explains what the problems are, who is exposed and what operators can do now. It deliberately leaves out
anything about how to cause the problems.

## Summary

- **Two problems in the current Sedra node, sedrad v2.0.0.** Both can make a node stop working for a while. Neither
  lets anyone take coins directly or change the chain's rules.
- **Who is exposed:** nodes whose P2P port (22111) or RPC port (22110) can be reached from the internet. By default,
  sedrad opens **both** ports on all network interfaces (Verified, see below).
- **What to do now:** close the RPC port to the outside, and on nodes that serve a pool, an exchange or an explorer,
  close the P2P port to incoming connections too. The node keeps following the chain and publishing blocks with
  outgoing connections only. This greatly reduces exposure; it does not remove it completely (see problem 1). Details
  in [What operators should do](#what-operators-should-do).
- **Status on 2026-11-21:** no fixed sedrad release exists. The Sedra team was told privately on 2026-11-09 and has
  said a maintenance release with updated network libraries is planned, without a date (Q39). No published security
  advisory from Sedra. We have no evidence that anyone has used these problems against Sedra nodes.

## The problems

### 1. A new peer can freeze a node's RPC for minutes (Verified on one node; cause Inferred)

When a sedrad node that accepts incoming P2P connections helps a brand-new node to join the network, it can stop
answering RPC requests for several minutes and may not recover without a restart.

**Observed (Verified):** on 2026-11-06 this happened to the sedrad node of the pool PuddlePool (operated by Nec) during
a test: its RPC answered nothing for about 8 minutes, until it was restarted by hand. The pool submitted no Sedra block
in that time (0 block candidates from 16:42 to 16:50 UTC, against about 28-32 per minute before and after).
[Incident report](archive/2026-11-06-m5-production-sync-incident/README.md).

**Impact (Inferred):** for a pool this is an outage: miners get no new work and the pool submits no blocks while it
lasts. For an exchange or an explorer, deposits and lookups stop. Any node on the internet that can open a P2P
connection to the node can cause this; no password or special access is needed. Whether a peer that the node itself
connects to (outgoing) can cause the same was not tested (**Unknown**). The exact cause in the Go code is not yet
confirmed (Q37). Kaspa's Go node, which sedrad is based on, has the same code and is probably affected the same way
(Inferred, not observed); Kaspa stopped developing its Go node in 2024.

### 2. Outdated network libraries with published vulnerabilities (Verified)

sedrad v2.0.0 still uses gRPC 1.38.0, x/net 0.7.0 and protobuf 1.28.1, all from 2021-2022 (`go.mod` at `4a1153d`).
Go's official vulnerability scanner, `govulncheck`, finds **12 published vulnerabilities in these libraries that
sedrad's code actually reaches**, all in the network server that runs both the P2P port and the RPC port. They are
public Go advisories with fixed versions (grpc, x/net, protobuf; the list with IDs is in the
[evidence](archive/2026-11-18-sedrad-advisory-checks/README.md#4-upstream-advisories)), and include remote crashes and
memory or CPU exhaustion. Kaspa updated the same libraries in its own Go node without any consensus change; sedrad did
not.

**Impact (Inferred):** a node whose P2P or RPC port is reachable from the internet can be crashed or slowed down from
outside. Not every one of the 12 is necessarily usable against sedrad in practice: the scanner shows that the
vulnerable code is reached, not that each attack works. None was tried.

Depending on which Go version built the official v2.0.0 binaries, there may be further vulnerabilities in Go itself
(41 more were found with the Go 1.22.2 toolchain used for the scan). The Go version of the official binaries is not
published (Q15; promised by the team by 2026-12-14).

### 3. An open RPC port is a risk of its own (Verified in code)

This is not a bug but the node's design, and it makes problem 2 worse: sedrad's RPC has **no password**, listens on all
interfaces by default, and unless the node is started with `--saferpc` it accepts administrative commands that change
the node's state. Anyone who can reach port 22110 can use them. The RPC port is meant for the operator's own software
(pool, wallet, explorer), never for the internet.

## Who is exposed

| Node | Exposed to | Why |
|---|---|---|
| Any node with RPC port **22110** reachable from the internet | Problems 2 and 3 | Default sedrad setting is to listen on all interfaces, with no password |
| Pools, exchanges, explorers, payment services whose node has P2P port **22111** reachable from the internet | Problems 1 and 2 | Default sedrad setting is to listen on all interfaces |
| Public nodes whose job is to accept peers (seed nodes, the fallback peers built into sedrad) | Problems 1 and 2 | They need the open P2P port, so they cannot simply close it |
| Nodes behind a router or firewall with no port forward, RPC not exposed | Much less exposed (Inferred) | Nobody outside can open a connection to them; they still connect out to peers, and whether such a peer can cause problem 1 is Unknown |

Home users running a wallet node behind an ordinary home router without port forwarding are usually not reachable from
outside (Inferred; check your router).

## What operators should do

These steps work with the current sedrad v2.0.0; none of them needs a new release.

1. **Never expose the RPC port 22110.** Start sedrad with `--rpclisten=127.0.0.1:22110` (or the private address your
   pool or service uses), block 22110 in the firewall, and add `--saferpc` unless you need the administrative
   commands. If your pool software runs on another machine, allow only that machine's address.
2. **Pools, exchanges, explorers and other services: close the P2P port 22111 to incoming connections.** Remove the
   port forward on the router or block incoming 22111 in the firewall. The node keeps making its own outgoing
   connections, so it follows the chain and publishes found blocks normally. **Verified on PuddlePool:** its P2P port
   forward was removed on 2026-11-07 and the pool has kept finding and publishing Sedra blocks since.
   - Binding P2P to the local machine with `--listen=127.0.0.1:22111` should have the same effect (Inferred from the
     code, not tested).
   - **Do not rely on `--nolisten`:** in sedrad v2.0.0 the flag exists but is never used by the code; the node still
     opens the P2P port on all interfaces. The same holds for nodes started with `--connect`, which sets the same
     unused flag (Verified by reading the code, not tested on a running node;
     [evidence](archive/2026-11-18-sedrad-advisory-checks/README.md#2-listen-defaults-and-flags-in-sedrad-v200-4a1153d)).
3. **Check from outside.** From a machine outside your network, test whether TCP 22110 and 22111 on your public address
   are reachable. A port that answers from outside is exposed, whatever the configuration file says.
4. **Watch every node, and especially the ones that must stay public** (seed nodes, fallback peers, which cannot close
   the P2P port): check every minute that RPC answers (for example a simple info request with a short timeout) and
   restart the node automatically if it stops answering for a few minutes. Keep public nodes separate from any node a
   pool or exchange depends on.
5. **Pools: keep a second node.** A pool that can switch to a second node, which itself accepts no incoming peers,
   loses less when one node freezes.
6. **Install the maintenance release when it comes**, after checking its published checksums (Q16, Q39). This
   advisory will be updated when it is out.

### An alternative node: sedra-rusty (with a conflict of interest)

[sedra-rusty](https://github.com/necatgit/sedra-rusty) is an independent Sedra node written in Rust, based on Kaspa's
current Rust node. **It is written and maintained by Nec, the author of this advisory, and is not a release of the
Sedra team**; sedrad remains Sedra's official node.

- Against problem 1 (Verified, one test): while a Rust node served a brand-new node, its RPC kept answering within
  17 ms (243 calls checked, Q38, [evidence](archive/2026-11-07-q38/README.md)). Serving many new peers at once was not
  tested.
- Against problem 2: it does not use the Go libraries. Its own Rust libraries were checked with `cargo audit` on
  2026-11-06: 10 known advisories remained after an update, none of them reachable from the network in the node as run
  there (Inferred from the dependency tree; [research/0006](0006-security-backports.md)).
- Against problem 3: its RPC listens only on the local machine by default, and administrative commands are off unless
  started with `--unsaferpc` (Verified in code, `sedra-v0.1.1`).
- It follows exactly the current Sedra mainnet rules (no fork) and ran seven days next to sedrad with no difference in
  10,064 checks (M9). Current release: v0.1.1 (2026-11-15), signed tag, reproducible build. It is young software with
  one maintainer; operators who switch should keep the same protection steps (1-5) and ideally keep a sedrad node as a
  second opinion.

## Timeline

| Date | What happened |
|---|---|
| 2026-11-06 | The RPC freeze (problem 1) observed on PuddlePool's sedrad node during a test |
| 2026-11-07 | Library scan with govulncheck (problem 2); PuddlePool closed its sedrad P2P port to incoming connections |
| 2026-11-09 | Both problems, the protection steps and the plan to publish them in about two weeks sent privately to the Sedra team |
| 2026-11-17 | The Sedra team's written reply (a draft) says the next maintenance release will have updated network libraries and a supported Go toolchain, with a candidate shared for review first; no date (Q16, Q39) |
| 2026-11-18 | Asked the team whether pools and the exchange have been told and whether the release will fix both problems (Q59); no answer yet |
| 2026-11-18 | Checked: no new sedrad release, no commit since 2026-08-11, no Sedra security advisory ([evidence](archive/2026-11-18-sedrad-advisory-checks/README.md#1-no-fixed-sedrad-release-yet)) |
| 2026-11-21 | Checked again: still no new sedrad release or commit, no Sedra security advisory, libraries unchanged, no answer to Q59 ([evidence](archive/2026-11-18-sedrad-advisory-checks/README.md#5-re-check-2026-11-21)) |
| 2026-11-21 | This advisory published, together with this repository |

## Current status (2026-11-21)

| Item | Status |
|---|---|
| Fixed sedrad release | **None.** Latest is v2.0.0 (2026-08-11) |
| Maintenance release with updated libraries | Planned by the Sedra team, no date (Q39) |
| Fix for the RPC freeze (problem 1) | **Unknown** whether the maintenance release will include it (Q59); not fixed in Kaspa's Go node either |
| Operators told by the Sedra team | **Unknown** (Q59) |
| Known attacks on Sedra nodes | None known to us |

This advisory is updated when any of these change.

## Disclosure

Nec holds about 250M SDR (roughly 1% of circulating supply) and has a direct interest in Sedra succeeding. Nec also
operates the pool PuddlePool, which mines Sedra, and writes the sedra-rusty node recommended above as an alternative.
This project is developed together with an AI, and that is stated openly.

## What this does NOT mean

- It does not mean the chain's rules or balances are affected: none of these problems lets anyone take coins directly
  or create them. A node that is down cannot serve its users, though, so an exchange or pool should treat an outage of
  its node seriously.
- It does not mean anyone has attacked Sedra nodes; we have no evidence of that.
- It does not mean every one of the 12 library vulnerabilities works against sedrad; they are reachable in the code,
  none was tried.
- It does not mean the Sedra team ignored the report: a maintenance release is planned; only its date and content are
  open.
- It does not mean sedra-rusty is free of problems: it was tested for problem 1 once, it has its own dependency
  advisories, and it is maintained by one person with a stake in Sedra.
- It does not mean nodes behind a firewall are safe from everything; it means they are not exposed to these problems
  from the internet.
