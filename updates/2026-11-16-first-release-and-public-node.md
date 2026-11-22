# 2026-11-16: The Rust node is released and runs as a public node

Covers 2026-11-14 to 2026-11-16.

## The seven-day run passed (M9)

From 2026-11-07 07:20 to 2026-11-14 07:20 UTC the Rust node ran next to two Go nodes and was compared with them every
minute: **10,064 checks, 0 alerts**, both nodes in sync on every check except one during a routine security update of
the test machine (level again after 80 s), and supply and treasury identical in all 29 comparisons that had a common
block (#28, closed with the full summary).

## v0.1.0 and v0.1.1

- **v0.1.0** (2026-11-14): the first public release of [sedra-rusty](https://github.com/necatgit/sedra-rusty), with
  exactly Sedra mainnet's current rules (no merged mining, no fork). It contains the soaked code plus the optional
  security back-ports from later Kaspa releases, which were merged after M9 so that the soak measured one version
  (#29, now closed). Full test suite on the release: 521 passed, 0 failed.
- **v0.1.1** (2026-11-15): documentation and a build-script exit code only; the node behaves exactly as 0.1.0
  ([notes](../release/v0.1.1-notes.md)).

Both tags are signed by Nec (key published at <https://puddlepool.com/keys.html>), and each release was rebuilt from
its tag on two different machines with **identical checksums**. Anyone can rebuild it and compare
(`docs/RELEASE.md` in sedra-rusty; results welcome on sedra-rusty#1). The whole day is recorded step by step in the
[release checklist](../release/v0.1.0-checklist.md).

## The public node

The former test machine now runs the release as a public node: P2P only, the RPC port stays on localhost. It ran 0.1.0
from 2026-11-14 and 0.1.1 since 2026-11-15 18:11 UTC.

- **Compared again:** for 24 hours (2026-11-14 15:13 to 11-15 15:14 UTC) the release binary was checked against the
  Go node: 1,439 checks, 1,427 at the same height and 12 one block apart for a moment, 0 errors, supply and treasury
  identical at start and end.
- **Outside nodes connect:** for the first hours nobody did; on 2026-11-15 around 16:40 UTC three outside nodes
  connected inbound.
- **Limit:** it runs on the same physical host as Nec's pool PuddlePool. It is an independent node, not independent
  hardware. A separate machine is the next step for it ([SIP-0002](../proposals/SIP-0002-network-resilience.md), #30).

## How small the reachable network is

A network map on the test machine probes every address its Go node knows, every six hours. On 2026-11-15 18:31 UTC it
knew 1,001 addresses and **4 accepted a P2P connection**; in the runs since, it knew only 4 addresses, all reachable,
and this project's public node is one of them. When the node started, two of Sedra's three DNS seeders returned no
addresses for it. This is exactly the weakness [SIP-0002](../proposals/SIP-0002-network-resilience.md) describes:
every additional public node matters. The seeder records were requested from the Sedra team on 2026-11-14; no answer
yet.

## What this does NOT mean

- The node does **not** merge-mine and changes **no** rules: v0.1.x follows Sedra mainnet exactly as the Go node does.
  Merged mining (step 2) is implemented and tested on local test networks only and is not active anywhere.
- Passing M9 and the 24-hour comparison shows the node agrees with the Go node under the conditions of those runs; it
  is not a security audit and not a guarantee against bugs that did not occur in that time.
- One public node does not make the network resilient. With four reachable nodes, the network still depends on very
  few machines.

## Next

- SIP-0003, the public testnet plan, goes to the public SIP repository after the Sedra team's reply on Q51/Q52, or on
  2026-11-17.
- A public write-up of the Go node security issues (research 0007) is planned for around 2026-11-23; this repository
  becomes public then. *Update 2026-11-22:* published on 2026-11-21, see [2026-11-22-week](2026-11-22-week.md).
- The treasury trace with an archival node, now that M9 is over.
