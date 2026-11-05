# 2026-11-05: First research results

Two research tasks are finished. Both documents label every finding as Verified, Inferred or Unknown and link to the
full evidence.

**[0002: How ZKas merged mining works](../research/0002-zkas-auxpow.md)**

- Merged mining with Kaspa needs no change to Kaspa nodes, and SDR and ZKAS can both be committed in the same Kaspa
  block, but only just: there is room for two commitments and almost nothing else.
- A correction to how the project described it earlier: merged mining does **not** make Sedra "secured by Kaspa". An
  aux chain is only as secure as the hashrate that chooses to mine it, and a large Kaspa pool could dominate it at no
  extra cost. The proposal will say this plainly.

**[0001: Review of the 2.0.0-relaunch release](../research/0001-relaunch-review.md)**

- The release made two consensus changes, both in the past: a difficulty reset and a 2.03B SDR treasury allocation.
- Some findings need answers from the Sedra team: the treasury is described as timelocked but is not, most of it has
  left the treasury address, and the circulating supply is about 6.0B SDR above what the published code can explain.
  These are questions, not accusations. They were sent to the Sedra owner today, who acknowledged them. Answers will
  be added when they come.

**Next:** issue #4, whether to build on Sedra's Go node or move to the Rust Kaspa codebase (rusty-kaspa), the same
move Kaspa itself made in 2023.
