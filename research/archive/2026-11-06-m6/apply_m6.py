"""M6: port sedrad v2.0.0's two relaunch rules (difficulty reset, treasury allocation) into sedra-rusty. Run from repo root."""
import pathlib
import re


def rd(p):
    return pathlib.Path(p).read_text()


def wr(p, s):
    pathlib.Path(p).write_text(s)


def once(s, old, new, where):
    assert s.count(old) == 1, f"{where}: expected 1 occurrence of {old[:70]!r}, found {s.count(old)}"
    return s.replace(old, new)


# ---------- params.rs ----------
P = "consensus/core/src/config/params.rs"
s = rd(P)
s = once(s, "pub struct ForkActivation(u64);", '''pub struct ForkActivation(u64);

/// SEDRA v2.0.0: one treasury allocation window. Blocks whose own DAA score lies in the half-open range
/// `[activation_daa_score, activation_daa_score + window_blocks)` carry an extra coinbase output of `per_block_seep`
/// to the treasury script. Mirrors `TreasuryAllocation*` in sedrad v2.0.0 `domain/dagconfig/params.go`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct TreasuryAllocationWindow {
    pub activation_daa_score: u64,
    pub window_blocks: u64,
    pub per_block_seep: u64,
}

/// SEDRA: mirrors sedrad's `blockInDifficultyResetWindow` exactly (window == 0 means never).
pub fn block_in_difficulty_reset_window(block_daa_score: u64, activation_daa_score: u64, window_blocks: u64) -> bool {
    if window_blocks == 0 || block_daa_score < activation_daa_score {
        return false;
    }
    block_daa_score - activation_daa_score < window_blocks
}

/// SEDRA: mirrors sedrad's `blockInTreasuryAllocationWindow` exactly, including its overflow guard.
pub fn block_in_treasury_allocation_window(block_daa_score: u64, activation_daa_score: u64, window_blocks: u64) -> bool {
    if window_blocks == 0 {
        return false;
    }
    let end = activation_daa_score.checked_add(window_blocks).unwrap_or(u64::MAX);
    block_daa_score >= activation_daa_score && block_daa_score < end
}

/// SEDRA v2.0.0 mainnet treasury allocation, "exactly as mined" (sedrad v2.0.0 `params.go`, 4a1153d).
pub const SEDRA_MAINNET_TREASURY_ALLOCATION_WINDOWS: [TreasuryAllocationWindow; 2] = [
    TreasuryAllocationWindow { activation_daa_score: 53_632_372, window_blocks: 200, per_block_seep: 1_000_000_000_000_000 },
    TreasuryAllocationWindow { activation_daa_score: 53_633_267, window_blocks: 454, per_block_seep: 100_000_000_000_000 },
];

/// SEDRA v2.0.0 mainnet treasury script (P2SH, script version 0) of
/// `sedra:pp8a4l47q0qjwlwgqvnmp5ppssk6zpn9hat58vaw6jkxkee2aqduue9252wc3`.
pub const SEDRA_MAINNET_TREASURY_SCRIPT_PUBLIC_KEY: [u8; 35] = [
    0xaa, 0x20, 0x4f, 0xda, 0xfe, 0xbe, 0x03, 0xc1, 0x27, 0x7d, 0xc8, 0x03, 0x27, 0xb0, 0xd0, 0x21, 0x84, 0x2d, 0xa1, 0x06,
    0x65, 0xbf, 0x57, 0x43, 0xb3, 0xae, 0xd4, 0xac, 0x6b, 0x67, 0x2a, 0xe8, 0x1b, 0xce, 0x87,
];''', P)
s = once(s, "    pub crescendo: CrescendoParams,\n    pub crescendo_activation: ForkActivation,\n}", '''    pub crescendo: CrescendoParams,
    pub crescendo_activation: ForkActivation,

    /// SEDRA v2.0.0 fair-restart difficulty reset: blocks with DAA score in
    /// `[difficulty_reset_activation_daa_score, + difficulty_reset_window_blocks)` require the genesis bits.
    /// Dormant when either is 0.
    pub difficulty_reset_activation_daa_score: u64,
    pub difficulty_reset_window_blocks: u64,
    /// SEDRA v2.0.0 treasury allocation windows (empty = dormant) and the treasury script (empty = dormant).
    pub treasury_allocation_windows: &'static [TreasuryAllocationWindow],
    pub treasury_script_public_key: &'static [u8],
}''', P)
marker = "    crescendo_activation: ForkActivation::never(), // Sedra runs the pre-Crescendo (kaspad Go v0.12.15) rules\n"
assert s.count(marker) == 4, s.count(marker)
parts = s.split(marker)
out = parts[0]
for i in range(4):
    if "pub const MAINNET_PARAMS: Params" in parts[i]:
        extra = '''    // SEDRA v2.0.0 relaunch rules, exactly as in sedrad v2.0.0 params.go
    difficulty_reset_activation_daa_score: 53_625_512,
    difficulty_reset_window_blocks: 2641,
    treasury_allocation_windows: &SEDRA_MAINNET_TREASURY_ALLOCATION_WINDOWS,
    treasury_script_public_key: &SEDRA_MAINNET_TREASURY_SCRIPT_PUBLIC_KEY,
'''
    else:
        extra = '''    difficulty_reset_activation_daa_score: 0,
    difficulty_reset_window_blocks: 0,
    treasury_allocation_windows: &[],
    treasury_script_public_key: &[],
'''
    out += marker + extra + parts[i + 1]
