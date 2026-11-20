# Kaspa testnet-10 payouts: Go kaspawallet against kaspad 2.1.0, 2026-11-20 (#13)

Evidence record for criterion 5 of SIP-0003 (the testnet pool pays Kaspa testnet coins). Approved by Nec 2026-11-20
(build of the upstream wallet). Labels: **Verified**, **Inferred**, **Unknown**.

## Question

Miningcore pays KAS only through the gRPC service `kaspawalletd.kaspawalletd`: `GetBalance`, then `Send` with the
wallet password, `useExistingChangeAddress = true`, `isSendAll = false` (`KaspaPayoutHandler.cs`, Miningcore
`57944adc`, lines 630 and 696-703). Does a wallet daemon that serves this work against the Kaspa node testnet-10 runs?

## Setup (WSL, loopback only)

| | |
|---|---|
| Wallet | Go `kaspawallet` from kaspanet/kaspad tag **v0.12.23** (`f6876d5`, 2026-06-05 "Increase wallet min fee rate"), built with Go 1.23.12; `kaspawallet version` → `0.12.23`; binary SHA256 `999163119ff2026a…` |
| Node | upstream rusty-kaspa kaspad **2.1.0** (`4863866f`), the version Kaspa's public testnet-10 runs (api-tn10.kaspa.org, 2026-11-19) |
| Chain | private testnet-10 chain from genesis, two nodes on loopback, no DNS seeding, `--override-params-file` with `{"crescendo_activation": 0}` so Crescendo rules (10 blocks/s parameters, coinbase maturity 1,000 blocks) apply from genesis as on the live testnet-10. kaspad parses the file strictly (a test file with an unknown field is refused: `unknown field bogus`) and applies the value (`params.rs:539`, `daemon.rs:316-330` of 2.1.0) |
| Client | a 60-line Go program calling the daemon's `GetBalance` and `Send` with the same fields as Miningcore (adapted from `contrib/e2e-merged-mining/walletcheck` in sedra-rusty) |
| Steps | `kaspawallet create --testnet`, `start-daemon --testnet --rpcserver=127.0.0.1:16210`, two addresses; 1,150 blocks mined to address 1; Send 10 KAS to an outside address, Send 5 KAS to address 2; 20 more blocks; balances |

## Result (Verified)

```
balance available=7400000000000 pending=50050000000000 sompi        (74,000 KAS mature after 1,150 blocks)
Send 10 KAS to outside address   -> sent txids: [9f7cf42d25a263023c13f189a7ba6d0db079d4779d4c993b97c2cb66be583699]
Send 5 KAS to the second address -> sent txids: [2a1dd91082aa499cb298c64806c0f2cc9f2bf80e271c08c0c6ddba111f728217]
after 20 more blocks: available=8398999364800 sompi
kaspatest:qz56pc…52srp65 (change)    1984.99364800
kaspatest:qq30ez…c2u (mining)       82000.00000000   500500.00635200 (pending)
kaspatest:qqz9ea…w26 (second)           5.00000000
Total balance, KAS                  83989.99364800
```

- Both transactions were accepted and mined: the second address holds 5 KAS, and the available balance equals
  74,000 + 20 x 500 - 10 - 0.006352 (two fees) = 83,989.993648 KAS.
- Maturity: 74,000 KAS available after 1,150 blocks = about 148 blocks x 500, consistent with a coinbase maturity of
  1,000 blocks (Crescendo); the block reward on this chain is 500 KAS because a new chain is in the pre-deflationary
  phase.
- No error, reject or invalid line in the wallet daemon log.

## What this shows and what it does not

- The pairing production already uses on mainnet (Go `kaspawallet` daemon against a Rust kaspad) also works on
  testnet-10 rules with kaspad 2.1.0 and `--testnet`, through exactly the calls Miningcore makes. **Verified** on a
  private chain.
- Not run: Miningcore itself paying (its payout run with PPLNS accounting), the live public testnet-10 (other
  transactions, real fee market, a node synced to it), many inputs or batch payouts. Those belong to the public
  testnet (runbook criterion 5). **Inferred:** they behave the same, since the node software and rules are the same.
- Which wallet version the production Kaspa host runs is still not recorded (**Unknown**); v0.12.23 is the latest
  release and is what the testnet pool should use.

## What this does NOT mean

- It is not a pass of criterion 5; that needs the testnet pool paying real participants on the public testnet.
- It says nothing about Sedra payouts (sedrawallet, tested separately on 2026-11-10 and in the dry run).
