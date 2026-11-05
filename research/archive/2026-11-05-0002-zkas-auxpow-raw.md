# Research #2: Study the ZKas AuxPoW design

Research date: 2026-11-05. Read-only study; the only write was `git pull` in `upstream/zkas-rusty`.

## Commits reviewed

| Repository | Ref | Commit |
|---|---|---|
| ZKas node (`upstream/zkas-rusty`, origin gitlab.com/zkas-group/zkas-rusty, `main`) | HEAD after pull | `97fafeca634eea75e88f7ca73edd6ad3dc552b91` (2026-11-05) |
| Kaspa reference (`upstream/rusty-kaspa`) | HEAD (not pulled) | `4edcbbccb449f84832afb1ca157904b35f37d006` (2026-10-19, workspace version 2.1.0) |
| Sedra Go node (`C:\Users\Nec\repos\sedrad`) | `origin/relaunch/v2.0.0` (read via `git show`) | `4a1153d8497d94f866961a67f25df722e2e3a0bc` (2026-08-11) |
| Miningcore pool (this repo) | `dev` | `38054decef32c1688ccdeef8302b0ff4335fdfeb` |

Labels: **Verified** = read in code at file:line@commit. **Inferred** = reasoned from the cited code, and the reasoning is given. **Unknown** = not determinable from these sources.

Short commit names used below: `zk` = zkas-rusty@97fafeca, `rk` = rusty-kaspa@4edcbbcc, `sd` = sedrad@4a1153d8, `mc` = miningcore@38054dec.

---

## Summary

