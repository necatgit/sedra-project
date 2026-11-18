# 2026-11-07: Go node audit (sedrad v2.0.0)

- `kaspad-go-fixes-raw.md`: raw report (unedited) of the comparison of kaspanet/kaspad after v0.12.15 with sedrad
  `4a1153d`; kaspad was only read with git, never built or run. *Held privately since 2026-11-18:* see
  [kaspad-go-fixes-held-private.md](kaspad-go-fixes-held-private.md).
- `govulncheck-sedrad-v2.0.0.txt`: `govulncheck` v1.1.4 on sedrad tag `v2.0.0`, Go 1.22.2, 2026-11-07. Exit code 3
  (vulnerabilities found). Reachable: 6 in `golang.org/x/net` v0.7.0, 5 in `google.golang.org/grpc` v1.38.0, 1 in
  `google.golang.org/protobuf` v1.28.1, 41 in the Go standard library of the scan toolchain.

Summary and recommendations: [research/0007](../../0007-go-node-security.md).
