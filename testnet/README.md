# Public testnet kit (#13)

The kit for the merged-mining testnet of [SIP-0003](../proposals/SIP-0003-public-testnet.md). The Sedra team agreed
in writing on 2026-11-24 to its duration and pass criteria (Q51) on a fresh chain (Q52 no longer a condition); the node release [`sedra-v0.2.0-testnet.1`](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.2.0-testnet.1)
is published as a pre-release, the rehearsal on the real hosts passed ([REHEARSAL.md](REHEARSAL.md)), and the public
status page is <https://testnet.puddlepool.com>. **Running since Fri 2026-11-27 10:00 UTC** ([start report](../updates/2026-11-27-testnet-chain-started.md)); merged mining about Tue 2026-12-01, the start day the Sedra team announced on 2026-11-26 (confirmed on [#13](https://github.com/necatgit/sedra-project/issues/13#issuecomment-7192048626))
([OVERVIEW.md](OVERVIEW.md) D4).

| File | For |
|---|---|
| [EXPLAINER.md](EXPLAINER.md) | Community and holders: why we test and what, in plain words (also shown on the status page) |
| [OVERVIEW.md](OVERVIEW.md) | Everyone: what runs, how blocks are found, the decision points and the step-by-step plan per stakeholder |
| [REHEARSAL.md](REHEARSAL.md) | The rehearsal on the real hosts before launch (run and passed 2026-11-25, moved forward from 11-30), and seed2's install |
| [GUIDE.md](GUIDE.md) | Participants: get and verify the node, run it, wallet, native and merged mining, reporting |
| [RUNBOOK.md](RUNBOOK.md) | The operator: go/no-go checks, infrastructure, launch, daily routine, how each criterion is measured, problems, reset, ending |
| [HOSTING.md](HOSTING.md) | Where it runs (decision D3): requirements per role, VPS offers compared 2026-11-24, recommendation |
| [PASS-REPORT-TEMPLATE.md](PASS-REPORT-TEMPLATE.md) | The dated report, one section per SIP-0003 §3 criterion |
| [DESIGN.md](DESIGN.md) | Gaps between the local end-to-end harness and a public testnet, and the design chosen (approved by Nec 2026-11-20) |
| [`.github/ISSUE_TEMPLATE/testnet-report.md`](../.github/ISSUE_TEMPLATE/testnet-report.md) | Reports and faucet requests |

Code, configs and scripts are in sedra-rusty, branch `testnet-kit`, directory `contrib/testnet/`: the native CPU
miner, the monitor and its summary script, the faucet script, systemd units, the testnet Miningcore config and the
dry-run scripts. The dry run of 2026-11-20 is in
[research/archive/2026-11-20-0013-testnet-dryrun.md](../research/archive/2026-11-20-0013-testnet-dryrun.md).
