# 2026-11-05: Project start

The project repository is set up. The goal is a hard fork that lets Sedra be merged-mined with Kaspa, using the
same approach as ZKas.

Current state of the network, checked against the public node:

- Mainnet runs `2.0.0-relaunch`. Its code is on the `relaunch/v2.0.0` branch of `sedracoin/sedrad`, not on `main`.
- That release introduced a difficulty reset and a foundation treasury allocation, both already active.

Next: review that release in detail, study the ZKas merged-mining design, and decide how to implement it in Sedra.
