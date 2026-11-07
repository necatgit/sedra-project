# 2026-11-07: Q35, why the Go and Rust pruning proofs differ

`q35-report-raw.md`: raw report (unedited) of a code comparison of sedrad `4a1153d`, kaspad (Go) and sedra-rusty
`dev` (rusty-kaspa v1.0.1 with Sedra changes). Read only; no node was run.

**Answer.** The two builders measure "2M blocks deep" over different sets of blocks:

- **sedrad (Go)** chooses each level's root with blue scores computed over the node's whole DAG at that level
  (`pruningproofmanager.go:290-316`, `blockAtDepth`) and ships the blocks from that root to the tip. Its validation does
  not reject a level whose selected tip has less than 2M blue score; it only leaves that level out of the "which proof
  is stronger" comparison (`pruningproofmanager.go:486`). **Verified** (re-checked by hand), and identical to Kaspa's
  Go node: inherited, not a Sedra change.
- **The Rust node** recomputes GHOSTDAG inside the shipped blocks only and moves the root deeper until the tip has at
  least 2M blue score there. Its code explicitly accepts proofs from "older nodes without a safety margin"
  (`build.rs:313-321`). **Verified** (re-checked by hand).
- Level 13 of the Go proof: blocks next to the root count as blue in the Go node's full DAG but are not in the proof, so
  inside the proof the tip ends up at 1998 instead of 2000. **Inferred**, consistent with the numbers.
- The 14 warnings "Locally built proof for level N does not match" come only from the Rust node's sanity check, which
  then validates its own rebuilt proof and continues. Harmless.

**Security.** Low. A Rust node without upstream check `48b63582` accepts the same proofs the all-Go network accepts
today. The check matters most against heavily shortened levels, which a fresh node cannot otherwise detect.

**Decision.** Keep `48b63582` out of `dev` while Go nodes serve proofs (as done). Possible later: a tolerant version
(reject only if the tip is clearly below 2M, e.g. by more than K = 18 or 100 blocks), tested offline against saved
sedrad proofs, and the full rule once no Go nodes are left. Not tested yet: a Go node syncing from a Rust node
(expected to work, Inferred).
