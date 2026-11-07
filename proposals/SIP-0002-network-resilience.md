# SIP-0002: Network resilience

| | |
|---|---|
| Status | **Idea** (not yet a full proposal; no code yet) |
| Author | Nec |
| Issue | #30 |
| Created | 2026-11-07 |

## Goal

Sedra's own roadmap says (stage "Built to last"): *"Many people run nodes, not only the team. … If any single server
goes down, ours included, Sedra stays up."* This proposal collects what is needed to make that true for the node
network.

## Where Sedra stands today (Verified, 2026-11-07)

- There is no "master node" in the code: every node validates every block itself and all nodes are equal (same design
  as Kaspa).
- Nodes already gossip: when two nodes connect they exchange lists of up to 1000 known node addresses
  (sedrad `app/protocol/flows/v5/addressexchange/`, Rust `protocol/flows/src/v5/address.rs`), keep them in a
  persistent address book, and aim for 8 outgoing connections.
- But the gossip has almost nothing to spread: a long-running pool node connected to only **three outside nodes** in
  60 hours, two of them the hardcoded fallback peers. New nodes find the network only through three DNS seeders
  (`sedra-seed-1/2/3`) and those fallback peers (who runs them: QUESTIONS.md Q7).
- Nodes behind a router without an open P2P port can connect out, but nobody can connect to them, so they never
  appear in other nodes' address books as reachable. Opening a Go node's P2P port is currently risky (research 0007,
  Q37); the Rust node does not have the sync-serving freeze (Q38).

**Consequence (Inferred):** if the few public nodes fail, new nodes cannot find the network, and existing nodes may be
left with no peers, mining on an isolated chain until connections return.

## Proposed parts

1. **More independent public nodes.** The decisive part, and an operations task more than a code task. This project
   starts with one public Rust node of its own after M9, on a machine separate from any pool.
2. **More seeders and fallback peers** from independent operators in the node code (a small change; needs the
   operators first). Planned for Step 2.
3. **Peer memory ("parents and children").** Idea by Nec: a node remembers the peers it had good, long connections with
   ("parents") and returns to them first after a restart or an outage, then exchanges newly discovered addresses with
   them, like neighbours gossiping. Bitcoin Core does something similar ("anchor connections": it saves its last
   outbound peers and reconnects to them on start). Kaspa's nodes keep an address book but have no such preference.
   To be designed: how many parents, how they are chosen and rotated, and how to avoid an attacker becoming everyone's
   parent (eclipse attacks). Not a consensus change: nodes with and without it work together.
4. **Easy installation:** release binaries with checksums, packages and a Docker image, so running a node takes
   minutes.

## What this does NOT change

No consensus rules, no coins, no fork. Parts 2 and 3 are node software changes that old and new nodes can run side by
side.

## Open questions

- Who besides this project would run public nodes and seeders? (Q7, Q40)
- Part 3: design and testing on the public testnet (Phase 3).
