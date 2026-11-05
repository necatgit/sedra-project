# SIP-0001: Merged mining of Sedra with Kaspa

| | |
|---|---|
| Status | Draft (skeleton, waiting for the Phase 0 research) |
| Author | Nec |
| Created | 2026-11-05 |
| Type | Consensus (hard fork) |

## Summary

Allow Sedra blocks to be accepted either by their native proof-of-work or by an AuxPoW proof: a Kaspa block whose
coinbase commits to the Sedra block hash and whose work meets Sedra's target.

## Motivation

To be written. Main points: Sedra's low hashrate share, security against majority attacks, miner incentives.

## Specification

To be written after the feasibility study:

- AuxPoW proof format and commitment in the Kaspa coinbase
- Coexistence with ZKas commitments in the same Kaspa block
- Validation rules and target check
- Activation point (DAA score)

## Backwards compatibility

This is a hard fork. Nodes that do not upgrade will reject merged-mined blocks after activation and end up on a
separate chain. Every node operator, pool, exchange and explorer must upgrade before the activation point.

## Unchanged

Emission schedule, total supply, block rate, addresses and transaction format.

## Security considerations

To be written: difficulty behaviour when merged hashrate joins or leaves, replay of parent proofs, and validation
cost.

## Reference implementation

None yet.
