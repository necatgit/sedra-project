# Q35: Why the Go (sedrad) and Rust pruning point proofs differ

Date: 2026-11-07. Read-only code research. No node, host or repository was changed.

Sources:
- Go: `upstream/sedrad` at `4a1153d` (v2.0.0), `domain/consensus/processes/pruningproofmanager/pruningproofmanager.go` (referred to below as `ppm.go`).
- Go reference: `upstream/kaspad-go` HEAD `88bd6043`, same file.
- Rust: `sedra-rusty` branch `dev` (HEAD `9cb74efc`), `consensus/src/processes/pruning_proof/{build,validate}.rs`, `protocol/flows/src/v5/ibd/flow.rs`. Note: the WSL checkout is on branch `optional-backports`; everything below was read from `dev` via `git show dev:<path>`.
- Upstream commit `48b63582` (rusty-kaspa #822, 2026-01-15).

Labels: **[V]** Verified in code (file:line or commit), **[I]** Inferred, **[U]** Unknown.

---

## Short answer

The two builders measure "2M deep" in different coordinate systems.

- **Go** picks each level's root by walking the level's selected chain until the stored level blue score has dropped by more than 2M. Those stored blue scores come from GHOSTDAG run over the node's whole level DAG. Then it ships only `future(root) ∩ past(selectedTip)`.
- **Rust** (since rusty-kaspa #494, "On-demand calculation for Ghostdag for Higher Levels") recomputes GHOSTDAG for each level inside exactly that `future(root) ∩ past(tip)` subDAG. It moves the root deeper (in 10 % steps) until the tip's blue score *inside the proof* is >= 2M.

A validator only sees the proof, so it recomputes blue scores from the root. Level-L blocks that are in the root's anticone and were merged as blue after the root counted toward Go's depth. They are not in the proof, so the tip's in-proof blue score can come out slightly below 2M (1998 at level 13). Upstream 48b63582 checks exactly that in-proof value and rejects the proof.

So the difference comes from code Sedra inherited unchanged from Kaspa. It is not a Sedra change, and the Go side has no new bug. The Go proof is legitimately about 0.1 % "thinner" than the 2M target that the Rust validator now enforces. The security impact of accepting it is negligible: it equals the security of today's all-Go network, which never enforced the rule at all. My recommendation is to keep the strict check out. If you want the protection, use a tolerant variant (see section 5).

---

## 1. How each builder selects headers per level

### Go (sedrad = kaspad-go)
- **[V]** `ppm.go` is identical to kaspad-go apart from import paths (`git diff --no-index`: 18 import lines changed and a BOM, no logic change).
- **[V]** Selected tip per level: the pruning point if `level <= ppLevel`, else `ChooseSelectedParent` among the pruning point's level parents (`ppm.go:150-176`).
- **[V]** `blockAtDepth2M = blockAtDepth(ghostdagDataStores[level], tip, 2M)` (`ppm.go:179`). `blockAtDepth` walks selected parents while `blueScore >= tip.blueScore - depth` (`ppm.go:290-316`, `:299`). The returned block therefore has a *stored* blue score at least 2M+1 below the tip.
- **[V]** Root: `blockAtDepth2M`, or the block at depth M on level L+1 if that block is its ancestor, or else their common ancestor along the L+1 block's chain (`ppm.go:184-230`, `:197`, `:224`).
- **[V]** Headers: an up-heap BFS from the root over level-L children, keeping only ancestors of the tip (`ppm.go:232-276`). That is exactly `future(root) ∩ past(tip)`, with no extra margin.
- **[V]** The stored level-L GHOSTDAG data comes from normal block processing. `validateDifficulty` runs `ghostdagManagers[i].GHOSTDAG` for every level `1..blockLevel` of each incoming block (sedrad `blockvalidator/pruning_violation_proof_of_work_and_difficulty.go`, around lines 120-127). On a node that itself synced from a proof, levels start from that proof's GHOSTDAG (`ApplyPruningPointProof`, `ppm.go:837-933`, GHOSTDAG at `:900`). In both cases the blue scores cover the *full known level DAG*, including blocks outside `future(root)`.

### Rust (sedra-rusty dev = rusty-kaspa v1.0.1 lineage)
- **[V]** `build_pruning_point_proof` → `calc_gd_for_all_levels` → `find_sufficient_root` for each level, top-down (`build.rs:65-…, 176-210, 220-330`; file offsets from `git show dev:`).
- **[V]** The candidate root comes from `level_block_at_base_depth`, which uses **level-0 header blue scores**. The search starts at depth `2M + 100` (`build.rs:250`) and grows ×1.1 per try (`:325`). The root is chosen against the required block (depth M at L+1) with the same three-way rule as Go.
- **[V]** For every level > 0, GHOSTDAG is recomputed **inside** `future(root) ∩ past(tip)`, with the root given genesis GHOSTDAG data (`fill_level_proof_ghostdag_data`, `build.rs:333-…`, root insert at `:359`). The root is accepted only if `has_required_block && (root == genesis || in-proof blue_score(tip) >= 2M)` (`build.rs:304-305`). Otherwise the search goes deeper.
- **[V]** Fallback: if the headers run out (`is_last_level_header`) but the required block was found, the root is accepted anyway. The code comment names exactly this case: "syncing with an older node version that doesn't have a safety margin for the proof … the proof only contains about 2000 headers" (`build.rs:313-321`).
- **[V]** Level 0 returns immediately with the full DAG GHOSTDAG store and no in-proof check (`build.rs:287`). Its candidate depth (2M+100 at level 0) differs from Go's 2M.
- **[V]** In-proof blue score is also what validation uses. It recomputes GHOSTDAG over the proof headers with ORIGIN as the root parent (`validate.rs:222-226, 291`). Go validation does the same with VirtualGenesis (`ppm.go:400, 408`).

## 2. Why level 13 has blue score 1998, and why levels 0-13 differ while 14+ match

- **[V]** Go guarantees `stored_bs(tip) - stored_bs(root) >= 2M+1`, where stored means full-DAG GHOSTDAG (`ppm.go:299`).
- **[I]** Inside the proof the root becomes a genesis-like block. The tip's in-proof blue score only counts blues in `future(root) ∩ past(tip)`. Any level-13 block in `anticone(root) ∩ past(tip)` that the full DAG counted blue is missing, so it does not count. The 1998 vs at least 2001 gap implies at least 3 such blocks (±1 for root/origin indexing). Recolouring in the smaller DAG can only add blues, not remove them, so the gap is a net anticone loss. If the root is a blue block on the tip's selected chain, the k-cluster property bounds this loss by K = 18 (Sedra/Kaspa `defaultGHOSTDAGK = 18`, sedrad `domain/dagconfig/consensus_defaults.go:35`). If Go picked the L+1 block or a common ancestor off the level-L chain, the bound is less clean.
- **[V]** The cause is neither GHOSTDAG K nor trusted data, and not a plain off-by-one. Both sides use the same K. The trusted (anticone) data is level-0 only and plays no part in level-13 validation. The mismatch is in *which DAG the blue score is measured over*.
- **[I]** Why 14+ match: for each level the Rust search first tries a root no deeper than the required block (the L+1 block at depth M). At that point `root == required_block`, which is the same block Go picks whenever it is deeper than Go's 2M block. When that root already gives an in-proof tip blue score >= 2M, Rust stops there with the same root as Go and emits identical headers. Levels 36+ (fewer than 2000 headers each) are rooted at genesis on both sides. At level 13 the Go root only reaches 1998 in the proof, so Rust goes deeper and builds a different (larger) level 13.
- **[I]** Levels 12 down to 0 then differ by cascade. Each level's required block is "depth M at L+1", measured with Rust's in-proof L+1 store instead of Go's full-DAG store. Level 0 also uses the +100 margin. This matches the observation of exactly 14 warnings (levels 0-13) and the Rust proof being 1,498 headers (35 unique) larger.
- **[V]** The mismatch warning only comes from the IBD sanity test and does not stop the sync. On mismatch the node validates the locally built proof and continues (`protocol/flows/src/v5/ibd/flow.rs:326-343`). Upstream expects this mismatch when syncing from a different builder.
- **[I]** Rust could rebuild deeper roots from a Go proof that holds only about 2000 headers per level because the higher levels' headers are also level-13 blocks (any level >= 14 header is a level-13 block). This gives Rust deeper level-13 candidates, and the `is_last_level_header` fallback covers the rest.
- **[U]** Whether the Go proof also fails the 2M rule at levels 0-12. Rust validation runs top-down (`validate.rs:251`) and stops at the first error, level 13. The 14 mismatches suggest some lower levels are also thin, but this was not measured.

## 3. Inherited from Kaspa?

- **[V]** Yes, for the Go side: the sedrad and kaspad-go proof managers have identical logic (diff above). kaspad-go's builder has the same full-DAG depth measure and its validator has no 2M rejection. Levels with `bs < 2M` are skipped in the work comparison (`ppm.go:486`, `:561`), not rejected.
- **[V]** The Rust side already handled this in #494 (`3a2bcbb8`, 2024-10-29) with the "older node version without safety margin" fallback (`build.rs:313-321`).
- **[V]** `48b63582` dates from 2026-01-15, and upstream master still has it unchanged (`validate.rs:281-285` on `upstream/master`).
- **[I]** Kaspa added the strict check at a point when Go kaspad no longer served mainnet proofs, so this incompatibility never mattered for Kaspa. Sedra still runs on Go provers, so it does.

## 4. Security relevance

- **[V]** What the rule adds: without it, a level that does not start at genesis and has in-proof `bs < 2M` is simply skipped in the "is this proof better" comparison (`validate.rs:96`, `:144`; Go `ppm.go:486`). With it, such a level is a hard error (`48b63582`). It stops a prover from shipping deliberately truncated levels, which cost less PoW to forge and drop out of the comparison.
- **[V]** A node whose current pruning point is genesis (a fresh IBD) accepts any structurally valid proof after the per-level checks (`validate.rs`, `if current_pp == genesis_hash return Ok`; Go equivalent `ppm.go:~553`). The full-level rule matters most for that case.
- **[I]** Accepting Go proofs (check removed) gives the Rust node the same proof-validation security as every sedrad node on the network today. The Go validator never had this rule. This weakens nothing compared with the current Sedra network. It is weaker than upstream rusty-kaspa only in the "truncated level" case.
- **[I]** The actual Go deficit is tiny (2 to about K blues out of 2000, about 0.1-1 %). A tolerance of that size would leave an attacker a negligible forging discount. The rule's value is against *gross* truncation (for example a 50-header level), which a tolerant check still catches.
- **[I]** Rust proofs served to Go nodes: they are a structural superset (deeper roots, in-proof tip bs >= 2M). They pass all Go checks: header level, parents present, block at depth M at L+1 contained (`ppm.go:441-450`), selected tip = pruning point or its parent. Kaspa ran mixed Go and Rust networks with Rust-built proofs from 2023 to 2025 with this same Go validator. **[U]** Not tested on Sedra. Size (about 77k headers vs 76k) is well within the existing message limits. **[U]** The limits were not checked.
- **[V]** Mixed network: the remaining risk is one way only. Rust nodes *with* 48b63582 cannot sync from Go peers (observed). Without it, both directions work.

## 5. Recommendation

1. **Keep the strict 48b63582 rule out of `dev`** as long as any Sedra node that can serve proofs runs sedrad (Go). The current state (`210a9065`, with the empty-level check from `7863751e` kept) is correct. Confidence: high.
2. **Optional hardening:** re-add the rule with a tolerance, rejecting only when `root != genesis && tip_bs + T < 2M`. Choose `T` as one of:
   - `T = ghostdag_k` (18): theoretically motivated, but [I] the bound is not proven when the Go root lies off the level chain;
   - a fixed safety margin of `T = 100`: this mirrors upstream's own `+100` build margin and still rejects gross truncation.

   Before enabling either, measure the in-proof tip blue score at **every** level (0-225) of several real sedrad proofs. Do this offline from saved proofs or a local Go test node, never by syncing from production (incident 2026-11-06). Log a warning in the tolerance band instead of failing silently. Add a regression test with a recorded Go-shaped proof (tip bs 1998) that must pass and a truncated level that must fail.
3. **Restore the full upstream rule** only when all proof-serving nodes are Rust-built (that is, after the Go nodes are retired).
4. **Before relying on mixed operation,** test Go sedrad IBD from a Rust node on an isolated test setup. Rust → Go acceptance is only inferred here.
5. Leave the IBD sanity-test mismatch warnings as they are. They are expected for Go-built proofs and harmless (`flow.rs:326-343`).
