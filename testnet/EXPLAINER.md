# The Sedra testnet in plain words

| | |
|---|---|
| For | Community members and holders who want to know why there is a testnet and what it checks, without the technical details |
| Shown on | https://testnet.puddlepool.com ("What is this?"), same text |
| Details | [GUIDE.md](GUIDE.md) (taking part), [OVERVIEW.md](OVERVIEW.md) (who runs what, dates), [SIP-0003](../proposals/SIP-0003-public-testnet.md) (why and the pass criteria), [SIP-0001](../proposals/SIP-0001-merged-mining.md) (the rules tested) |

This page explains; it decides nothing. Where it and the documents above differ, the documents are right.

## What is this?

A separate test network for Sedra, running since Friday 2026-11-27. Its coins are test coins: they have no value,
now or later, and there is no reward, airdrop or allocation for taking part. Nothing changes on Sedra mainnet: no
mainnet date is set, and supply, balances and rewards stay as they are. The testnet exists so that anyone can watch
the proposed merged-mining rules work, or fail, in public before anyone decides anything about mainnet.

## What is merged mining?

Sedra and Kaspa use the same kind of mining work. Today a miner has to choose one of the two. With merged mining, a
Kaspa miner's work can count for a Sedra block too, without extra hashing: the pool puts a small Sedra tag into the
Kaspa block it is working on, and when the work is good enough for Sedra, that Kaspa header is the proof. ZKas is
already merge-mined with Kaspa this way, so one share could count for up to three coins: KAS, SDR and ZKas.

Sedra gains the hashrate of every Kaspa miner whose pool chooses to merge-mine it. How much that is depends on how many
pools take part; at first it is one. Merged mining does not make Sedra "secured by Kaspa" as such: Sedra is as strong
as the hashrate that actually mines it. Normal (native) Sedra mining keeps working next to it.

## What is the self-parent ban?

A merged-mined Sedra block must be proven by a Kaspa block, its "parent". The ban stops a Sedra block from carrying a
Sedra merged-mining tag in its own reward transaction, so it cannot pose as the parent of another Sedra block. Without
the ban, one piece of work could be counted twice. It starts two days before merged mining opens, so that no block
mined just before the switch can be used that way just after it.

## The phases

The chain counts its progress with the DAA score, which grows by about one per second. The countdowns on the status
page show live estimates for each step.

1. **Native phase** (from the start on 2026-11-27): normal Sedra mining with CPUs.
2. **Ban start** at DAA score **172,800** (about 2026-11-29): the self-parent ban takes effect.
3. **Activation** at DAA score **345,600** (about 2026-12-01): merged-mined blocks become valid. Native mining goes on.
4. **At least two weeks** of running after activation.
5. **A public report**, criterion by criterion, with the evidence. Only if the testnet passes do the Sedra team and
   this project talk about a mainnet plan.

**The old Go node (`old-go`)** runs Sedra's current software, never upgraded. It should follow the chain until the
first merged-mined block and then stop. That shows what happens to any node that does not upgrade.

## What we check

1. The switch happens exactly at the announced score, and all upgraded nodes stay on one chain. The ban starts when
   written.
2. Merged-mined and normally mined blocks appear side by side, and every upgraded node accepts both.
3. A node that was not upgraded follows until the first merged-mined block and then stops, as predicted.
4. A brand-new node started after the switch can download and check the whole chain.
5. The pool pays both test coins (Kaspa testnet and Sedra testnet) to the right miners.
6. The Sedra wallet sends and receives test coins.
7. At least one person outside this project runs a node or mines and reports what they saw.
8. At least two weeks after the switch without the nodes disagreeing about the chain; every problem found is fixed
   and tested again.
9. *Proposed extra, not one of the eight the Sedra team accepted:* one Kaspa block carries both a Sedra and a ZKas
   tag; both chains accept their blocks, neither disturbs the other, and no share is paid twice. The ZKas side is a
   private test chain used only by the testnet pool.

## How to help

- **Run a node**: [GUIDE §4](GUIDE.md#4-run-a-node).
- **Mine**: until activation with a CPU, or one GPU at low intensity ([GUIDE §6, §7](GUIDE.md#6-mine-natively-sedra-only));
  after activation through the testnet pool. Please no Kaspa ASICs.
- **No miner?** Ask the faucet for test coins ([GUIDE §5](GUIDE.md#5-wallet)).
- **Tell us what you see**, good or bad: a "Testnet report" issue ([GUIDE §8](GUIDE.md#8-report-what-you-see));
  progress is posted on [#13](https://github.com/necatgit/sedra-project/issues/13).
