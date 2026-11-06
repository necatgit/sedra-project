#!/usr/bin/env python3
"""Export a contiguous DAG section of real Sedra headers from the local Go node (sedrad v2.0.0) via sedractl.
Walks level-0 parents back from the current tips until DAA score < tip DAA - DEPTH. Output: gzipped JSON."""
import json, subprocess, sys, gzip, datetime
DEPTH = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
OUT = sys.argv[2] if len(sys.argv) > 2 else "/data/logs/sedra_headers.json.gz"
def rpc(*args):
    r = subprocess.run(["/data/bin/sedractl", "-s", "localhost:22110", *args], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)
dag = rpc("GetBlockDagInfo")["getBlockDagInfoResponse"]
tips = dag["tipHashes"]; tip_daa = int(dag["virtualDaaScore"]); stop = tip_daa - DEPTH
seen, queue, blocks = set(tips), list(tips), []
while queue:
    h = queue.pop()
    b = rpc("GetBlock", h, "false")["getBlockResponse"]["block"]
    hd, vd = b["header"], b["verboseData"]
    assert vd["hash"] == h, (h, vd["hash"])
    blocks.append({"hash": h, "header": hd, "is_chain_block": vd["isChainBlock"], "selected_parent": vd["selectedParentHash"]})
    if int(hd["daaScore"]) < stop:
        continue
    for p in hd["parents"][0]["parentHashes"]:
        if p not in seen:
            seen.add(p); queue.append(p)
doc = {"source": "sedrad v2.0.0 (4a1153d) GetBlock RPC, local node synced from the public Sedra network",
       "exported_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "tip_virtual_daa_score": tip_daa,
       "depth": DEPTH, "pruning_point": dag["pruningPointHash"], "blocks": blocks}
with gzip.open(OUT, "wt") as f: json.dump(doc, f, separators=(",", ":"))
daa = [int(b["header"]["daaScore"]) for b in blocks]
nchain = sum(1 for b in blocks if b["is_chain_block"]); maxlev = max(len(b["header"]["parents"]) for b in blocks)
print(len(blocks), "blocks, DAA", min(daa), "..", max(daa), ", chain blocks", nchain, ", max parent levels", maxlev, "->", OUT)