- The proof (`AuxPow`) has three fields: the parent header, the parent coinbase transaction, and a Merkle branch from the coinbase (leaf 0) up to the parent's `hash_merkle_root`. It is Borsh-encoded and travels **on the header as a separate `aux_pow` field that is not covered by the block hash**. (Verified)
- The commitment is ASCII text inside the parent's **coinbase payload**, in the miner-controlled `extra_data` part: today the tag `ZKM1` followed by 64 lowercase hex characters (68 bytes). The legacy `ZKMM || hex(block hash)` form was replaced by a "security fork" at ZKas mainnet DAA 6,983,500 (mid-October 2026). (Verified)
- A ZKas block is valid if **either** its own kHeavyHash clears its own target **or** the parent header's kHeavyHash clears **ZKas's** target and the binding checks pass. The native path is always tried first. (Verified)
- **The parent does not have to be a valid or accepted Kaspa block.** ZKas checks only that some header-shaped object has enough kHeavyHash work and is bound to the ZKas block. It does not check the parent's `bits`, parents, DAA score, or that Kaspa ever saw it. The code says so explicitly. (Verified) The Miningcore Sedra pool already uses **Sedra** blocks as ZKas parents (`sedra1-zkas`). (Verified in config and docs)
- Replay protection after the fork: the commitment binds ZKas's genesis hash plus the nonce-free header hash, and the ZKas block's nonce must equal the first 8 bytes of the parent's hash, so one block has exactly one witness. A ZKas coinbase may not carry a ZKas commitment, which closed a real "one solution, two ZKas blocks" double-credit bug. (Verified)
- The difficulty adjustment has **no merged-mining-specific logic**. Merged hashrate simply counts as more blocks found. (Verified, absence of code)
- **No multi-aux Merkle tree** (as in Namecoin). Each chain owns its own tag slot in the coinbase. A Sedra tag would coexist with `ZKM1` as long as it is a distinct tag that cannot occur inside lowercase hex. (Verified for ZKas's parser; the Sedra side is a design inference)
- **The hard constraint for issue #3 is space.** Kaspa caps the coinbase payload at 204 bytes, and the node prepends its version string. With a P2PK payout address, about 145 bytes remain for pool `extra_data`. Two 68-byte hex commitments (136 bytes) fit only with 9 bytes or fewer of other pool text. This pool's current Kaspa prefix (`<node version>.PuddlePool Kaspa`, about 22 bytes) would not fit; it would have to shrink. A third chain cannot fit. (Inferred, arithmetic from verified constants)
- Kaspa nodes need no change. A Kaspa **pool** needs code per aux chain: an aux template subscription, the commitment, a per-share check against the aux target, proof building and aux submission. Miningcore today supports exactly one aux chain per parent pool. (Verified)
- Porting to Sedra's Go node touches the header model and its wire/DB/RPC encodings, a Borsh-compatible decoder (or a Sedra-native encoding), the PoW gate, a coinbase-tag ban, size limits, fork activation and tests. In Rust the core logic is about 1,150 lines including tests; Sedra's PoW and hashing primitives already appear to match Kaspa's. (Inferred)

---

## Findings

### Q1. Proof structure, serialization, where it is carried

- **Verified.** `pub struct AuxPow { parent_header: Header, parent_coinbase: Transaction, coinbase_merkle_branch: Vec<Hash> }` (`consensus/core/src/auxpow.rs:93-109@zk`). The coinbase is always leaf 0, and the branch is folded as a pure left path: `acc = merkle_hash(acc, sibling)` (`auxpow.rs:317-327@zk`).
- **Verified.** Serialization is Borsh, with a hand-written `BorshDeserialize` that enforces a nesting-depth limit, `MAX_AUX_POW_NESTING = 4` (`auxpow.rs:131, 168-183@zk`). The nested `Header` is ZKas's own `Header` type, which itself carries an `Option<Box<AuxPow>>`, so the encoding of the parent header includes a trailing Option tag (normally `0x00` for None). The Miningcore serializer writes it the same way (`KaspaAuxPowSerializer.cs:209-261@mc`, step 14 `WriteU8(0)`). Borsh field order: cached `hash` (32 bytes), `version` (u16), `parents_by_level` (compressed), `hash_merkle_root`, `accepted_id_merkle_root`, `utxo_commitment`, `timestamp` (u64), `bits` (u32), `nonce` (u64), `daa_score` (u64), `blue_work` (Uint192, 24 bytes), `blue_score` (u64), `pruning_point`, then `aux_pow` (`consensus/core/src/header.rs:174-205@zk`). The `Transaction` decoder is also hand-written, so it rejects compute-commit variants that don't match the tx version. That closed a remotely triggerable node crash (`consensus/core/src/tx.rs:286-310@zk`).
- **Verified, where it is carried.** As the field `Header.aux_pow`, "deliberately excluded from the header hash" (`header.rs:193-205@zk`). On the wire it travels as `bytes auxPow = 15` in the P2P block header (`protocol/p2p/proto/p2p.proto:89-91@zk`) and as `string auxPow = 16` (hex of the Borsh bytes) in the RPC header (`rpc/grpc/core/proto/rpc.proto:39-41@zk`). The RPC decoder is at `rpc/core/src/model/header.rs:15-29@zk`, and the P2P decoder at `protocol/p2p/src/convert/header.rs:113-145@zk` silently drops an undecodable or oversized witness and keeps the header.
- **Verified, size limits.** Branch length at most 64 (`MAX_COINBASE_MERKLE_BRANCH`, `auxpow.rs:62`). Total serialized witness at most 256 KiB (`MAX_AUX_POW_SERIALIZED_LEN`, `auxpow.rs:83`, enforced in `validate_structure`, `auxpow.rs:196-216`). Parent `parents_by_level` is bounded by `CompressedParents` decoding (`MAX_EXPANDED_PARENT_HASHES`, `header.rs:~140-160@zk`).
- **Verified, consequence.** Because the witness sits outside the hash, any relaying peer can strip or replace it. The design handles this by trying native PoW first and treating a missing or bad witness as a PoW failure, not as a cached-invalid block (`consensus/pow/src/auxpow.rs:60-71@zk`; `p2p/src/convert/header.rs:113-130@zk` comments).

### Q2. The commitment: what, where, format, how it is verified

- **Verified, location.** The commitment goes in the parent coinbase transaction's `payload`. On Kaspa that payload is `blue_score u64 || subsidy u64 || spk_version u16 || spk_len u8 || script_pubkey || extra_data` (`consensus/src/processes/coinbase.rs:144-161@rk`). `extra_data` is supplied by the miner through `getBlockTemplate`, and the Kaspa node prepends `"<version>/"` to it (`rpc/service/src/service.rs:413@rk`). ZKas scans the **whole** payload, not just `extra_data` (`auxpow.rs:283-312@zk`).
- **Verified, format (current, post security fork).** `"ZKM1"` (ASCII, 4 bytes) followed by 64 lowercase hex characters of `bound_commitment = BlockHash-hasher("zkas_aux_bind1" || genesis_hash || nonce_free_header_hash)` (`auxpow.rs:51, 250-255@zk`). `nonce_free_header_hash` is the ZKas header hash with nonce = 0 and the real timestamp (`consensus/pow/src/auxpow.rs:91@zk`). Hex rather than raw bytes, because Kaspa's GBT `extraData` is a protobuf **string** that must be valid UTF-8 (`auxpow.rs:223-226@zk`). Uppercase hex is rejected (`auxpow.rs:378-384`).
- **Verified, legacy format.** `"ZKMM" || hex(H_fc)` (`auxpow.rs:47, 227-229@zk`). Valid only before the fork, and from the fork on a bound-rule parent must **not** also carry exactly one `ZKMM` (`consensus/pow/src/auxpow.rs:88-93@zk`).
- **Verified, uniqueness.** The tag must appear exactly once. Two occurrences, a truncated commitment or non-hex characters all mean rejection (`auxpow.rs:31-38, 283-312@zk`).
- **Verified, verification chain.** `pow(parent_header) → parent_header.hash_merkle_root → coinbase (leaf 0) → commitment` (`auxpow.rs:21-29@zk`). Post-fork checks, in `check_pow_gated` (`consensus/pow/src/auxpow.rs:72-103@zk`):
  1. Native PoW fails (otherwise the block is accepted natively).
  2. `header.nonce == u64_le(first 8 bytes of hash(parent_header))` (`auxpow.rs:261-264@zk`).
  3. The parent coinbase carries **no** valid single `ZKMM`.
  4. Exactly one `ZKM1` equal to `bound_commitment(genesis, nonce_free_hash)`, plus coinbase Merkle inclusion.
  5. `kHeavyHash(parent_header) <= target(ZKas header.bits)`.
- **Verified, data needed.** Yes, the full parent coinbase transaction plus a Merkle path. The parent header fields used are **all** fields that feed the Kaspa header hash (version, parents, three roots, timestamp, bits, nonce, daa_score, blue_work, blue_score, pruning_point), because the PoW's pre-PoW hash covers them (`consensus/pow/src/lib.rs:28-38@zk`; `consensus/core/src/hashing/header.rs:7-30@zk`). Semantically only `hash_merkle_root` (for inclusion) and `nonce` / `timestamp` (for PoW) are interpreted. The parent's own `bits` is **ignored**; the work is compared against ZKas's target (`consensus/pow/src/auxpow.rs:25-30@zk`).
- **Verified, compatibility with real Kaspa.** ZKas's header hashing is byte-for-byte the same function as Kaspa's (`hashing/header.rs:7-30` is identical in `zk` and `rk`). Both `Header` structs have identical fields apart from `aux_pow` (diff of `consensus/core/src/header.rs`). The tx hashing differs from Kaspa's only by an import and a doc comment (diff of `consensus/core/src/hashing/tx.rs`). Kaspa coinbases have mass 0, so the mass commitment is a no-op for them (`hashing/tx.rs:73-91@rk` design note "Require in consensus that coinbase mass == 0").

### Q3. Dual acceptance, activation, difficulty

- **Verified, flow.** The header pipeline calls `check_pow_and_calc_block_level`, which picks `AuxRule::{Off, Legacy, Bound(genesis)}` from `merged_mining_activation` and `security_fork_activation` evaluated at the header's own `daa_score`, then calls `check_pow_gated` (`consensus/src/pipeline/header_processor/pre_ghostdag_validation.rs:102-122@zk`; `consensus/pow/src/auxpow.rs:105-129@zk`). The returned `pow` value (the parent's kHeavyHash for an aux block) sets the **block level** used by the pruning proof (`pre_ghostdag_validation.rs:121`).
- **Verified, activation.** Mainnet `merged_mining_activation: ForkActivation::always()`, active from genesis since the July 2026 relaunch (`consensus/core/src/config/params.rs:1089-1097@zk`). `security_fork_activation: ForkActivation::new(ZKAS_SECURITY_FORK_DAA)` with `ZKAS_SECURITY_FORK_DAA = 6_983_500` (`params.rs:945-951, 1098@zk`). The coinbase-tag ban starts `2 * finality_depth` earlier (`params.rs:726-735@zk`, `coinbase_commitment_ban_activation`). Testnet has both active from genesis (`params.rs:1193-1195@zk`).
- **Verified, difficulty.** `consensus/src/processes/difficulty.rs@zk` contains no reference to aux, and neither do the ghostdag modules (grep found no matches). The difficulty adjustment sees aux-mined blocks exactly like native blocks: same `bits`, same block rate. Blue work derives from `bits`, not from the parent's actual hash value. (Inferred from upstream Kaspa design. Blue work in rusty-kaspa is computed from `bits`.)
- **Verified, one aux-specific allowance.** The fresh-sync pruning-proof work floor assumes "one solution can back at most two headers (a header, and the block it serves as aux parent for)" and halves its estimate accordingly (`consensus/src/processes/pruning_proof/validate.rs:373-384, 440-455@zk`). Pruning-proof level validation also applies the aux rule (`validate.rs:172, 204-217`; `pruning_proof/mod.rs:224, 479-485@zk`).
- **Inferred, merged hashrate.** With merged mining, a Kaspa pool's shares that fail Kaspa's target routinely clear the much easier aux target (`consensus/pow/src/auxpow.rs:14-17@zk` comment). So the aux chain's difficulty rises toward whatever fraction of Kaspa hashrate participates. For Sedra this would leave native-only miners marginal.

