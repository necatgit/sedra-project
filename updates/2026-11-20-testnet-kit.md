# 2026-11-20: The public testnet kit is ready; the launch waits for the Sedra team

The public testnet with merged mining ([SIP-0003](../proposals/SIP-0003-public-testnet.md), #13) cannot start before
the Sedra team agrees on its duration and pass criteria (Q51) and on the test chain (Q52; they promised an answer by
2026-12-14). Everything that does not depend on that answer is now prepared, so the testnet can start soon after.

## What is ready

- **For participants:** [testnet/GUIDE.md](../testnet/GUIDE.md): get and verify the node, run it, use the wallet,
  mine natively or merged, report problems (new issue template "Testnet report").
- **For the operator:** [testnet/RUNBOOK.md](../testnet/RUNBOOK.md): go/no-go checks, infrastructure, launch, the daily
  routine, how each of SIP-0003's eight criteria is measured, problems and resets, ending.
- **The report:** [testnet/PASS-REPORT-TEMPLATE.md](../testnet/PASS-REPORT-TEMPLATE.md), one section per criterion.
- **Code** (sedra-rusty, branch `testnet-kit`): the activation switch for dry runs, test vectors from 20 real Kaspa
  testnet-10 blocks (Kaspa's public testnet is the parent network; its blocks hash exactly as Kaspa reports), a CPU
  miner, a monitor that tells merged-mined from native blocks and checks that all nodes have the same chain, a faucet
  script, service files and the pool configuration. Full test suite: 561 passed, 0 failed.

## The dry run

On the test machine, closed off from the network, the whole kit ran once with a short timeline
([evidence](../research/archive/2026-11-20-0013-testnet-dryrun.md)): merged mining started at exactly the set block
score, merged-mined and native blocks were accepted side by side, the upgraded nodes always agreed, the unchanged Go
node followed until the first merged-mined block and then dropped off as predicted, a block breaking the self-parent
rule was rejected, a fresh node synced, and the wallet and faucet worked.

It also found four things that would have gone wrong in public, all fixed in the kit before anyone else ran it. The
most important: the pool software would have committed to the mainnet genesis unless told otherwise, which would have
made every merged-mined testnet block invalid.

## Not done yet

- Pool payouts were not part of the dry run; how the pool pays Kaspa testnet coins is still open.
- Where the seed nodes and the testnet pool run is decided at launch.
- Only a public run can show the rest: Kaspa's real testnet as the parent, outside participants, two weeks of running.

## What this does NOT mean

- No launch date is set. The testnet starts only after the Sedra team agrees (Q51, Q52).
- A ready kit and a passed dry run say nothing about whether the public testnet will pass.
- Nothing here schedules merged mining on mainnet.
