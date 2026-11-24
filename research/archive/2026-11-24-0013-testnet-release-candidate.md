# 2026-11-24: testnet release candidate 0.2.0-testnet.1 (#13), raw evidence

Unedited record of the checks for the release candidate. Commands ran in WSL Ubuntu 24.04 (`~/repos/sedra-rusty`) and
on sedra-dev (Ubuntu 26.04 VM), 2026-11-24 between 12:30 and 14:05 UTC+1.

## Branch

```
$ git merge-base --is-ancestor origin/<b> origin/testnet-kit   (before the release branch)
main: NO (2d3f8787 Release sedra-rusty 0.1.1, d20f07be Release sedra-rusty 0.1.0 missing)
dev: yes
m10-auxpow: yes
$ git diff --stat origin/dev origin/main
 AGENTS.md | 2 +-
 SEDRA.md  | 2 +-
```

Release branch `release-0.2.0-testnet.1`: `582be8a5` (testnet-kit) -> `124e3bba` merge of `origin/main` (no
conflict; `git diff 124e3bba^1 124e3bba` empty, tree unchanged) -> `24511407` release commit (8 files, +165 -10).
Pushed to GitHub 2026-11-24 (branch only; `git ls-remote origin 'refs/tags/sedra-v0.2*'` = 0 lines).

## Tests (full suite, `cargo test --release --no-fail-fast --workspace --exclude kaspa-wasm --exclude kaspa-wallet-pskt`)

```
WSL (Ubuntu 24.04, rustc 1.99.1), tree of 24511407:  112 suites, 566 passed, 0 failed, 25 ignored; exit 0
sedra-dev: /data/logs/sedra-rusty-v0.2.0-testnet.1-rc-20261124T124630Z.log:
== v0.2.0-testnet.1-rc 2026-11-24T12:46:30Z 2451140 | Ubuntu 26.04.1 LTS | rustc 1.99.1 (58cf8f9c3 2026-10-13) | 6 cpus
112 suites, 566 passed, 0 failed, 25 ignored
build exit: 0 (116s)
test exit: 0 (518s)
test processes::sedra_auxpow_consensus_test::sedra_auxpow_ban_boundary_test ... ok
test processes::sedra_auxpow_consensus_test::sedra_auxpow_testnet_release_activation_test ... ok
test processes::sedra_auxpow_consensus_test::sedra_auxpow_activation_boundary_test ... ok
test kaspad_env::tests::testnet_releases_are_recognised ... ok
test args::sedra_aux_pow_flag_tests::testnet_release_refuses_mainnet ... ok
```

A first version of `sedra_auxpow_activation_boundary_test` asserted that the first block on genesis has a DAA score
above 0; it failed (the test builder gives it 0). The test now asserts 0 and checks the boundary there (activation 1:
proof ignored; activation 0: accepted).

## Reproducible build (`contrib/reproducible/build-in-docker.sh`, fresh clone, detached HEAD at 24511407)

```
WSL, Podman 4.9.3:      build exit 0 (330s)
sedra-dev, Podman 5.7.0: build exit 0 (308s)   (systemd-run --user --scope -p MemoryMax=8G nice -n 19 ionice -c3)
both dist/SHA256SUMS:
a32f8cd9e475dbe5982c1ce627108891b70400ef62bbb5d27f9eb2794dc46793  sedra-rusty-0.2.0-testnet.1-linux-amd64.tar.gz
c0e0d23d913496cded1feba2374d7e42d147fced6b0be030fe19cb015244290b  sedra-rusty-0.2.0-testnet.1-linux-amd64/kaspad
$ diff SHA256SUMS SHA256SUMS.sedra-dev && echo IDENTICAL
IDENTICAL
BUILDINFO: sedra-rusty 0.2.0-testnet.1 / commit 24511407f15734d2b7b0daa0403f3b1edd4e1ed4 / rustc rustc 1.99.1 (58cf8f9c3 2026-10-13)
```

## The built binary

```
$ kaspad >/dev/null; echo "mainnet exit $?"
error: this is the testnet release 0.2.0-testnet.1 of sedra-rusty: it runs only with --testnet (or --devnet, --simnet). For Sedra mainnet use a mainnet release (tag sedra-vX.Y.Z without "-testnet").
mainnet exit 1
$ kaspad --version
kaspad 0.2.0-testnet.1 (rusty-kaspa v1.0.1, commit 24511407f157)
$ timeout 5 kaspad --testnet --appdir=/tmp/tn-probe --nogrpc --listen=127.0.0.1:22999 --nodnsseed --disable-upnp
[INFO ] kaspad v1.0.1-24511407f157 (sedra-rusty 0.2.0-testnet.1)
[INFO ] Data directory: /tmp/tn-probe/sedra-testnet-10/datadir
```

sedra-dev services after the runs: `sedra-rusty` active, `sedrad-dev` active.
