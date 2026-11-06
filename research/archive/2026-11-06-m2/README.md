# M2 evidence (2026-11-06)

Milestone M2 (#21): block subsidy of the Rust node equals sedrad's. Code: `necatgit/sedra-rusty` `dev`, commit
`8aa3d981` (test and vectors), `d2c4f7e4` (SEDRA.md).

| File | What it is |
|---|---|
| `go_zz_subsidy_vectors_test.go` | Generator, run as a temporary Go test inside sedrad v2.0.0's `coinbasemanager` package. It calls sedrad's real `CalcBlockSubsidy` with mainnet params; only the DAA score lookup is stubbed. Removed again after the run (sedrad working tree clean before and after) |
| `sedrad_subsidy_vectors.json` | Its output: 813 DAA scores and subsidies (DAA 0-2, start of the deflationary phase, one block before/at/after every month boundary up to month 200, mid-month points, relaunch and current mainnet DAA scores, far beyond the table) |
| `test-vm-m2.log` | Full test run on the test VM with M2: 112 suites, 501 passed, 0 failed, 25 ignored |

Result: `calc_block_subsidy` and `legacy_calc_block_subsidy` match all 813 values. Mutation check: changing the month-98
table entry by 1 seep (62259853 → 62259854) makes the test fail at DAA score 273,240,000, the first block of month 98.

Reproduce the vectors: copy the generator into `domain/consensus/processes/coinbasemanager/` of sedrad at `4a1153d`, run
`SUBSIDY_VECTORS_OUT=out.json go test ./domain/consensus/processes/coinbasemanager -run TestZZSubsidyVectors`.
