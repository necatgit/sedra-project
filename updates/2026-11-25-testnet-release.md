# 2026-11-25: Testnet go-ahead, rehearsal passed, node release published

Covers 2026-11-23 to 2026-11-25.

## The Sedra team said yes to the testnet

- On 2026-11-24 the Sedra team agreed in writing to run the public testnet under
  [SIP-0003](../proposals/SIP-0003-public-testnet.md) as it stands: at least two weeks after activation and the eight
  pass criteria, on a fresh chain (Q51 answered). A fresh chain started from the existing `testnet-10` genesis needs
  nobody's old data, so the question about the old test chain (Q52) no longer holds up the launch; it stays open as
  information.
- **Proposed start: Tuesday 2026-12-01. Not announced yet.** The Sedra team announces it if it wishes (Q48), with a text
  that says: test network only, no mainnet date, no change to supply.

## Hosts, release and rehearsal

- **Hosts** (decided 2026-11-24, [testnet/HOSTING.md](../testnet/HOSTING.md)): seed2 on a rented VPS in the EU,
  outside the home network; seed1 (which mines the first blocks), an unchanged Go node, the testnet pool, the monitor
  and a Kaspa testnet-10 node at home ([testnet/REHEARSAL.md](../testnet/REHEARSAL.md) §1).
- **Rehearsal on the real hosts, 2026-11-25** ([testnet/REHEARSAL.md](../testnet/REHEARSAL.md) §3.1): R1-R11 passed,
  then everything was wiped back to genesis. Two findings are written down there: the native miner does not reconnect
  by itself after a node restart, and a wiped node must not start while any node that held the old chain still runs
  (the wipe needed a second attempt for that reason).
- **Node release `sedra-v0.2.0-testnet.1`**: signed tag, identical rebuilds on two machines, refuses to start on
  mainnet; published as a [pre-release](https://github.com/necatgit/sedra-rusty/releases/tag/sedra-v0.2.0-testnet.1)
  on 2026-11-25 ([checklist](../release/v0.2.0-testnet.1-checklist.md)). Independent rebuilds are welcome in
  [necatgit/sedra-rusty#3](https://github.com/necatgit/sedra-rusty/issues/3).
- **Public status page:** <https://testnet.puddlepool.com> (paused during the rehearsal; it shows the testnet once it
  runs).

## ZKas in the same test, and two corrections

- **ZKas added** (decision D11, [testnet/OVERVIEW.md](../testnet/OVERVIEW.md)): the testnet pool also merges a private
  ZKas test chain under the same Kaspa testnet-10 parents, as the mainnet pool would. In the rehearsal a Kaspa
  testnet-10 block carried exactly one ZKas and one Sedra commitment within the 204-byte limit (R11). Proposed as an
  extra criterion 9 in SIP-0003; it is not part of the eight criteria the Sedra team accepted.
- **SIP-0001 corrected on 2026-11-25:** §9 said the 2026-11-10 end-to-end run included ZKas; it did not (Sedra only),
  which is why ZKas is now in the testnet. §6 said about 30 bytes remain for a pool's own tag when Kaspa, ZKas and Sedra
  are mined together; with the pool software used here it is about 24. Both corrections are dated in the SIP and in
  the [sedra-sips](https://github.com/necatgit/sedra-sips) copy.

## How the documents are kept

The working rules ([AGENTS.md](../AGENTS.md), "Keeping documentation current") now name one owning document for each
kind of fact (roadmap, issues, questions, SIPs, testnet folder, node changes). When a fact changes, every copy is fixed
in the same session, and a state change gets a short dated comment on its issue. A first sweep on 2026-11-25 brought
the testnet documents, the README and the SIP-0003 status line up to date with the team's yes and the rehearsal.

## Questions

All 65 questions: 24 answered, 31 asked and waiting, 6 open, 2 being investigated, 1 proposed, 1 split
([QUESTIONS.md](../QUESTIONS.md)). The answers promised in the Sedra team's 2026-11-23 working draft are due on
2026-11-30, 2026-12-07 and 2026-12-14.

## What this does NOT mean

- The testnet is not running and not announced. 2026-12-01 is a proposal.
- A passed rehearsal is not a pass of any SIP-0003 criterion.
- The Sedra team's yes covers the testnet only. Nothing about merged mining on mainnet (SIP-0001) is agreed, and no
  mainnet date is set.
