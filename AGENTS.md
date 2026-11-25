# AGENTS.md: working rules for this project

These rules apply to everyone working on the project, people and AI agents alike. They follow the same standards as
the Miningcore pool project this effort grew out of.

## What this repository is

The public home of the Sedra project (`necatgit/sedra-project`, named `sedra-merged-mining` until 2026-11-15): plan,
roadmap, decisions, proposals (SIPs), research and analyses, questions and answers, release notes and progress
updates. It holds documents, not code.

Where things belong:
- **Code** goes to the code repositories: the Rust node `necatgit/sedra-rusty` (with its own AGENTS.md, build and test
  rules; the merged-mining end-to-end harness is there in `contrib/e2e-merged-mining/` on `m10-auxpow`) and the
  Miningcore pool. The only scripts here are the ones that build this repository's documents (`tools/`).
- **Private material** (private correspondence, personal details, unpublished notes) lives in a separate private repository and never comes here. A result from it is published here
  only when Nec says so, as a summary with checkable evidence.

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

**One fact, one source.** Every fact has one document that owns it; everywhere else links to it or mirrors it, and
mirrors must say the same. When two documents disagree, the owner is right and the other one gets fixed.

| Fact | Owner | Mirrors |
|---|---|---|
| Public plan and phase status | `ROADMAP.md` | `README.md` status, `TIMELINE.md` (generated) |
| Status of one piece of work | its GitHub issue (here, in `sedra-rusty` or in `sedra-sips`) | `ROADMAP.md` ticks |
| Questions and answers | `QUESTIONS.md` (by Q-ID) | other documents cite the ID only |
| A SIP's rules and status | `proposals/SIP-*.md` here | the public copy in `necatgit/sedra-sips` (same substance, no links to private notes) and its README table |
| Testnet facts (kit, decisions, rehearsal, launch state) | `testnet/` | `contrib/testnet/` in `sedra-rusty` |
| Node changes and releases | `SEDRA.md` in `sedra-rusty` (branch `dev`) and its GitHub releases | `README.md`, `ROADMAP.md` |
| Dated posts, raw evidence | the dated file (`updates/`, `research/archive/`): history, never rewritten | none |

When a fact changes:
- update the owner first, then every mirror; then search this repository, `sedra-sips` and `sedra-rusty` (and the
  issues) for the old wording, number or date and fix every live copy in the same session;
- when the state of a piece of work changes (milestone done, date moved, answer in, blocker gone or new), post a
  short dated comment on its issue in the same session: neutral facts and links to public documents only;
- never write "Verified", "done", "passed" or "live" before the check ran; link the evidence and give time-sensitive
  claims their observation date; corrections get a dated note, never a silent rewrite.

Before ending a working session, check for documents that have fallen behind (stale status lines, open items that are
done, numbers and dates that differ between documents, issues that are open or closed in the wrong state, SIP copies
that differ) and fix them. Documentation that is wrong is worse than documentation that is missing.

This is the public part of the shared documentation rule "One fact, one source"; the full rule, which also covers the
maintainer's private notes and the pool repository, is kept in the Miningcore pool repository's `AGENTS.md`. Nothing
private comes here (see "Public identity").

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
