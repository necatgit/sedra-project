# 2026-11-07: Q38, does the Rust node freeze while it serves a syncing peer?

**Setup.** Two extra test nodes on the test VM, isolated from the M9 soak nodes, both sedra-rusty `210a906`:
node A (server) on last night's synced test database with **no outbound peers**, node B (client) with an empty
database connecting only to A. Every 0.5 s the script timed one RPC call (`GetBlockDagInfo`) to node A and read the
bytes A had sent on the P2P connection (`ss`).

**Result (Verified, `latency.log`, `summary-and-node-a.txt`, `node-b-key-lines.txt`):**

| Phase | RPC calls to A | Slowest | Over 1 s | Failed |
|---|---|---|---|---|
| Before B started | 30 | 19 ms | 0 | 0 |
| While A served node B (07:23:51-07:26:00) | 243 | 17 ms | 0 | 0 |
| After | 20 | 13 ms | 0 | 0 |

Node A built the proof (77,382 headers, 24,479 → 24,514 unique) at 07:24:45; node B received and validated it,
processed 2647 trusted blocks at 07:26:00 and continued syncing. **The Rust node's RPC stayed responsive throughout**,
unlike sedrad (Q37, frozen for about 8 minutes in the same situation). This matches the code reading: the Rust node does this work
without blocking its RPC.

**What this does NOT mean:** one serving of one proof was tested, on an otherwise idle node. Serving many peers at once
was not tested.
