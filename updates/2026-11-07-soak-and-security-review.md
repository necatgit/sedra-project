# 2026-11-07: Seven-day test started, and a security review of the public Sedra node

## M9: the seven-day run has started

The Rust node, with all security fixes, now runs next to a Go node on the test machine for seven days, until
2026-11-14 07:20 UTC (#28). Every minute both nodes are compared (block height, newest block, pruning point), every six
hours their total supply and the treasury balance. So far: no difference. The night before, the same build followed
the chain for about ten hours without a single error.

## Security review of the current Sedra node (sedrad v2.0.0)

Full details: [research/0007](../research/0007-go-node-security.md). In short:

- **Outdated network libraries (Verified with Go's official vulnerability scanner).** sedrad uses network libraries
  from 2021-2022 with 12 known vulnerabilities that its P2P and RPC server actually reaches, including a crash and
  several ways to exhaust memory or CPU. Kaspa updated these libraries in its own Go node; Sedra did not.
- **A new peer can freeze a node for minutes** (Q37, seen on 2026-11-06). Kaspa's old Go node behaves the same.
- **What operators should do:** do not open a pool's or service's Sedra node P2P port to the internet, and never the
  RPC port. The pool node used in this project closed its port on 2026-11-07 and works normally.

The Sedra team is being informed first; the suggested fix is a maintenance release with updated libraries (Q39).

## The Rust node does not freeze (Q38)

A Rust test node served a fresh node while we asked it for data every half second: it always
answered within 17 ms.

## Why the Go and Rust proofs differ (Q35)

They measure "2000 blocks deep" over different sets of blocks. The difference comes from Kaspa's Go node, is harmless,
and is the reason one newer Kaspa check stays switched off while Go nodes serve proofs.

## More fixes, and an idea for a sturdier network

- Five more small fixes from later Kaspa releases are ready and tested on a branch; they go in after the seven-day run,
  so the run measures one version.
- New idea document [SIP-0002](../proposals/SIP-0002-network-resilience.md): Sedra's own roadmap says the network
  should survive any single server going down. Today new nodes depend on very few public nodes. The proposal collects
  what would help: more independent public nodes (this project will run one after M9), more seed nodes, and Nec's idea
  of "parent" peers that a node returns to after an outage.

## Next

The daily M9 check, and a public Rust node once M9 has passed. Questions: [QUESTIONS.md](../QUESTIONS.md) (40 so far).