### Q4. Security checks: what is and is not guaranteed

Guaranteed (Verified, `zk`):
- **Work binding.** An aux-accepted block has a kHeavyHash value at or below its own ZKas target, computed by the node from the parent's header fields. The cached `hash` is never trusted (`auxpow.rs:94-97`; `consensus/pow/src/auxpow.rs:28-30`).
- **Commitment binding.** Exactly one `ZKM1` tag naming this block (genesis-bound, nonce-free), and Merkle-proven to be leaf 0 under the parent's `hash_merkle_root`. A non-coinbase transaction cannot be passed off as leaf 0 (`auxpow.rs:101-108`).
- **One block, one witness.** The nonce equals the truncated parent hash (`auxpow.rs:257-264`; `consensus/pow/src/auxpow.rs:83-95`).
- **Cross-network replay.** The genesis hash is mixed into the commitment (`auxpow.rs:246-255`), so a commitment for testnet or another ZKas-scheme chain does not match mainnet.
- **Self-parent ban.** A ZKas block's own coinbase may not carry `ZKMM`/`ZKM1` (`consensus/src/pipeline/body_processor/body_validation_in_context.rs:118-125`; RPC refusal at `rpc/service/src/service.rs:457-468`). This fixed a real bug: one native ZKas solution whose coinbase committed to a second ZKas block counted as PoW for both (`zkas-api/examples/auxpow_double_credit.rs:1-18`; fix in commit `df238f2c`, 2026-10-06).
- **Straddle protection.** A parent cannot back both a legacy and a bound block (fuzz test `consensus/pow/src/auxpow.rs:167-256`).
- **DoS bounds.** See the size limits in Q1. A natively valid block can never be invalidated by a junk witness (`consensus/pow/src/auxpow.rs:62-66`).

