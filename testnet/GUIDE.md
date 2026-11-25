# Sedra public testnet: participant guide

| | |
|---|---|
| Status | **Not launched.** This guide is prepared in advance (2026-11-20; release candidate `0.2.0-testnet.1` prepared 2026-11-24, not published). The launch waits for the Sedra team's agreement on the testnet's duration and pass criteria (Q51) and on which test chain to use (Q52). Values marked `<at launch>` are filled in then |
| Process | [SIP-0003](../proposals/SIP-0003-public-testnet.md): what the testnet must show. [SIP-0001](../proposals/SIP-0001-merged-mining.md): the merged-mining rules being tested |
| Questions, problems | GitHub issue in this repository, template "Testnet report" (section 8) |

The testnet is a separate network where merged mining of Sedra with Kaspa runs in public before anyone decides about
mainnet. You can run a node, mine natively or merged, use the wallet, and report what you see. **Testnet coins have no
value and never will.** Never use a mainnet wallet, key or address on the testnet.

## 1. The network at a glance

| | Value |
|---|---|
| Network name | `sedra-testnet-10` (the testnet already in Sedra's Go and Rust nodes) |
| Addresses | `sedratest:...` |
| Ports | P2P **22211**, gRPC 22210 (keep RPC on localhost) |
| Genesis hash | `f896a3034873be1739fc4359236899fd3d65d2bc94f9780df0d0da3eb1cc4370` |
| Block rate, rewards, finality | as on mainnet (1 block per second, finality depth 86,400) |
| Parent chain for merged mining | Kaspa testnet-10 (`kaspatest:` addresses) |
| Seed nodes | `<at launch>` (no DNS seeders; you add them with `--addpeer`) |
| Merged-mining activation | DAA score **345,600** (about 4 days after launch), built into the release |
| Self-parent ban start | DAA score **172,800** = activation - 172,800 (about 2 days after launch) |
| Node release | sedra-rusty `sedra-v0.2.0-testnet.1` (release candidate prepared 2026-11-24, **not published yet**) |

The testnet cannot connect to Sedra mainnet or to Kaspa's networks: it has its own network name, genesis, ports and
address prefix, and nodes reject a peer from another network in the handshake.

### Phases

1. **Native phase** (launch to activation, about 4 days): normal Sedra mining. Old Go nodes (sedrad v2.0.0) follow.
2. **Ban start** (about day 2): from here a Sedra block whose own coinbase carries a merged-mining commitment (`SDM1`)
   is invalid for the new node (SIP-0001 §4.5). Old nodes do not know this rule.
3. **Activation** (about day 4): blocks proven by a Kaspa testnet-10 parent (merged-mined) become valid. Native mining
   continues. Old nodes reject the first merged-mined block and fall behind; that is expected and is one of the things
   the testnet shows.
4. **At least two weeks after activation** of running, then a public report against SIP-0003's criteria.

## 2. What you need

- Linux x86-64 (tested: Ubuntu 24.04 and 26.04). Other systems: build from source and tell us how it went.
- About 2 CPU cores, 4 GB RAM, 20 GB disk for a node (**Inferred** from mainnet's Rust node; the testnet starts
  empty and grows by about one block per second).
- For mining natively: any CPU (the miner below). For merged mining: a Kaspa miner (GPU or ASIC software that speaks
  Kaspa stratum) and a Kaspa testnet-10 address.

## 3. Get the node

**Download** (`<at launch>`): `sedra-rusty-0.2.0-testnet.1-linux-amd64.tar.gz` and `SHA256SUMS` from the sedra-rusty
pre-release `sedra-v0.2.0-testnet.1`. The node binary inside is `kaspad` (the binary name is still upstream's).
Verify before you run it:

```
sha256sum -c --ignore-missing SHA256SUMS          # the archive
tar xzf sedra-rusty-0.2.0-testnet.1-linux-amd64.tar.gz
sha256sum -c SHA256SUMS                           # now both lines: archive and kaspad
```

The tag `sedra-v0.2.0-testnet.1` is signed by Nec with the SSH key published on puddlepool.com, and its message
carries the same two checksums, so a good signature covers the checksums too:

```
git clone https://github.com/necatgit/sedra-rusty && cd sedra-rusty
curl -sO https://puddlepool.com/keys/allowed_signers
git -c gpg.ssh.allowedSignersFile=allowed_signers tag -v sedra-v0.2.0-testnet.1
```

The release is built reproducibly; you can rebuild it and compare checksums (sedra-rusty `docs/RELEASE.md`).

**Or build it:**

```
sudo apt install build-essential clang llvm libclang-dev pkg-config libssl-dev protobuf-compiler cmake git
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
git clone https://github.com/necatgit/sedra-rusty && cd sedra-rusty
git checkout sedra-v0.2.0-testnet.1          # once published
cargo build --release --bin kaspad
bash contrib/testnet/build_tools.sh          # sedra-testnet-miner and sedra-testnet-monitor
```

Check the version: `kaspad --version` must print `0.2.0-testnet.1 (rusty-kaspa v1.0.1, commit <12 hex digits>)`.
The testnet release refuses to start without `--testnet`: it cannot run as a mainnet node by accident. For Sedra
mainnet use a mainnet release (`sedra-v0.1.1`).

## 4. Run a node

```
./kaspad --testnet --utxoindex --disable-upnp --nodnsseed \
  --appdir=$HOME/sedra-testnet --rpclisten=127.0.0.1:22210 \
  --addpeer=<seed1>:22211 --addpeer=<seed2>:22211 --yes
```

- `--appdir` keeps testnet data apart from anything else you run.
- `--utxoindex` is needed for the wallet.
- If your machine is reachable from the internet, open TCP 22211 so others can connect to you. Never open 22210.
- As a service: `contrib/testnet/systemd/sedra-testnet-node.service` in sedra-rusty.
- Never use `--aux-pow-activation-override`: it changes the activation for your node only, and your node splits from
  the network. It exists for private dry runs.

**Is it working?** The log shows peers connecting and blocks being accepted. A quick snapshot:

```
./sedra-testnet-monitor --once --out /tmp/sedra-check --node me=grpc://127.0.0.1:22210
cat /tmp/sedra-check/nodes.csv
```

`network` must be `sedra-testnet-10`, `is_synced` 1, and `virtual_daa_score` close to what the seed nodes show.
The public status page, **https://testnet.puddlepool.com**, shows the seed nodes' DAA score, the phase, the countdowns
to the ban start and the activation, native and merged-mined blocks, the SIP-0003 pass criteria and the recent blocks
(`/status.json` for scripts). It is a TEST network page: the coins have no value.

## 5. Wallet

The wallet is Sedra's Go `sedrawallet` from sedrad v2.0.0 (unchanged; it works against the Rust node). Build it from
`https://github.com/sedracoin/sedrad` at tag v2.0.0 (`go build ./cmd/sedrawallet`), or use the binary from that
release.

```
sedrawallet create --testnet
sedrawallet start-daemon --testnet --rpcserver=127.0.0.1:22210 --listen=127.0.0.1:8182
sedrawallet new-address --testnet -d 127.0.0.1:8182
sedrawallet balance --testnet -d 127.0.0.1:8182
sedrawallet send --testnet -d 127.0.0.1:8182 -t sedratest:... -v 10
```

Mined coins can be spent after 100 confirmations (coinbase maturity, as on mainnet).

**No miner?** Ask for coins: open an issue with the template "Testnet report", type "faucet", and your `sedratest:`
address. The operator sends them by hand.

## 6. Mine natively (Sedra only)

```
./sedra-testnet-miner --rpc grpc://127.0.0.1:22210 --address sedratest:YOUR_ADDRESS
```

It uses all CPU threads (`--threads N` to limit). It refuses mainnet addresses and mainnet nodes. Sedra's Go
`sedraminer --testnet` (from sedrad v2.0.0) works the same way, pointed at your node's RPC.

Before activation, native mining is the only way to make blocks. After activation it keeps working next to merged
mining.

## 7. Mine merged (Kaspa testnet-10 and Sedra testnet at once)

Only after activation do merged-mined Sedra blocks count. Merged mining happens at a pool that works on Kaspa
testnet-10 templates carrying a Sedra commitment.

**At the testnet pool** (`<at launch>`: host and port, for example `stratum+tcp://<pool-host>:15555`):

- user: `kaspatest:YOUR_KASPA_TN10_ADDRESS.rig1`
- password: `a=sedratest:YOUR_SEDRA_TESTNET_ADDRESS`

Any Kaspa stratum miner works (kHeavyHash). The pool credits Kaspa testnet coins to the first address and Sedra
testnet coins to the second. Without the `a=` part your Sedra share is not paid to you.

**ZKas as well (since 2026-11-25).** The testnet pool also merges a private ZKas test chain (for the pool only; it
is not a public ZKas network, and its coins have no value either). To have ZKas test credits recorded for you, add a
ZKas test address to the **user name**, not the password: user `kaspatest:YOUR_KASPA_TN10_ADDRESS+zkastest:YOUR_ZKAS_TEST_ADDRESS.rig1`.
A `zkastest:` address in the password is ignored by the pool today. Without one, your share of ZKas blocks goes to
the pool's own ZKas test address. ZKas test addresses are shielded (they start with `zkastest:p`) and come from
zkas-walletd in testnet mode; since the ZKas test chain is private, most testers leave this out.

A Kaspa testnet-10 address comes from any Kaspa wallet in testnet mode (for example rusty-kaspa's `kaspa-wallet` with
`network testnet-10`).

**Your own pool:** run a Kaspa testnet-10 node (upstream rusty-kaspa, the version Kaspa runs on testnet-10;
`kaspad --testnet --netsuffix=10 --utxoindex`), a Sedra testnet node, and Miningcore from branch
`sedra-merged-mining`, starting from `contrib/testnet/pool/miningcore-testnet.json` in sedra-rusty. Two settings
matter most:

- `genesisHash` of the Sedra entry must be the testnet genesis above. Without it Miningcore commits to the mainnet
  genesis and every Sedra block is rejected.
- Use your own database and wallets, never a production pool's.

## 8. Report what you see

Open an issue in this repository with the template **"Testnet report"**. Useful in every report:

- what you ran: node release (`kaspad --version`), OS, miner and pool;
- what you expected and what happened, with UTC times;
- block hashes or DAA scores involved;
- the relevant log lines (remove IP addresses you don't want public).

Reports of things that worked are useful too: criterion 7 of SIP-0003 asks for at least one participant outside this
project.

Security problems in the node: report them privately as described in sedra-rusty `SECURITY.md`, not as a public issue.

## 9. Old-node test (optional)

To see what happens to a node that did not upgrade, run unchanged Go sedrad v2.0.0 on the testnet next to your node,
on its own ports:

```
sedrad --testnet --appdir=$HOME/sedrad-testnet --nodnsseed --listen=127.0.0.1:22231 --rpclisten=127.0.0.1:22230 \
  --connect=127.0.0.1:22211
```

Predicted (**Inferred** from SIP-0001 §7): it follows the chain before activation, and stops following at the first
merged-mined block. If you see anything else, report it.

## What this does NOT mean

- The testnet is not launched yet, and no launch date is set. It starts after the Sedra team agrees (Q51, Q52).
- Passing the testnet does not schedule merged mining on mainnet. A mainnet date is chosen with the Sedra team after
  the testnet report, if at all.
- Taking part does not mean you or anyone else supports SIP-0001.
- Testnet coins have no value, now or later. There is no reward, airdrop or allocation for taking part.
