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

**Update 2026-11-16 (Verified):** a network map on the test VM probes every address its Go node knows, every six
hours. On 2026-11-15 18:31 UTC it knew 1,001 addresses and 4 of them accepted a P2P connection; in the runs since
(2026-11-16 00:30 and 06:30 UTC) it knew 4 addresses, all 4 reachable. This project's public node is one of them.
When the public node started on 2026-11-14, two of Sedra's three DNS seeders returned no addresses for its lookup
(release checklist step 7; the seeder records were requested from the Sedra team the same day, no answer yet).

**Consequence (Inferred):** if the few public nodes fail, new nodes cannot find the network, and existing nodes may be
left with no peers, mining on an isolated chain until connections return.

## Proposed parts

1. **More independent public nodes.** The decisive part, and an operations task more than a code task. This project
   started with one public Rust node of its own: P2P only, running since 2026-11-14 (release v0.1.1 since 2026-11-15),
   with outside nodes connecting since 2026-11-15. It runs on the same physical host as Nec's pool, so it is an
   independent node, not independent hardware; a machine separate from any pool is the next step.
2. **More seeders and fallback peers** from independent operators in the node code (a small change; needs the
   operators first). Planned for Step 2.
3. **Peer memory ("parents and children").** Idea by Nec: a node remembers the peers it had good, long connections with
   and returns to them first after a restart or an outage, then exchanges newly discovered addresses with them, like
   neighbours gossiping. Bitcoin Core does something similar ("anchor connections": it saves its last outbound peers
   and reconnects to them on start).
   - **Parents** are the peers this node connected *to* (outbound). **Children** are the peers that connected *to this
     node* (inbound). Both are remembered with when they were last seen and how long and how well the connection
     worked.
   - The order on start: last good parents and children first. If none of them answers, the rest of the address book.
     The DNS seeders and hard-coded fallback peers come last.
   - What exists today (Verified in sedrad, 2026-11-11): the address book is already stored in the node's database and
     survives restarts (`infrastructure/network/addressmanager/store.go`). Inbound peers' advertised addresses already
     go into it (`app/protocol/flows/handshake/handshake.go:92`). Per address it only keeps the address and a count of
     failed connections (`addressmanager.go:34`). There is no "last seen", no "connection was good" and no order of
     preference.
   - Children are only useful as a way back if they can be reached. A node behind a router without an open P2P port
     can connect out, but nobody can connect to it.
   - To be designed: how many parents and children, how they are chosen and rotated, and how to stop an attacker from
     becoming everyone's parent (eclipse attacks). Not a consensus change: nodes with and without it work together.
4. **Opt-in "I am alive" announcement.** Idea by Nec: an operator who wants to can let the node report regularly that it
   is alive and reachable, so others can find it. It is off by default, and it is documented: what is sent, where it goes
   and how to switch it off. A node that announces itself reveals its IP address, so it has to be the operator's
   choice.
   - Where the reports are recorded is the open part. A single list run by one operator is a new central point, the
     same problem as today's seeders. Possibilities: several independent lists; or the DNS seeders accept
     announcements in addition to crawling; or a public list in a repository that anyone can mirror.
   - Whoever keeps a list must check every announcement by connecting back to the node. Otherwise anyone can register
     fake or hostile addresses.
   - Kaspa nodes already announce their own address to their peers through gossip if they know it is reachable
     (configured external IP). Part 4 adds a way to be found that does not depend on already being connected.
5. **The first contact cannot be avoided.** A brand-new node has no memory yet, so its very first peer has to come from
   somewhere: the DNS seeders, the hard-coded fallback peers, an address the operator enters by hand (`--addpeer` /
   `--connect`), or a published node list (part 4). Parts 3 and 4 do not remove this. They make sure a node needs it
   only once and can do without it after that, and part 2 makes that first contact depend on more than a few servers.
6. **Easy installation:** release binaries with checksums, packages and a Docker image, so running a node takes
   minutes.
4. **Easy installation:** release binaries with checksums, packages and a Docker image, so running a node takes
   minutes.

## What this does NOT change

No consensus rules, no coins, no fork. Parts 2, 3 and 4 are node software changes (part 4 also needs lists that
accept announcements) that old and new nodes can run side by side.

## Open questions

- Who besides this project would run public nodes and seeders? (Q7, Q40)
- Parts 3 and 4: design and testing on the public testnet (Phase 3).
- Part 4: where announcements are recorded, who runs those lists and how they check them (Q53).
