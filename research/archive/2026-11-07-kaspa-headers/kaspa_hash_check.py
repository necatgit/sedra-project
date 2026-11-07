"""Recompute Kaspa header hashes from the fetched JSON (rusty-kaspa consensus/core/src/hashing/header.rs layout)."""
import hashlib, json, struct, sys

def u16(n): return struct.pack("<H", n)
def u32(n): return struct.pack("<I", n)
def u64(n): return struct.pack("<Q", n)

def blue_work_bytes(hexstr):
    b = bytes.fromhex(hexstr if len(hexstr) % 2 == 0 else "0" + hexstr).lstrip(b"\x00")
    return u64(len(b)) + b

def header_hash(h):
    w = hashlib.blake2b(digest_size=32, key=b"BlockHash")
    w.update(u16(int(h["version"])))
    parents = h["parents"]
    w.update(u64(len(parents)))
    for level in parents:
        hashes = level["parentHashes"]
        w.update(u64(len(hashes)))
        for p in hashes:
            w.update(bytes.fromhex(p))
    for f in ("hashMerkleRoot", "acceptedIdMerkleRoot", "utxoCommitment"):
        w.update(bytes.fromhex(h[f]))
    w.update(u64(int(h["timestamp"])))
    w.update(u32(int(h["bits"])))
    w.update(u64(int(h["nonce"])))
    w.update(u64(int(h["daaScore"])))
    w.update(u64(int(h["blueScore"])))
    w.update(blue_work_bytes(h["blueWork"]))
    w.update(bytes.fromhex(h["pruningPoint"]))
    return w.hexdigest()

doc = json.load(open(sys.argv[1]))
ok = sum(header_hash(b["header"]) == b["hash"] for b in doc["blocks"])
print(f"{ok}/{len(doc['blocks'])} header hashes reproduced")
b = doc["blocks"][0]
print("first:", b["hash"][:16], "computed:", header_hash(b["header"])[:16], "parents per level:", [len(l["parentHashes"]) for l in b["header"]["parents"]])
