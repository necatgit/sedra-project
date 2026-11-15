#!/usr/bin/env python3
"""Regenerate TIMELINE.md: elapsed time from the project start to each closed milestone/issue, and the AI tokens used.

Usage:
  python tools/update_timeline.py <session.jsonl> [<subagent.jsonl> ...]

- Milestone times come from GitHub (issue `closed_at`, via the `gh` CLI).
- AI usage comes from the local Claude Code transcripts (only token counts and timestamps are read). Each model call is
  assigned to the phase (interval between two consecutive closed issues) in which it happened.
"""
import datetime as dt
import glob
import json
import os
import subprocess
import sys
from collections import defaultdict

REPO = "necatgit/sedra-project"
PROJECT_START = "2026-11-05T07:19:00Z"  # first message of the Claude Code session in which the project started
KEYS = ("input_tokens", "cache_creation_input_tokens", "output_tokens", "cache_read_input_tokens")


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def calls(paths):
    out = {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            m = e.get("message") or {}
            if e.get("type") == "assistant" and m.get("usage") and m.get("id") and e.get("timestamp"):
                out[(p, m["id"])] = (ts(e["timestamp"]), m["usage"], "agent" if "subagents" in p.replace("\\", "/") else "main")
    return sorted(out.values(), key=lambda c: c[0])


def fmt_elapsed(d):
    h = int(d.total_seconds() // 3600)
    m = int((d.total_seconds() % 3600) // 60)
    return f"{h} h {m:02d} min"


def k(n):
    return f"{n / 1000:,.0f} k" if n < 10_000_000 else f"{n / 1_000_000:,.1f} M"


def main(paths):
    issues = json.loads(subprocess.run(
        ["gh", "api", f"repos/{REPO}/issues?state=all&per_page=100"], capture_output=True, text=True, check=True).stdout)
    closed = sorted((ts(i["closed_at"]), i["number"], i["title"]) for i in issues
                    if i.get("closed_at") and "pull_request" not in i)
    start = ts(PROJECT_START)
    cs = calls(paths)
    now = max([c[0] for c in cs] + [dt.datetime.now(dt.timezone.utc)])

    bounds = [start] + [c[0] for c in closed] + [now]
    phase = defaultdict(lambda: defaultdict(int))
    for t, u, who in cs:
        idx = next((i for i in range(len(bounds) - 1) if bounds[i] <= t < bounds[i + 1]), len(bounds) - 2)
        for key in KEYS:
            phase[idx][key] += u.get(key, 0) or 0
        phase[idx]["calls"] += 1
        phase[idx]["agent_calls"] += who == "agent"

    total = defaultdict(int)
    for p in phase.values():
        for key, v in p.items():
            total[key] += v

    L = []
    L.append("# Timeline and AI effort\n")
    L.append("How long each step took from the start of the project, and how much AI work went into it. Regenerated "
             "with `python tools/update_timeline.py <transcripts>`; see the notes at the end for what the numbers mean.\n")
    L.append(f"**Project start:** {start:%Y-%m-%d %H:%M} UTC (first message of the session in which the project began). "
             f"**Last update:** {now:%Y-%m-%d %H:%M} UTC.\n")
    L.append("## Milestones and closed issues\n")
    L.append("| Closed (UTC) | Since start | Issue | AI calls in this phase | Fresh tokens (in / out) |")
    L.append("|---|---|---|---|---|")
    for i, (t, num, title) in enumerate(closed, start=1):
        p = phase.get(i - 1, {})
        fresh_in = p.get("input_tokens", 0) + p.get("cache_creation_input_tokens", 0)
        L.append(f"| {t:%Y-%m-%d %H:%M} | {fmt_elapsed(t - start)} | #{num} {title} | {p.get('calls', 0)} "
                 f"| {k(fresh_in)} / {k(p.get('output_tokens', 0))} |")
    p = phase.get(len(closed), {})
    if p:
        fresh_in = p.get("input_tokens", 0) + p.get("cache_creation_input_tokens", 0)
        L.append(f"| (open) | {fmt_elapsed(now - start)} | work since the last closed issue | {p.get('calls', 0)} "
                 f"| {k(fresh_in)} / {k(p.get('output_tokens', 0))} |")
    L.append("")
    L.append("A phase counts **all** AI work between two closed issues, not only the issue in that row. For example, the "
             "first row includes the project setup (repository, rules, identity), and the M2 row includes setting up the "
             "test VM, the build fix for GCC 15 and the coverage measurement. Several issues closed in the same minute "
             "share one phase; their AI effort is counted on the first of them.\n")
    # per UTC day, with links to that day's update posts (what happened), so work between closed issues shows up too
    daily = defaultdict(lambda: defaultdict(int))
    for t, u, who in cs:
        d = daily[t.date()]
        for key in KEYS:
            d[key] += u.get(key, 0) or 0
        d["calls"] += 1
    L.append("## Per day\n")
    L.append("| Day (UTC) | AI calls | Fresh tokens (in / out) | What happened |")
    L.append("|---|---|---|---|")
    for day in sorted(daily):
        d = daily[day]
        posts = sorted(glob.glob(f"updates/{day:%Y-%m-%d}-*.md"))
        links = ", ".join(f"[{os.path.basename(x)[11:-3]}]({x.replace(os.sep, '/')})" for x in posts) or "-"
        fresh_in = d["input_tokens"] + d["cache_creation_input_tokens"]
        L.append(f"| {day:%Y-%m-%d} | {d['calls']:,} | {k(fresh_in)} / {k(d['output_tokens'])} | {links} |")
    L.append("")
    L.append("## AI usage in total\n")
    L.append("| | Tokens |")
    L.append("|---|---|")
    L.append(f"| Model calls | {total['calls']:,} (of which {total['agent_calls']:,} by research agents) |")
    L.append(f"| Fresh input (new text read: messages, files, command output) | {total['input_tokens'] + total['cache_creation_input_tokens']:,} |")
    L.append(f"| Output (text and code written by the AI) | {total['output_tokens']:,} |")
    L.append(f"| Re-read from cache (the conversation so far, read again on every call) | {total['cache_read_input_tokens']:,} |")
    L.append("")
    L.append("## Notes\n")
    L.append("- Times are wall-clock time since the project start, nights and pauses included, not working hours.")
    L.append("- \"Closed\" is the moment the GitHub issue was closed, which can be some time after the work itself was done.")
    L.append("- Model: Claude (Anthropic), used through Claude Code. Every model call re-reads the conversation so far from a "
             "cache; that is why the cache figure is so large. Fresh input and output reflect the actual work.")
    L.append("- Only token counts and timestamps are taken from the local transcripts; no conversation content is published.")
    L.append("- Not included: an earlier conversation about the idea before the project started, and the human time spent.")
    L.append("- The same sessions also contain some work on Nec's pool PuddlePool (for example its solo pool on 2026-11-07); "
             "it is counted here too, so the figures are an upper bound for this project.")
    open("TIMELINE.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