assert out.count("difficulty_reset_activation_daa_score: 53_625_512") == 1
s = out
wr(P, s)

# ---------- integration test literal Params ----------
I = "testing/integration/src/consensus_integration_tests.rs"
s = rd(I)
s = once(s, "            crescendo_activation: ForkActivation::never(),\n", '''            crescendo_activation: ForkActivation::never(),
            difficulty_reset_activation_daa_score: 0,
            difficulty_reset_window_blocks: 0,
            treasury_allocation_windows: &[],
            treasury_script_public_key: &[],
''', I)
wr(I, s)

# ---------- window.rs: difficulty reset in DualWindowManager ----------
W = "consensus/src/processes/window.rs"
s = rd(W)
s = once(s, '''    crescendo_activation: ForkActivation,
    full_window_manager: FullWindowManager<T, U, V>,
    sampled_window_manager: SampledWindowManager<T, U, V, W>,
}''', '''    crescendo_activation: ForkActivation,
    full_window_manager: FullWindowManager<T, U, V>,
    sampled_window_manager: SampledWindowManager<T, U, V, W>,
    // SEDRA v2.0.0 difficulty reset
    genesis_bits: u32,
    difficulty_reset_activation_daa_score: u64,
    difficulty_reset_window_blocks: u64,
}''', W)
s = once(s, '''        sampled_past_median_time_window_size: usize,
        past_median_time_sample_rate: u64,
    ) -> Self {
        let full_window_manager = FullWindowManager::new(''', '''        sampled_past_median_time_window_size: usize,
        past_median_time_sample_rate: u64,
        difficulty_reset_activation_daa_score: u64,
        difficulty_reset_window_blocks: u64,
    ) -> Self {
        let full_window_manager = FullWindowManager::new(''', W)
s = once(s, "        Self { ghostdag_store, headers_store, sampled_window_manager, full_window_manager, crescendo_activation }\n",
'''        Self {
            ghostdag_store,
            headers_store,
            sampled_window_manager,
            full_window_manager,
            crescendo_activation,
            genesis_bits: genesis.bits,
            difficulty_reset_activation_daa_score,
            difficulty_reset_window_blocks,
        }
''', W)
s = once(s, '''    fn calculate_difficulty_bits(&self, ghostdag_data: &GhostdagData, daa_window: &DaaWindow) -> u32 {
        match self.sampling(ghostdag_data.selected_parent) {
            true => self.sampled_window_manager.calculate_difficulty_bits(ghostdag_data, daa_window),
            false => self.full_window_manager.calculate_difficulty_bits(ghostdag_data, daa_window),
        }
    }''', '''    fn calculate_difficulty_bits(&self, ghostdag_data: &GhostdagData, daa_window: &DaaWindow) -> u32 {
        let bits = match self.sampling(ghostdag_data.selected_parent) {
            true => self.sampled_window_manager.calculate_difficulty_bits(ghostdag_data, daa_window),
            false => self.full_window_manager.calculate_difficulty_bits(ghostdag_data, daa_window),
        };
        // SEDRA v2.0.0: sedrad's applyDifficultyReset, applied after the normal calculation on the block's own DAA score
        apply_difficulty_reset(
            bits,
            daa_window.daa_score,
            self.difficulty_reset_activation_daa_score,
            self.difficulty_reset_window_blocks,
            self.genesis_bits,
        )
    }''', W)
