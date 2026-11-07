# Treasury address snapshot, 2026-11-07

Unedited raw data. Not reviewed; conclusions belong in a numbered research note and in [QUESTIONS.md](../../../QUESTIONS.md).

## What was queried

- Address: `sedra:pp8a4l47q0qjwlwgqvnmp5ppssk6zpn9hat58vaw6jkxkee2aqduue9252wc3`, the treasury defined in sedrad
  `domain/dagconfig/params.go` at tag `v2.0.0`. ScriptPublicKey `aa204fdafebe…1bce87` (P2SH).
- Node: the project's own test node (sedrad v2.0.0, `--utxoindex`), synced from the public network. The Rust test node
  running beside it reported the same balance (see below).
- Time: 2026-11-07 19:19 UTC, virtual DAA score ≈ 61,306,011.
- Command: `sedractl -s localhost:22110 GetUtxosByAddresses sedra:pp8a4l47q0qjwlwgqvnmp5ppssk6zpn9hat58vaw6jkxkee2aqduue9252wc3`
- Output: [getUtxosByAddresses-raw.json](getUtxosByAddresses-raw.json), SHA-256
  `53a5657d6951a5034c786bdc686da37f4fe6e67b9ff521f1a316c05669d35c82`.

## Raw result

- 43 unspent outputs, total **3,293,175,798,122,500 seep = 32,931,757.98122500 SDR**.
- All 43 have `isCoinbase: false` and output index 1. Block DAA scores range from 56,316,881 to 60,531,336.
- `GetBalanceByAddress` on the Go and Rust nodes, sampled at the same virtual DAA score, gives the same total at
  61,262,644 (07:20 UTC) and 61,284,362 (13:20 UTC).

## Labelled findings

- **Verified:** none of the treasury's coinbase outputs is still unspent at this address. (563 outputs, 163 × 10M +
  400 × 1M = 2.03B SDR, is the count given in the `v2.0.0` params comment and in Sedra's reply; we have not counted
  them on chain, see Q29.)
- **Verified:** the balance is unchanged from the 32.93M SDR recorded on 2026-11-05 (Q12).
- **Verified:** the treasury redeem script is a plain 2-of-3 multisig, `OP_2 <3 × 32-byte key> OP_3 OP_CHECKMULTISIG`,
  with no `OP_CHECKLOCKTIMEVERIFY`. Source: the signature script of input 0 of transaction
  `61f643bd11551e01566c1c9dacff4a392be424cb5ede6d7435a64041ab8926c3`, which spends a treasury output, from
  `https://api.sedracoin.com/transactions/61f643bd…26c3?inputs=true&outputs=true` (checked 2026-11-07).
  The same transaction pays 1 SDR to `sedra:qq770x…mmlj87` and returns 999,998.9998 SDR to the treasury.
- **Verified:** the public explorer API reports `{"total":16}` transactions for the address
  (`/addresses/<address>/transactions-count`, 2026-11-07), although the address has received at least 563 coinbase
  outputs plus the 43 outputs above.
- **Inferred:** the 43 index-1 outputs are change returned to the treasury by spending transactions, because the one
  transaction looked up has exactly that shape (payment at index 0, change at index 1). The other 42 were not looked up.
- **Unknown:** where the roughly 1.997B SDR that left the address went. Tracing it needs the spending transactions,
  which our pruned node no longer holds (an archival node, or the explorer API as an unverified cross-check).

## What this does NOT mean

- It does not show that funds were misused. Spending from a treasury can be legitimate; this snapshot only shows that
  it was spent and how much is left.
- It does not show who holds the keys or who signed the spends.
- The explorer cross-check comes from Sedra's own indexer, so it is not independent evidence.
