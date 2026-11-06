# M3 evidence (2026-11-06)

Milestone M3 (#22): real Sedra headers validated offline by the Rust node. Code: `necatgit/sedra-rusty` `dev`, commit
`b9b51075`.

| File | What it is |
|---|---|
| `export_headers.py` | Exporter: walks level-0 parents back from the tips of a local sedrad v2.0.0 node (via `sedractl GetBlock`) until 2000 DAA scores are covered, keeping all header fields in their original order and the hash the Go node reports |
| `sedra_headers_2000.json.gz` | Its output: 2001 blocks, DAA 61,175,445-61,177,445, 1101 chain blocks, up to 48 parent levels |
| `test-vm-m3-and-go-node.log` | Full test run with M3 (112 suites, 502 passed, 0 failed), the Go node's sync log and its systemd unit |

**Reference Go node:** sedrad v2.0.0 built from `4a1153d` on the test VM, `--nolisten` (no inbound connections),
RPC on localhost only, UTXO index on, low CPU/IO priority. It synced from the public network (fallback peers and
DNS seeds) in 25 minutes (4.4 GB) and matched the public node: pruning point `a990faed…20ed`, same DAA score and
difficulty. The pool's production node was not used.

**Results:** header hash Rust = Go for 2001/2001 blocks; proof of work passes for 2001/2001; 76,081 parent-level
references consistent with computed block levels (13..26). Mutation checks (swapped parent order, impossible
difficulty, a parent level forced to 0) each make the test fail.

**Not covered:** GHOSTDAG ordering, DAA scores, difficulty recalculation (M5). The synthetic level-3 block seen in M1
(`bounded_merge_depth_test`) remains unexplained; real blocks show no such anomaly.
