# AGENTS.md: working rules for this project

These rules apply to everyone working on the project, people and AI agents alike. They follow the same standards as
the Miningcore pool project this effort grew out of.

## What this repository is

The public home of the Sedra merged-mining proposal: plan, roadmap, proposals (SIPs), research, questions and
answers, and progress updates. Node code lives in a separate repository (a fork of `sedracoin/sedrad`) once
implementation starts. That repository gets its own AGENTS.md with build and test rules.

## Public identity

- Everything is published as **Nec** (GitHub `necatgit`). Commits use the GitHub noreply address.
- Never write a real name, private email, wallet address, holdings detail beyond the README disclosure, or anything
  from private notes into this repository.
- Check before every commit: `git config user.name` must be `Nec`, and `git diff --cached` must contain no personal data.

## Truthfulness: no false hopes

This project exists because communication around Sedra has been poor. Every public statement must hold up.

- Label every finding **Verified** (with evidence), **Inferred** (say from what), or **Unknown**.
- Evidence means something a reader can check themselves: `file:line@commit`, a commit hash, a command and its
  output, or an API URL and the returned value, with the date it was checked.
- Never present a plan, estimate or hope as a fact. Never promise dates, prices, listings or outcomes.
- Every research document ends with a **"What this does NOT mean"** section, to prevent over-reading.
- Bad news is published like good news: failed tests, slipped dates, dropped ideas, unanswered questions.
- Correct mistakes visibly. Add a dated correction note; never silently rewrite a published claim.

## Where things go

| What | Where |
|---|---|
| Overview of phases and status | `ROADMAP.md` (tick items, link issues) |
| One piece of work, its discussion and outcome | A GitHub issue; close it with a summary comment linking the evidence |
| Research findings with evidence | `research/NNNN-short-name.md`, numbered by issue |
| Unedited original reports (kept for later reference) | `research/archive/YYYY-MM-DD-NNNN-*-raw.md`, never edited |
| Every question: who it was asked, status, answer and source | `QUESTIONS.md`, the **one** list of questions. Every new question gets the next free ID there first, with a link to where it came from; other documents refer to it by ID ("Q22") instead of keeping their own list |
| Formal consensus proposals | `proposals/SIP-NNNN-*.md` |
| Dated progress posts | `updates/YYYY-MM-DD-*.md` |
| Release checklists | `release/vX.Y.Z-checklist.md` |
| Time per milestone and AI effort | `TIMELINE.md`, regenerated with `tools/update_timeline.py` together with every documentation update (it has a per-day table, so work between closed issues shows up too) |

## Keeping documentation current

The documents must always describe the current state. Not everything that happens needs to be written down, but
whatever a document claims has to be true now. Whenever a piece of work is finished (a milestone, a finding, an
answered question, a decision, a test result, a change to how something is run), update in the same session, before
reporting the work as done:

- every document whose statement it changes: `README.md` (status), `ROADMAP.md`, `QUESTIONS.md` (rows and summary
  counts), the research note, the proposal, `SEDRA.md` in the code repository;
- the evidence in `research/archive/`, and the issue (comment or close);
- `TIMELINE.md` (regenerate) and, for bigger steps or at the end of a working day, a dated `updates/` post.

Before ending a working session, check for documents that have fallen behind (stale status lines, open items that are
done, numbers that changed) and fix them. Documentation that is wrong is worse than documentation that is missing.

## Changes, commits and pushes

- Documentation commits go to `main` and are pushed when complete. Code repositories work on `dev`, and code is
  pushed only after its tests pass.
- Commit messages say what changed and why.
- **Ask first** before bigger changes: anything that changes the proposal's substance (SIP specification, activation,
  emission, treasury stance), the roadmap's scope or dates, or the repository's visibility.
- Never force-push, rewrite history or delete branches without explicit approval.

## Testing and verification

- Research: re-run the evidence commands before publishing; quote outputs, never paraphrase numbers.
- Code (once it exists): build plus the full test suite before any push. Consensus changes need tests for valid and
  invalid cases and for the activation boundary. A bug fix always comes with a regression test.
- Never claim something was built, tested or verified unless that was actually run, and report the real results.

## Safety

- Never interact with mainnet nodes, wallets or pools except through read-only public APIs.
- Never use real wallets or keys in tests. Testnet or devnet only.
- Consensus, treasury and emission topics are high-risk: verify twice and ask when in doubt.
