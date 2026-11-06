# M1 evidence (2026-11-05)

Milestone M1 (#20): Sedra's network on rusty-kaspa v1.0.1. Code: `necatgit/sedra-rusty`, branch `dev`, commit `7fa343ab`.

| File | What it is |
|---|---|
| `apply_m1.py` | The script that applied the parameter changes (genesis, names, prefixes, ports, seeders, subsidy table, activation, P2P v5) |
| `go_addrvectors.go` | Go program (sedrad v2.0.0) that produced the Sedra address test vectors |
| `go_reencode.go`, `address-reencode-map.txt` | Go program (sedrad's bech32) that re-encodes the Kaspa addresses in rusty-kaspa's tests, and its output. The map was regenerated after the commit from the unmodified test files on `main` (350 valid addresses; the intentionally invalid strings of the address error tests are excluded). Every Sedra address in it appears in the committed code, and no Kaspa address is left |
| `test-baseline-v1.0.1.log` | Full test run of unmodified rusty-kaspa v1.0.1: 112 suites, 498 passed, 1 failed, 25 ignored |
| `test-m1-final.log` | Full test run with M1: 112 suites, 499 passed, 1 failed, 25 ignored |

The failure in both runs is `kaspa-perf-monitor::monitor_works`, a timing-dependent test. Test changes and the reasons
for them are listed in `SEDRA.md` in the code repository.

## Second environment (2026-11-06)

| File | What it is |
|---|---|
| `test-vm-run1-build-failed-gcc15.log` | First run on the test VM (Ubuntu 26.04, GCC 15): the build failed in RocksDB 8.10 (`uint64_t` without `<cstdint>`) |
| `test-vm-cargo-config.log` | Test VM with `.cargo/config.toml` (sedra-rusty `e481e23f`, CXXFLAGS unset in the environment): 112 suites, 500 passed, 0 failed, 25 ignored |
| `test-wsl-cargo-config.log` | WSL (Ubuntu 24.04, GCC 13) with the same commit: 112 suites, 499 passed, 1 failed (`monitor_works`), 25 ignored |
| `run-tests.sh` | The script that runs every full build and test on the test VM |

Per suite, the two environments differ only in `kaspa-perf-monitor::monitor_works`, a timing test that passes on the
VM and fails under load in WSL.
