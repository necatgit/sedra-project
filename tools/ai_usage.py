#!/usr/bin/env python3
"""Sum the AI token usage of a Claude Code session (and its subagents) from its local transcript files.

Usage: python ai_usage.py <session.jsonl> [<subagent.jsonl> ...]  -> prints JSON

Each assistant answer in a transcript carries a `usage` block. One answer can be written as several lines (one per
content block) with the same message id, so lines are de-duplicated by message id. Only token counts, models and
timestamps are read; no conversation content is copied.
"""
import json
import sys
from collections import defaultdict


def summarize(path):
    seen = {}
    first = last = None
    for line in open(path, encoding="utf-8"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = e.get("timestamp")
        if ts:
            first = ts if first is None or ts < first else first
            last = ts if last is None or ts > last else last
        m = e.get("message") or {}
        u = m.get("usage")
        if e.get("type") != "assistant" or not u or not m.get("id"):
            continue
        seen[m["id"]] = (m.get("model", "unknown"), u, (ts or "")[:10])
    per_model = defaultdict(lambda: defaultdict(int))
    per_day = defaultdict(lambda: defaultdict(int))
    for model, u, day in seen.values():
        for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
            per_model[model][k] += u.get(k, 0) or 0
            per_day[day][k] += u.get(k, 0) or 0
        per_model[model]["answers"] += 1
        per_day[day]["answers"] += 1
    return {"file": path.replace("\\", "/").split("/")[-1], "first": first, "last": last,
            "per_model": per_model, "per_day": per_day}


if __name__ == "__main__":
    print(json.dumps([summarize(p) for p in sys.argv[1:]], indent=1, default=dict))
