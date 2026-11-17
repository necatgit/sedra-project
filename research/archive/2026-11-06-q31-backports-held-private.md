# Q31 raw report: held privately

The unedited raw report for Q31 (`2026-11-06-q31-backports-raw.md`, written 2026-11-06) is **not published**. It
was moved out of this repository on 2026-11-17, before the repository went public, and is kept unchanged in Nec's
private records (SHA-256 `dcc408714dc8ce09b7a9db4bf2cae7fd17ce68438045c8a58f0a3566a7d32fe8`).

## Why

The report explains, for each crash bug in rusty-kaspa v1.0.1, which peer- or RPC-supplied value triggers it, and it
lists fixes that upstream made without mentioning them in any release notes (checked 2026-11-17: rusty-kaspa has no
published security advisories, and the v2.0.1 notes do not mention the mempool or storage-mass fixes). Sedra's Rust node
has all these fixes (sedra-rusty `sedra-v0.1.1`, see `SEDRA.md` there), but other networks may still run unpatched
v1.0.1 code. Collecting the trigger details in one public document would help someone attack those nodes.

## What is public

- [research/0006](../0006-security-backports.md): every finding by area and upstream commit, with priorities and status.
- The fixes and their regression tests, in sedra-rusty (public) and in the evidence folders
  [2026-11-06-security-backports/](2026-11-06-security-backports/README.md),
  [2026-11-06-hardening/](2026-11-06-hardening/README.md),
  [2026-11-06-proof-checks/](2026-11-06-proof-checks/README.md) and
  [2026-11-07-optional-backports/](2026-11-07-optional-backports/mutation-and-suite.txt).

## When it will be published

It will be reviewed again on **2027-05-17**, or earlier if no network is known to run unpatched rusty-kaspa v1.0.1 code
any more. It will then be published unchanged, or with a dated note saying why it is still held.

## What this does NOT mean

- It does not mean the Sedra Rust node is vulnerable: the fixes are in v0.1.1, each with a test that fails on the
  original code.
- It does not affect Sedra mainnet, which runs the Go node (see research/0007 for that node).
- Nothing in research/0006 was changed by this. Its conclusions still rest on the full report, which is now held privately.
