# 2026-11-06 (evening): The Rust node syncs Sedra mainnet and holds the same state

The Sedra Rust node has synced the live Sedra chain from a Go node and holds exactly the same state. On the way there,
the project fixed security problems in the Rust code it builds on and ran into a problem with Sedra's Go node that
operators should know about. Everything below links to its evidence.

## M5 and M7: full sync, identical state

- **M5 (#24):** the Rust node synced from a local Go node in 7.5 minutes and then followed the chain for one hour:
  120 of 120 checks at exactly the same block height (DAA score) as the Go node.
- **M7 (#26):** at the same block, both nodes have the same UTXO commitment, the same circulating supply
  (26,690,835,727.40495147 SDR, to the last unit) and the same balances and individual coins for the treasury
  address and two of its recipients. The Rust node only accepts a block if its own calculation of all balances matches
  the block, so this means it computes exactly what the Go node computes.
- The supply figure also confirms, from an independent implementation, the number behind one of the open questions
  to the Sedra team (QUESTIONS.md Q14): about 6.0 billion SDR more than the published code can explain.

Evidence: [research/archive/2026-11-06-m5-m7/](../research/archive/2026-11-06-m5-m7/README.md).

## How the sync was made to work

The first attempt failed because the public Sedra peers had given our Go node an incomplete set of the blocks needed
around the current pruning point (QUESTIONS.md Q5). The working solution was to copy the database of a long-running
Sedra node to the test machine, read-only and without stopping that node, which gave the local Go node the complete
data.

## An incident, and a warning for Sedra node operators

Before the database copy, we let the Rust node sync directly from the long-running node, which is the node behind
PuddlePool. Soon after it started syncing, that Go node stopped answering requests for about eight
minutes, until it was restarted, and stayed blocked even after our node had disconnected. For a pool this means no new
work for miners during that time. This was a mistake in the risk assessment, and it is documented as an incident.

**What it means for others:** if a Sedra Go node accepts connections from new peers, any node starting a sync from
it may freeze it in the same way. This is being investigated (Q37), and whether the Rust node behaves the same is open
(Q38). The project's rule is now: test nodes never connect to a production node.

Evidence: [research/archive/2026-11-06-m5-production-sync-incident/](../research/archive/2026-11-06-m5-production-sync-incident/README.md).

## Security fixes in the Rust code

The Rust code the node is built on (rusty-kaspa v1.0.1) has crash bugs that Kaspa fixed only in later releases. The
project went through all later Kaspa fixes ([research/0006](../research/0006-security-backports.md)) and carried over
the important ones, each with a test that fails without the fix:

- in use now: four crash or validation fixes (network handshake, transaction pool, addresses) and a crash during sync
  that the project's own monitoring would have triggered;
- ready, to be merged next: an update of external libraries that removes 18 of 28 known vulnerabilities (none of the
  remaining 10 is reachable from the network in the node as run), and three hardening changes (transaction pool,
  block size limit, limits on incoming connections).

## Also fixed or answered today

- Building on current Linux systems (GCC 15) failed; fixed with a build setting.
- Sedra's copies of its two cryptography libraries are identical to Kaspa's (Q28).
- An inherited bug in Sedra's Go node turned out to have no practical effect (Q36).
- A first full draft of the merged-mining proposal ([SIP-0001](../proposals/SIP-0001-merged-mining.md)) is out for
  review.
- All questions are now in one list, [QUESTIONS.md](../QUESTIONS.md): 38 so far, 13 of them with the Sedra team.

## Next

Merge the prepared security changes and test them on the synced node, check two remaining proof-validation rules
against real Sedra data, and start M9: seven days of the Rust node running next to Go nodes without diverging.

Time and AI effort per milestone: [TIMELINE.md](../TIMELINE.md).
