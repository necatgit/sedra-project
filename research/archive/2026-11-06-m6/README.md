# M6 evidence (2026-11-06)

Milestone M6 (#25): the two sedrad v2.0.0 relaunch rules in the Rust node. Code: `necatgit/sedra-rusty` `dev`, commit
`4873e9af` (rules and tests).

| File | What it is |
|---|---|
| `go_zz_relaunch_vectors_test.go`, `go_zz_coinbasemanager_export.go`, `go_zz_difficultymanager_export.go` | Generator, run temporarily inside sedrad v2.0.0: calls sedrad's real `applyDifficultyReset` and `treasuryAllocationOutput` with mainnet params (only the DAA score lookup stubbed). The two export files only make those unexported functions callable; they were removed after the run (sedrad working tree clean before and after) |
| `sedrad_relaunch_vectors.json` | Its output: 25 DAA scores one block before, at and after every window boundary, plus points inside, between and far outside |
| `apply_m6.py` | The script that applied the code changes |
| `test-vm-m6.log` | Full test run on the test VM: 112 suites, 507 passed, 0 failed, 25 ignored |

**Tests:** difficulty-reset parity with Go (25/25), treasury parity with Go (25/25, 8 paying), the full expected coinbase
(treasury output last, right value and script, only inside the windows), the rules dormant outside mainnet, and an
integration test in which the reset takes effect in the running consensus (block building and validation).

**Mutation checks:** reset one block late → fails at DAA 53,625,512; wrong window-2 amount → fails at DAA 53,633,267;
treasury output first instead of last → fails ("blue reward output first"); reset not applied in the running node →
fails at the first reset block.

**Note:** this ports the rules as sedrad applies them to the existing chain. It does not endorse the treasury
allocation; the open questions about it are in #19.
