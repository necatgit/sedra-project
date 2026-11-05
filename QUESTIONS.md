# Questions and answers

Every open question the project depends on, who it was put to, and the answer with its source. Questions are never
deleted: answered ones stay for the record, and dropped ones say why.

Status: **Open** · **Asked** (sent to someone, waiting) · **Answered** · **Dropped**

| # | Question | Raised | Asked whom / when | Status | Answer and source |
|---|---|---|---|---|---|
| Q1 | Can one Kaspa block carry merged-mining commitments for both ZKas and Sedra? | 2026-11-05 (#3) | — (research) | Answered | Yes, but only just: ~145 bytes free, two 68-byte commitments leave ~9 bytes for the pool tag, a third never fits. [research/0002](research/0002-zkas-auxpow.md) |
| Q2 | Should AuxPoW be added to the Go node, or should Sedra move to the Rust codebase? | 2026-11-05 (#4) | — (research + decision) | Answered | Rust, based on rusty-kaspa v1.0.1, in two steps; decided by Nec on 2026-11-05. [research/0004](research/0004-rust-path.md) |
| Q3 | Does the Sedra owner support the merged-mining fork, and where should development happen? | 2026-11-05 | Sedra owner, 2026-11-05 (direct message) | Asked | Acknowledged 2026-11-05: "Got it, I check later and give a response" |
| Q4 | Questions about the v2.0.0 relaunch: treasury script and keys, treasury outflows, circulating supply vs published emission, mainnet build provenance | 2026-11-05 (#1) | Sedra owner, 2026-11-05 (direct message) | Asked | |