s = s.rstrip("\n") + '''

/// SEDRA v2.0.0: sedrad's `applyDifficultyReset`. Returns the genesis bits for blocks inside the reset window,
/// otherwise the computed bits unchanged. Dormant when either reset parameter is 0.
pub fn apply_difficulty_reset(bits: u32, block_daa_score: u64, activation_daa_score: u64, window_blocks: u64, genesis_bits: u32) -> u32 {
    if window_blocks == 0 || activation_daa_score == 0 {
        return bits;
    }
    if kaspa_consensus_core::config::params::block_in_difficulty_reset_window(block_daa_score, activation_daa_score, window_blocks) {
        genesis_bits
    } else {
        bits
    }
}
'''
wr(W, s)

# ---------- services.rs ----------
S = "consensus/src/consensus/services.rs"
s = rd(S)
m = re.search(r"let window_manager = DualWindowManager::new\((.*?)\n        \);", s, re.S)
assert m, "DualWindowManager::new call"
call = m.group(0)
new_call = call[: -len("\n        );")] + "\n            params.difficulty_reset_activation_daa_score,\n            params.difficulty_reset_window_blocks,\n        );"
s = s.replace(call, new_call, 1)
s = once(s, '''            params.pre_deflationary_phase_base_subsidy,
            params.bps(),
        );
''', '''            params.pre_deflationary_phase_base_subsidy,
            params.bps(),
        )
        .with_treasury_allocation(params.treasury_allocation_windows, params.treasury_script_public_key);
''', S)
wr(S, s)

# ---------- coinbase.rs: treasury allocation ----------
C = "consensus/src/processes/coinbase.rs"
s = rd(C)
s = once(s, "    config::params::ForkedParam,", "    config::params::{block_in_treasury_allocation_window, ForkedParam, TreasuryAllocationWindow},", C)
s = once(s, '''    crescendo_activation_daa_score: u64,
}''', '''    crescendo_activation_daa_score: u64,

    /// SEDRA v2.0.0 treasury allocation (dormant when the windows or the script are empty)
    treasury_allocation_windows: &'static [TreasuryAllocationWindow],
    treasury_script_public_key: Option<ScriptPublicKey>,
}''', C)
s = once(s, '''            crescendo_activation_daa_score: bps.activation().daa_score(),
        }
    }
''', '''            crescendo_activation_daa_score: bps.activation().daa_score(),
            treasury_allocation_windows: &[],
            treasury_script_public_key: None,
        }
    }

    /// SEDRA v2.0.0: enables the treasury allocation output (sedrad's `treasuryAllocationOutput`).
    pub fn with_treasury_allocation(mut self, windows: &'static [TreasuryAllocationWindow], script_public_key: &'static [u8]) -> Self {
        self.treasury_allocation_windows = windows;
        self.treasury_script_public_key =
            if script_public_key.is_empty() { None } else { Some(ScriptPublicKey::new(0, ScriptVec::from_slice(script_public_key))) };
        self
    }

    /// SEDRA v2.0.0: sedrad's `treasuryAllocationOutput` for a block with the given DAA score. The first matching window
    /// with a non-zero amount pays. Dormant when no window or no script is configured.
    pub fn treasury_allocation_output(&self, daa_score: u64) -> Option<TransactionOutput> {
        let spk = self.treasury_script_public_key.as_ref()?;
        if self.treasury_allocation_windows.is_empty() {
            return None;
        }
        self.treasury_allocation_windows
            .iter()
            .filter(|w| w.per_block_seep != 0)
            .find(|w| block_in_treasury_allocation_window(daa_score, w.activation_daa_score, w.window_blocks))
            .map(|w| TransactionOutput::new(w.per_block_seep, spk.clone()))
    }
''', C)
s = once(s, '''        if red_reward > 0 {
            outputs.push(TransactionOutput::new(red_reward, miner_data.script_public_key.clone()));
        }
''', '''        if red_reward > 0 {
            outputs.push(TransactionOutput::new(red_reward, miner_data.script_public_key.clone()));
        }

        // SEDRA v2.0.0: the treasury allocation output comes after the blue and red reward outputs, as in sedrad
        if let Some(treasury_output) = self.treasury_allocation_output(daa_score) {
            outputs.push(treasury_output);
        }
''', C)
wr(C, s)
print("M6 code applied")
