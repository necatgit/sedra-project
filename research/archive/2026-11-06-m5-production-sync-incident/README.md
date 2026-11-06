# Incident: syncing from a long-running Sedra node froze its RPC (2026-11-06)

**Why it was tried:** M5 (#24) was blocked because the public peers had served our Go node an incomplete DAA window
(Q5). A long-running Sedra node (the PuddlePool node operated by Nec) had the complete window, so the Rust node was
synced from it instead of waiting for the next pruning point move. Approved by Nec, with a watchdog that stops
the sync if the node slows down.

**What happened (UTC):** 16:41:40 the Rust node (sedra-rusty `b8182ca`) connected and started its initial
sync from it. From the first watchdog check at 16:42:13 the Go node (sedrad `2.0.0-relaunch`) answered no RPC request
(30 s timeouts). The sync was stopped at 16:43:30, but the Go node stayed blocked until it was restarted by its
operator around 16:49. RPC answered again at 16:50:06; the node was back at the network tip at 16:52:27. The Rust node
had not got past the first stage of the sync.

**Interpretation (Inferred):** sedrad does work for the new peer that blocks its RPC,
including a pool's block-template requests, and does not stop when the peer leaves. Not yet verified
in the Go code (QUESTIONS.md Q37).

**Consequences:** any public Sedra Go node that accepts inbound peers can have its RPC frozen for minutes by a new peer
starting a sync. For a pool node this means no new work for miners in that time. Never sync a test node from a
production node. Whether the Rust node behaves the same is open (Q38).

`watchdog.log`: the checks from the test VM (RPC response time of the production node, DAA lag).
