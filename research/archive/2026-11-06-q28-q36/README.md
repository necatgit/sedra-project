# Evidence for Q28 and Q36 (2026-11-06)

**Q28: are Sedra's copies of the two crypto libraries identical to Kaspa's originals?** Yes, in code.
`q28-crypto-modules-diff.txt`: `github.com/sedracoin/go-muhash@v1.0.1` and `github.com/sedracoin/go-secp256k1@v1.0.2`
(the versions in sedrad v2.0.0's `go.mod`) downloaded from the public Go module proxy, with their checksums, and compared
with `github.com/kaspanet/go-muhash@v0.0.4` and `github.com/kaspanet/go-secp256k1@v0.0.7` after replacing the module
name `sedracoin` with `kaspanet`. No difference in any `.go`, `.c`, `.h` or `.s` file. The only differences: `go.mod`
(one dependency line, formatting), the fuzz-test corpus (test inputs, not compiled) and an extra `.gitattributes`.

**Q36: does the inherited `isStaged()` bug in sedrad have a practical effect?** No.
`isStaged()` in `domain/consensus/datastructures/headersselectedchainstore/headers_selected_chain_staging_shard.go:82-86`
(sedrad `4a1153d`) checks `addedByIndex` twice and never `removedByIndex`, so it would miss changes that consist only of
index removals. `git grep -n "removedByIndex\[" 4a1153d -- '*.go'` finds exactly one write,
`headers_selected_chain_store.go:56`, and it is always followed by a write to `removedByHash` on line 57. So whenever
`removedByIndex` is non-empty, `removedByHash` is too, and `isStaged()` returns true. The condition is redundant code
(Kaspa later corrected it to `removedByIndex`), not a functional defect.
