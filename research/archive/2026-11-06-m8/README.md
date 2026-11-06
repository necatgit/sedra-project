# M8 evidence (2026-11-06)

Milestone M8 (#27): mining parity between Sedra's Go node and the Rust node, on an isolated private devnet on the test
VM. Rust node: sedra-rusty `4873e9af`. Go node: sedrad v2.0.0 `4a1153d`. Miner: sedrad's own `sedraminer`.

**Setup.** Both nodes run `--devnet` (Sedra's devnet genesis, identical to its mainnet genesis), no DNS seeds, P2P and
RPC on localhost only; the Rust node connects only to the Go node. Both handshake with protocol version 5. The Go
node needs its hidden test option `--allow-submit-block-when-not-synced`, because a fresh devnet (genesis from 2015)
never counts as synced. Mining pays to a throwaway devnet-only address
(`sedradev:qzymwwym3zxmuml92zuneuzz7ek8juu2h9uls4eq98uh2gu4m95fjwg9htl8j`); its key stays on the VM and has no value.
Devnet parameters compared first: genesis, max target (2^255-1), max block level 250, K, block time, window and
subsidy are the same on both sides.

| Phase | What | Go node | Rust node |
|---|---|---|---|
| A | 300 blocks from the Go node's templates | DAA 300, tip `e88fa249…` | DAA 300, same tip, 0 errors |
| B | 300 blocks from the Rust node's templates | DAA 600, same tip, 0 rejects | DAA 600, tip `335d1149…` |
| C | 2 miners in parallel (400 + 400) | DAA 1400, tip `6f777154…` | same, 0 errors |

After phase C both nodes report the same balance for the mining address and the same circulating supply:
69,950,000,000,000 seep = 699,500 SDR = 1399 × 500 SDR. In the last 300 chain blocks, 178 had more than one parent and
562 parallel blocks were merged as blue.

**Not covered:** red blocks (none occurred; K = 18 needs much more parallelism) and transactions other than coinbase
payouts. These are left to M7/M9 with mainnet data.

`devnet-logs.txt`: miner summaries, the systemd units of both nodes, and the relevant log lines of both nodes.
