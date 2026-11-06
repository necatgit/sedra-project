# M5 and M7 evidence (2026-11-06)

**Setup.** The local Go node on the test VM (sedrad v2.0.0) runs on a copy of the database of a long-running Sedra
node (copied with rsync while it ran, read-only, no proof request to that node). It has the complete DAA window for
pruning point `a990faed…` (2641 of 2641). The Rust node (sedra-rusty `b8182ca8`, with the security back-ports)
starts with an empty database and connects only to that local Go node.

**M5 (#24), full sync:** started 17:11:52 UTC, proof received 17:12:10 (75,884 headers, 24,479 unique), trusted data
accepted (no "DAA window data" error), synced at 17:19 UTC: Rust and Go at the same virtual DAA score 61,212,190.
One-hour follow check 17:20-18:20 UTC (`m5-follow.log`): 120 of 120 checks at 30 s intervals with the Rust node at
exactly the Go node's virtual DAA score (maximum difference 0), always synced, service always active.

**M7 (#26), state parity** (`m7-comparison.txt`, two samples): same tip, same pruning point, same UTXO commitment in
the same block, identical circulating supply (26,690,835,727.40495147 SDR at DAA 61,212,260), and identical balances
and UTXO counts for the treasury address and two of its recipients. The Rust node accepts a chain block only if the
UTXO commitment (MuHash) it computed itself equals the header's, so identical commitments mean identical UTXO sets.
The supply also independently confirms the figure behind Q14 (research 0001).

**Q35 (proof warnings):** 14 warnings "Locally built proof for level N does not match the applied one", for levels
0-13, once per proof application. The first attempt (incomplete window) had 154 = 11 applications × 14, so the
incomplete window was not the cause. The applied proof is valid (identical end state); only the Rust node's own
rebuild of the lower levels differs from the Go node's. Cause still open.

| File | Content |
|---|---|
| `rust-sync-log.txt` | Key lines of the Rust node's log, all its warnings, the systemd unit and the binary used |
| `m7-comparison.txt` | Supply, balances and UTXO counts on both nodes |
| `m5-follow.log` | The one-hour follow check |
