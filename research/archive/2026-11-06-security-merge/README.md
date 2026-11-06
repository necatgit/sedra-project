# 2026-11-06: security changes merged into dev (#29)

Branches `deps-security` (`49e314f6`) and `hardening` (`4d2f8b91`) merged into `dev` of sedra-rusty without
conflicts as `36cf4cbf`, then a SEDRA.md note as `a9b230b5`.

Full build and test run of `36cf4cbf` on the test machine (`run-tests.log`, same script as M1):

- release build: exit 0 (83 s)
- tests: 112 suites, 517 passed, 0 failed, 25 ignored (exit 0, 346 s)

The 25 ignored tests are upstream's long-running tests, ignored in every run since M1.

**What this does NOT mean:** the merged code has not yet run against the live chain. The running test node still
uses `b8182ca8`; switching it to the merged build is the next step, before the seven-day run (M9).
