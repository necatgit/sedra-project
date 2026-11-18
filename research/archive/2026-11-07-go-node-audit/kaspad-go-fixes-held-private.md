# Go node audit raw report: held privately

The unedited raw report of the 2026-11-07 Go node audit (`kaspad-go-fixes-raw.md`) is **not published**. It was
moved out of this repository on 2026-11-18, before the repository went public, and is kept unchanged in Nec's private
records (SHA-256 `7cf8e282c9367b16d60ed267c3a8b410e924688c1957cc03daf15e6b88c1455e`). The same was done with one raw
log of the Q38 test (`2026-11-07-q38/bytes.log`, SHA-256
`0717e8e3e467e580ddb9fcee36a1e99d707872d58c307447468e61c66b28b73f`).

## Why

The 2026-11-09 security notice to the Sedra team promised a public write-up with the impact and the protection steps,
but without instructions for causing the problems. The raw report and the log contain detail about how the RPC freeze
of sedrad (Q37) arises, and related measurements. sedrad v2.0.0 has no fix yet, so this detail stays private.

At the same time, and for the same reason, the wording about how the freeze arises was shortened in the earlier
history of these files (removed lines only, no finding changed): `QUESTIONS.md` (Q37, Q38), the
[incident report](../2026-11-06-m5-production-sync-incident/README.md), the [Q38 test](../2026-11-07-q38/README.md),
[research/0007](../../0007-go-node-security.md), [SIP-0002](../../../proposals/SIP-0002-network-resilience.md) and the
update posts of 2026-11-06 and 2026-11-07. One commit message was shortened the same way.

## What is public

- [research/0007](../../0007-go-node-security.md): the findings of the audit (missing kaspad fixes by commit, the
  library vulnerabilities, the freeze being unfixed in Kaspa's Go node).
- [govulncheck-sedrad-v2.0.0.txt](govulncheck-sedrad-v2.0.0.txt): the full scan output.
- The [operator advisory](../../0007-sedrad-v2.0.0-advisory.md): impact, who is exposed, protection steps, status.

## When it will be published

When a sedrad release that fixes the RPC freeze has been out long enough for operators to update, or on
**2027-05-18** at the latest for a review. It will then be published unchanged, or with a dated note saying why it is
still held.

## What this does NOT mean

- No finding was changed or withdrawn: research/0007 and the advisory still say the same, and their conclusions still
  rest on the full report.
- It does not mean there is more bad news being hidden: the report's findings are all summarised in research/0007.
