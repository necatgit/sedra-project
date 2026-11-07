# 0007: Security state of the public Sedra node (sedrad v2.0.0)

| | |
|---|---|
| Date | 2026-11-07 |
| Reviewed | `sedracoin/sedrad` tag `v2.0.0` = `4a1153d` (the code mainnet runs, see research/0001), compared with `kaspanet/kaspad` (Go) after v0.12.15 |
| Raw evidence | [archive/2026-11-07-go-node-audit/](archive/2026-11-07-go-node-audit/README.md) |

Labels: **Verified** = checked in code or by a tool, with the output archived. **Inferred** = interpretation, could be wrong.

## Summary

1. **Outdated network libraries with known, reachable vulnerabilities (Verified, `govulncheck` v1.1.4).** sedrad pins
   `google.golang.org/grpc` v1.38.0, `golang.org/x/net` v0.7.0 and `google.golang.org/protobuf` v1.28.1. govulncheck
   finds **12 vulnerabilities in these modules that sedrad's code actually reaches**, all through the gRPC server that
   carries both the P2P port and the RPC port (`grpc_server.go:62`, `grpc.Server.Serve`). They include a gRPC server
   panic (GO-2026-6443), HTTP/2 "Rapid Reset" (GO-2023-2153), an HTTP/2 CONTINUATION flood (GO-2024-2687) and several
   HTTP/2 memory and CPU exhaustion issues. **Impact (Inferred):** a node whose P2P port is reachable from the internet
   can be crashed or slowed down remotely, without any special access. Kaspa's Go node updated these libraries
   (kaspad `43b95239`); Sedra did not.
2. **A further 41 reachable vulnerabilities are in the Go standard library** of the toolchain used for the scan
   (Go 1.22.2). Whether they affect mainnet depends on which Go version built the mainnet binaries, which is not
   published (Q15).
3. **The node fixes Kaspa made after v0.12.15 are otherwise small (Verified by the raw report):** Kaspa changed no P2P,
   sync, pruning-proof or consensus-processing code after v0.12.15 except a one-line fix (the `isStaged` redundancy,
   Q36, harmless). Missing are some RPC and wallet fixes (kaspad `6b38bf70`, `0819244b`, `d2453f8e`, `a0149cd8`,
   `ed745a9a`), relevant mainly for services that pay out through the Sedra wallet daemon.
4. **The RPC freeze while serving a syncing peer (Q37) is not fixed in Kaspa's Go node either** (Go development
   stopped in 2024). It remains an open issue of the Go codebase.

## What to do about it (recommendations, Inferred)

- **Operators (now):** do not expose a pool's or service's Sedra node P2P port to the internet; never expose the RPC
  port. Outgoing connections are enough to follow the chain and to publish found blocks.
- **Sedra team:** a maintenance release of sedrad with updated gRPC / x/net / protobuf, built with a current Go version,
  with published checksums (Q16). Kaspa did the same library update without consensus changes.
- **This project:** the Rust node is not affected by these Go findings; its own dependencies were audited separately
  (research 0006, `cargo audit`).

## What this does NOT mean

- Not every listed vulnerability is necessarily exploitable in sedrad's configuration; govulncheck shows that the
  vulnerable functions are reachable, not that each attack works. None was tried.
- It does not mean anyone has attacked Sedra nodes; we have no evidence of that.
- It is not a consensus problem: no coins can be created or moved through these issues.