Not guaranteed (Verified, stated in code):
- **The parent is not required to be a valid or accepted Kaspa block.** "Nothing in the parent needs to be a *valid* Kaspa block — only that enough kHeavyHash work, bound to `H_fc`, was performed" (`consensus/core/src/auxpow.rs:25-29@zk`). The demo miner builds a "synthetic Kaspa-shaped block" (`miner/src/merged.rs:9-13@zk`).
- **No parent-chain identification.** There is no check of the parent's `bits`, its parents, its DAA score, its timestamp, its Kaspa network or genesis, or that its coinbase pays anyone. Evidence: the Miningcore Sedra pool (`config.json`: pool `sedra1` at line 190, with `mergedMining` zkas at lines 304-316) uses Sedra blocks as ZKas parents. `doc/ROADMAP.md:125@mc` records 12 `sedra1-zkas` blocks from 2026-10-20 to 10-31, which is after the fork.
- **Not a "Kaspa-secured" guarantee.** ZKas's security is the kHeavyHash work aimed at ZKas, natively or through any parent. (Inferred.) Because merged mining removes the opportunity cost, a large Kaspa pool could out-mine ZKas without losing Kaspa revenue. This is the classic merged-mining risk; ZKas's code has no mitigation for it.

### Q5. Multi-aux: several aux chains in one Kaspa coinbase

