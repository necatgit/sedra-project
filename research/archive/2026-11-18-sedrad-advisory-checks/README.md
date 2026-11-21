# 2026-11-18: checks for the sedrad v2.0.0 operator advisory

Checked 2026-11-18 between 14:00 and 14:30 UTC with `gh` (authenticated, read-only) from WSL. Summary and advice:
[research/0007-sedrad-v2.0.0-advisory.md](../../0007-sedrad-v2.0.0-advisory.md).

## 1. No fixed sedrad release yet

```
$ gh release list -R sedracoin/sedrad --limit 5
SEDRA v2.0.0 — Relaunch	Latest	v2.0.0	2026-08-11T14:46:34Z
Sedrad v1.0.2		v1.0.2	2025-04-08T09:01:32Z
Sedrad v1.0.0		v1.0.0	2024-02-16T12:44:24Z

$ gh api repos/sedracoin/sedrad --jq .pushed_at
2026-08-11T14:46:34Z

$ gh api "repos/sedracoin/sedrad/commits?sha=relaunch/v2.0.0&per_page=2" --jq '.[]|.sha[0:8]+" "+.commit.committer.date+" "+(.commit.message|split("\n")[0])'
4a1153d8 2026-08-11T14:25:29Z v2.0.0: treasury allocation supports multiple windows
f58dcb09 2026-08-11T03:36:06Z v2.0.0: treasury top-up window to bring foundation allocation to ~2B

$ gh api repos/sedracoin/sedrad/git/ref/tags/v2.0.0 --jq .object.sha
4a1153d8497d94f866961a67f25df722e2e3a0bc

$ gh api "repos/sedracoin/sedrad/contents/go.mod?ref=relaunch/v2.0.0" --jq .content | base64 -d | grep -E 'grpc |x/net|protobuf |^go '
go 1.19
	github.com/golang/protobuf v1.5.2
	google.golang.org/grpc v1.38.0
	google.golang.org/protobuf v1.28.1
	golang.org/x/net v0.7.0 // indirect

$ gh api repos/sedracoin/sedrad/security-advisories
[]
```

Branches: `1.0.0-new`, `main`, `relaunch/v2.0.0`. No commit after 2026-08-11 on any of them, no published security
advisory.

## 2. Listen defaults and flags in sedrad v2.0.0 (`4a1153d`)

Source: `gh api repos/sedracoin/sedrad/tarball/v2.0.0`, then `grep`.

- P2P listener: when `--listen` is not given, sedrad listens on **all interfaces**, port 22111
  (`infrastructure/config/config.go:433-437@4a1153d`; port from `domain/dagconfig/params.go:254@4a1153d`).
- RPC listener: when `--rpclisten` is not given, sedrad listens on **all interfaces**, port 22110
  (`infrastructure/config/config.go:446-450@4a1153d`; port from `domain/dagconfig/params.go:253@4a1153d`). The comment
  in the code says so too: "The default RPC listener is all addresses on the RPC listen port".
- `--nolisten` is **not read anywhere** except in `config.go` itself:

```
$ grep -rn "DisableListen" --include=*.go .
./infrastructure/config/config.go:86:	DisableListen  bool `long:"nolisten" description:"Disable listening for incoming connections -- ..."`
./infrastructure/config/config.go:421:		cfg.DisableListen = true
$ grep -rn "cfg.Listeners\|\.Listeners\b" --include=*.go . | grep -v _test
...
./infrastructure/network/netadapter/netadapter.go:45:	p2pServer, err := grpcserver.NewP2PServer(cfg.Listeners)
```

  The P2P server is always started on `cfg.Listeners`, which defaults to all interfaces. So **`--nolisten` does not
  close the P2P port** (Verified by reading the code; not tested on a running node).
- `--saferpc` (`config.go:101`, default off) makes the node refuse the RPC commands that change its state (for
  example peer management and shutdown; the checks are in `app/rpc/rpchandlers/`). Without it, anyone who can reach
  the RPC port can use them. The RPC server has no password option.
- `--connect` also only sets the unused `DisableListen` flag (`config.go:418-421`), so it does not close the P2P port
  either.

## 3. Rust node defaults (sedra-rusty `sedra-v0.1.1` = `2d3f8787`)

- RPC (gRPC) listens on **loopback** unless `--rpclisten` is given: `kaspad/src/daemon.rs:499@2d3f8787`
  (`args.rpclisten.unwrap_or(ContextualNetAddress::loopback())`). P2P listens on all interfaces
  (`daemon.rs:493`).
- State-changing RPC commands are off unless `--unsaferpc` is given: `kaspad/src/args.rs:103,257@2d3f8787`.

## 4. Upstream advisories

The 12 library vulnerabilities from the 2026-11-07 scan
([govulncheck-sedrad-v2.0.0.txt](../2026-11-07-go-node-audit/govulncheck-sedrad-v2.0.0.txt)) are all **published Go
advisories** with fixed versions, listed at `https://pkg.go.dev/vuln/<ID>`:

| Module (version in sedrad) | Advisories | Fixed from |
|---|---|---|
| `google.golang.org/grpc` v1.38.0 | GO-2023-2153, GO-2026-4762, GO-2026-6061, GO-2026-6348, GO-2026-6443 | v1.83.1 covers all five |
| `golang.org/x/net` v0.7.0 | GO-2024-2687, GO-2025-3503, GO-2026-6603, GO-2026-6611, GO-2026-6612, GO-2026-6617 | v0.60.0 covers all six |
| `google.golang.org/protobuf` v1.28.1 | GO-2024-2611 | v1.33.0 |

There is no Sedra-specific advisory and no CVE for the RPC freeze (problem 1, Q37); Kaspa's Go node has the same
behaviour and is no longer developed (research 0007).

## 5. Re-check 2026-11-21

Checked 2026-11-21 07:30 UTC with the same `gh` commands as in section 1:

```
$ gh release list -R sedracoin/sedrad --limit 3
SEDRA v2.0.0 — Relaunch	Latest	v2.0.0	2026-08-11T14:46:34Z
Sedrad v1.0.2		v1.0.2	2025-04-08T09:01:32Z
Sedrad v1.0.0		v1.0.0	2024-02-16T12:44:24Z
$ gh api repos/sedracoin/sedrad --jq .pushed_at
2026-08-11T14:46:34Z
branch tips: main e61214d5 (2025-04-08), relaunch/v2.0.0 4a1153d8 (2026-08-11), 1.0.0-new d1878914 (2024-01-02)
$ gh api repos/sedracoin/sedrad/security-advisories --jq length
0
go.mod on relaunch/v2.0.0: grpc v1.38.0, protobuf v1.28.1, x/net v0.7.0 (unchanged)
```

No change since 2026-11-18. Q59 (were operators told, will the release fix both problems) has no answer yet.