- **Verified, no Namecoin-style design.** There is no aux-chain Merkle tree, chain-id slot or chain index. ZKas requires its **own** tag with its own 32-byte commitment, unique in the payload (`auxpow.rs:283-312@zk`). Sedra cannot share ZKas's slot without a ZKas hard fork.
- **Verified, non-collision with ZKas.** ZKas counts only the exact byte sequences `ZKMM` and `ZKM1`. Any other bytes, including another chain's tag and hex, are ignored, as the fuzz test with junk around the tags shows (`consensus/pow/src/auxpow.rs:184-218@zk`). Lowercase hex (`0-9a-f`) can never contain `Z`, `K` or `M`, so a ZKas commitment cannot spoof a tag that contains a character outside `0-9a-f`, and vice versa.
- **Inferred, what Sedra needs so it doesn't collide.**
  1. A distinct 4-byte tag with at least one character outside `[0-9a-f]` and not equal to `ZKMM` or `ZKM1` (for example something `SD..`-prefixed; the exact value is for issue #3).
  2. A genesis-bound commitment with its own domain string (ZKas uses `"zkas_aux_bind1"`).
  3. The same "exactly once" rule.
  4. A self-parent ban (no Sedra tag in Sedra's own coinbase).
  5. Nonce binding.
- **Inferred, space budget (the binding constraint).** Kaspa `max_coinbase_payload_len = 204` is enforced in consensus (`consensus/core/src/config/params.rs:614@rk`; `consensus/src/processes/coinbase.rs:190-191@rk`). The fixed part is 19 bytes. A P2PK Schnorr script is 34 bytes (P2SH and ECDSA are 35). The node prefix `"2.1.0/"` is 6 bytes (`Cargo.toml:76@rk`; `service.rs:413@rk`). That leaves 204 − 19 − 34 − 6 = **145 bytes** for pool `extra_data`.
  - One commitment: 68 bytes.
  - Two: 136 bytes, which leaves 9 bytes for any pool tag. Miningcore's Kaspa parent prefix is `ServerVersion + "." + extraData` (`KaspaJobManager.cs:1421, 1503@mc`), with `extraData` = "PuddlePool Kaspa" for `kaspa1` (`config.json:116@mc`). That is about 22 bytes, assuming a 5-character node version. So today 22 + 68 = 90 bytes are used and 55 remain, which is not enough for a second 68-byte commitment unless the pool tag is cut to 9 bytes or fewer. (`mergedMining.extraData` "Miningcore" at `config.json:172` goes to the aux daemon, not into the Kaspa coinbase.)
  - Three: impossible.
  - A P2SH payout or a longer future node version string shrinks the room further.
- **Inferred, implication.** For Sedra plus ZKas on the same Kaspa block, the space is just enough. Issue #3 could consider a raw-bytes or shorter encoding (for example a truncated commitment), or a multi-chain root. Any non-UTF-8 encoding cannot go through Kaspa's GBT `extraData` string, but a pool could still splice the payload itself only if the coinbase is built locally, which Kaspa's GBT does not offer. Unknown.

### Q6. How the Miningcore pool builds the commitment and submits

All Verified at `mc`:
- **Aux template.** The pool subscribes to the aux daemon's `NewBlockTemplate` stream (`src/Miningcore/Blockchain/Kaspa/KaspaJobManager.cs:461-560`). `UpdateAuxBlockTemplate` zeroes the nonce, computes the nonce-free header hash in C#, computes `bound_commitment` with the hard-coded ZKas genesis, and stores `currentAuxBlockHashHex` and the aux target (`KaspaJobManager.cs:384-413`; constants and genesis in `KaspaAuxPowSerializer.cs:21-37`). A changed commitment triggers a parent template refresh, throttled to 3 s (`KaspaJobManager.cs:425-431`).
- **Where the Kaspa template is modified.** It isn't modified after the fact. The commitment is passed as `ExtraData` in the parent `GetBlockTemplateRequest` (`KaspaJobManager.cs:91-104`), built by `GetParentExtraData()` = `extraData + "ZKM1" + hex`, where the prefix is `<node ServerVersion>.<pool extraData>` (`KaspaJobManager.cs:1421, 1503`) (`KaspaJobManager.cs:134-147`; `KaspaAuxPowSerializer.cs:101-112`). The parent node writes it into the coinbase.
- **Job binding.** A job is linked to the aux template only if the template's coinbase actually carries the current commitment (`KaspaJobManager.cs:695-712`).
- **Submit.** For a share that meets the aux target, `SubmitAuxBlockAsync`:
  1. hashes all parent transactions,
  2. builds the leaf-0 branch,
  3. re-checks the Merkle root against the header,
  4. re-extracts and compares the `ZKM1` commitment,
  5. Borsh-serializes `AuxPow`,
  6. sets the aux nonce to `ComputeNonceBinding(parentHash)` and `Header.AuxPow` to the hex,
  7. calls `SubmitBlock` on the aux daemon.

  (`KaspaJobManager.cs:911-990`; serializer `KaspaAuxPowSerializer.cs:160-300`.)
- **Per extra aux chain.** The Kaspa node needs no change. The pool does: Miningcore holds exactly one `auxRpc`, `currentAuxBlockTemplate`, `currentAuxBlockHashHex` and target (`KaspaJobManager.cs:74-82`) and one `mergedMining` config block per pool. Supporting a second aux chain would need N-way state, a combined `extraData`, a per-share check against each aux target, per-chain proof building with a different commitment rule, and separate DB pool IDs, wallets and payouts (`.agents/rules/merged_mining.md`). (Inferred for the design; the single-aux limit is Verified.) Stock Kaspa bridges and other pools do none of this. Whether any third-party Kaspa pool would adopt a Sedra tag is Unknown.

### Q7. Implementation size and what a Go port would involve

Verified LOC at `zk` (total lines / lines mentioning "aux"):

| Area | File | Lines | Aux lines |
|---|---|---|---|
| Structure and binding (incl. ~9 tests) | `consensus/core/src/auxpow.rs` | 576 | 81 |
| PoW gate and rules (incl. fuzz tests) | `consensus/pow/src/auxpow.rs` | 572 | 110 |
| Header field and memory estimate | `consensus/core/src/header.rs` | – | ~15 |
| Params and activations | `consensus/core/src/config/params.rs` | – | ~30 |
| Header pipeline gate | `consensus/src/pipeline/header_processor/pre_ghostdag_validation.rs` | 123 | 6 |
| Coinbase-tag ban | `consensus/src/pipeline/body_processor/body_validation_in_context.rs` | 319 | 2 |
| Pruning proof | `consensus/src/processes/pruning_proof/{mod,validate}.rs` | – | ~15 |
| RPC model | `rpc/core/src/model/header.rs` | 382 | 26 |
| P2P conversion | `protocol/p2p/src/convert/header.rs` | 340 | 53 |
| Protos | `rpc.proto`, `p2p.proto` | – | 2 fields |
| GBT refusal | `rpc/service/src/service.rs` | – | ~12 |
| Demo miner | `miner/src/merged.rs` | 90 | 14 |
| Probes | `zkas-api/examples/auxpow_{live,double_credit}.rs` | 266 | – |

The two core auxpow files contain 23 `#[test]` functions. The history has 14 commits touching the two core files, from `c0022c93` (2026-07-08, "merged mining (AuxPoW) end-to-end") to the October security fork `df238f2c` / `b4f8886c` / `6209635c`. Several later commits are hardening fixes (nesting DoS, oversized witness, tx decode crash, double credit), which shows the attack surface is not trivial.

Pool side, Verified at `mc`: `KaspaAuxPowSerializer.cs` 764 lines, aux paths in `KaspaJobManager.cs`, and tests `KaspaAuxPowSerializerTests.cs` (715) and `KaspaAuxBlockTrackingTests.cs` (561).

**Inferred, Go port components for Sedra** (no time estimate):
1. An aux-witness field on Sedra's block header, outside `HeaderHash`, threaded through the domain model, the appmessage/P2P protobuf, the RPC protobuf and converters, and the block/header DB serialization. That is a hard fork plus a protocol version bump.
2. A Kaspa-header and Kaspa-coinbase decoder. Either Borsh-compatible with ZKas (so pools reuse one serializer), or a Sedra-native encoding.
3. A PoW gate: native first, then aux. Uses Sedra's existing kHeavyHash (`domain/consensus/utils/pow/pow.go@sd`, `NewState`), with the parent's header hash computed by `consensushashing.HeaderHash`. Sedra's domain strings `BlockHash`, `ProofOfWorkHash`, `HeavyHash`, `TransactionHash` and `MerkleBranchHash` match Kaspa's (`domain/consensus/utils/hashes/domains.go:10-19@sd` vs `crypto/hashes/src/hashers.rs:19-28@rk`). Whether they are byte-identical end to end is Inferred and needs cross-implementation test vectors against real Kaspa mainnet blocks.
4. Coinbase Merkle-branch verification, plus Kaspa's tx hash for the coinbase. Kaspa's current tx hash includes a storage-mass commitment, which is a no-op for mass-0 coinbases. Kaspa tx versions ≥1 encode inputs differently, which doesn't matter for an input-less coinbase. Needs vectors.
5. A Sedra tag and genesis-bound commitment, nonce binding, the exactly-once rule, a self-parent ban in Sedra's coinbase validation and GBT, and size limits (branch ≤64, witness cap, parents cap).
6. Block level and pruning proof (Sedra is a kaspad fork with pruning proofs) must use the aux PoW value.
7. Fork activation by DAA score.
8. Mining manager / GBT: no change is needed for Sedra as an aux, but the template's hash and nonce semantics must be documented for pools.
9. Tests: unit, fuzz and devnet probes like `auxpow_double_credit`.
10. The pool side: multi-aux support in Miningcore.

---

## Evidence appendix (key excerpts)

- `consensus/core/src/auxpow.rs:47,51@zk`: `MERGE_MINE_MAGIC = *b"ZKMM"`, `MERGE_MINE_MAGIC_V1 = *b"ZKM1"`.
- `consensus/core/src/auxpow.rs:250-255@zk`: `hasher.update(b"zkas_aux_bind1").update(genesis).update(nonce_free_header_hash)`.
- `consensus/core/src/auxpow.rs:261-264@zk`: nonce binding = `u64::from_le_bytes(hash(parent_header)[..8])`.
- `consensus/pow/src/auxpow.rs:91-95@zk`: `header.nonce == AuxPow::nonce_binding(&a.parent_header) && a.committed_hash().is_none() && a.verify_binding_v1(genesis, nonce_free) && parent_pow(a) <= target`.
- `consensus/core/src/auxpow.rs:25-26@zk`: "Nothing in the parent needs to be a *valid* Kaspa block — only that enough kHeavyHash work, bound to `H_fc`, was performed."
- `consensus/core/src/config/params.rs:951@zk`: `ZKAS_SECURITY_FORK_DAA: u64 = 6_983_500`. `:1097`: `merged_mining_activation: ForkActivation::always()`.
- `consensus/core/src/config/params.rs:614@rk`: `max_coinbase_payload_len: 204`. `rpc/service/src/service.rs:413@rk`: `extra_data = version() + "/" + request.extra_data`.
- `src/Miningcore/Blockchain/Kaspa/KaspaJobManager.cs:142@mc`: `KaspaAuxPowSerializer.EmbedCommitment(currentAuxBlockHashHex, prefix: extraData)`.
- `src/Miningcore/Blockchain/Kaspa/KaspaJobManager.cs:969-970@mc` (in `SubmitAuxBlockAsync`): `auxBlockToSubmit.Header.Nonce = ComputeNonceBinding(parentBlockHash); auxBlockToSubmit.Header.AuxPow = hex(auxPowBytes)`.
- `doc/ROADMAP.md:125@mc`: `sedra1-zkas: 12 blocks … 2026-10-20 … 10-31` (Sedra-parented ZKas blocks).

## Open questions

1. **Byte budget (issue #3).** Can a Kaspa pool fit two 68-byte commitments plus its tag in 145 bytes? Do other pools use P2SH payout scripts or long tags? Should Sedra use a shorter commitment, which weakens the binding, or propose a shared multi-chain root, which needs a ZKas fork to share?
2. **Cross-implementation equality.** Do Go kHeavyHash, header hashing, tx hashing and Merkle on Sedra produce identical results to rusty-kaspa for real Kaspa mainnet blocks, including post-Crescendo and future Toccata blocks? This needs test vectors.
3. **Kaspa header evolution.** If Kaspa adds header fields in a future hard fork, both ZKas and a Sedra port must update their parent-header decoder and hasher, or merged mining with Kaspa stops. The header fields are identical today (diff of `header.rs`, `zk` vs `rk`). How would Sedra track this?
4. **Pool adoption.** Which Kaspa pools beyond this Miningcore instance would include a Sedra tag? Unknown.
5. **Security model.** Do Sedra holders accept that merged mining lets a large Kaspa pool out-mine Sedra at no opportunity cost? Is any mitigation wanted, such as checkpoints or finality rules, and would it be acceptable?
6. **DAA.** With large merged hashrate and no special DAA handling, how does Sedra's difficulty react if a big Kaspa pool joins or leaves abruptly? Nothing in ZKas mitigates this. Its effect on ZKas is not measured here (Unknown).
7. **Coexistence.** Sedra blocks currently act as ZKas parents (`sedra1-zkas`). A Sedra block that is itself merge-mined from Kaspa can still carry a `ZKM1` commitment. Should Sedra's self-parent ban cover only its own tag (Inferred: yes, only its own)?
8. **Raw-bytes path.** Could the commitment bypass the UTF-8 `extraData` string? Only if a pool builds the Kaspa coinbase itself, which stock Kaspa GBT does not support (Unknown whether a Kaspa RPC exists for it).

## What this does NOT mean

- It does **not** mean Sedra can be merged-mined with Kaspa today, or that any Kaspa pool has agreed to do it.
- It does **not** mean Sedra would inherit "Kaspa's security". The ZKas design checks only kHeavyHash work bound to the aux block, not that the parent is a real, accepted Kaspa block. An aux chain is only as secure as the hashrate that chooses to mine it.
- It does **not** mean the Go port is small or low-risk. ZKas needed several security-fix rounds after launch (double credit, DoS bounds, decoder crash, nesting).
- It does **not** establish byte-level compatibility between Sedra's Go hashing and Kaspa's Rust hashing. That is inferred from matching code shapes and domain strings, and not tested here.
- It does **not** say anything about prices, rewards, adoption timelines or the outcome of the proposed fork.
- The production figures cited (`sedra1-zkas` block counts) come from a project document, not from a live check made for this report.
