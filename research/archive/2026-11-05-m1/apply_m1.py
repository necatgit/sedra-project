"""M1: put Sedra's network parameters into rusty-kaspa v1.0.1. Run from the repo root."""
import re, pathlib, subprocess

def edit(path, old, new, count=1):
    p = pathlib.Path(path); s = p.read_text()
    n = s.count(old)
    assert n == count, f"{path}: expected {count} occurrence(s) of {old[:60]!r}, found {n}"
    p.write_text(s.replace(old, new))

# --- genesis (values from sedrad v2.0.0 domain/dagconfig/genesis.go) ---
g = pathlib.Path("consensus/core/src/config/genesis.rs"); s = g.read_text()
start = s.index("/// The genesis block of the block-DAG which serves as the public transaction ledger for the main network.")
end = s.index("pub const TESTNET_GENESIS")
def hx(h): 
    b = bytes.fromhex(h); return ", ".join(f"0x{x:02x}" for x in b)
sedra = f'''/// The genesis block of the Sedra mainnet. Values copied from sedrad v2.0.0 (`domain/dagconfig/genesis.go`).
/// Unlike Kaspa (checkpoint genesis at DAA score 1312860), Sedra starts at DAA score 0 with an empty UTXO set.
pub const GENESIS: GenesisBlock = GenesisBlock {{
    hash: Hash::from_bytes([{hx("7c380ae690f9eaa64f300451d5e466371113c38b96ed96fe3f1e934869355ffa")}]),
    version: 0,
    hash_merkle_root: Hash::from_bytes([{hx("0a654355c1d58bd4abd9bdcc2e52f1bd565864e8a16ce0377b48ecc64db54b27")}]),
    utxo_commitment: Hash::from_bytes([{hx("544eb3142c000f0ad2c76ac41f4222abbababed830eeafee4b6dc56b52d5cac0")}]), // empty MuHash
    timestamp: 0x14d2bd72185,
    bits: 525264379,
    nonce: 0x1a14e,
    daa_score: 0,
    #[rustfmt::skip]
    coinbase_payload: &[
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // Blue score
        0x00, 0xE1, 0xF5, 0x05, 0x00, 0x00, 0x00, 0x00, // Subsidy
        0x00, 0x00,                                     // Script version
        0x01,                                           // Varint
        0x00,                                           // OP-FALSE
        0x73, 0x65, 0x64, 0x72, 0x61, 0x2D, 0x6D, 0x61, 0x69, 0x6E, 0x6E, 0x65, 0x74, // "sedra-mainnet"
    ],
}};

'''
s = s[:start] + sedra + s[end:]
# Sedra's devnet genesis is identical to its mainnet genesis (sedrad genesis.go, devnet section).
dstart = s.index("pub const DEVNET_GENESIS: GenesisBlock = GenesisBlock {")
dend = s.index("};", dstart) + 2
s = s[:dstart] + "/// Sedra's devnet genesis is identical to its mainnet genesis (sedrad v2.0.0 `genesis.go`).\npub const DEVNET_GENESIS: GenesisBlock = GENESIS;" + s[dend:]
g.write_text(s)

# --- network name prefix and ports (sedrad params.go) ---
edit("consensus/core/src/network.rs", 'format!("kaspa-{}", self)', 'format!("sedra-{}", self)')
edit("consensus/core/src/network.rs", 'strip_prefix("kaspa-")', 'strip_prefix("sedra-")')
for a, b in [("NetworkType::Mainnet => 16110", "NetworkType::Mainnet => 22110"), ("NetworkType::Testnet => 16210", "NetworkType::Testnet => 22210"),
             ("NetworkType::Simnet => 16510", "NetworkType::Simnet => 22510"), ("NetworkType::Devnet => 16610", "NetworkType::Devnet => 22610"),
             ("NetworkType::Mainnet => 16111", "NetworkType::Mainnet => 22111"), ("Some(10) => 16211", "Some(10) => 22211"),
             ("Some(11) => 16311", "Some(11) => 22311"), ("None | Some(_) => 16411", "None | Some(_) => 22411"),
             ("NetworkType::Simnet => 16511", "NetworkType::Simnet => 22511"), ("NetworkType::Devnet => 16611", "NetworkType::Devnet => 22611")]:
    edit("consensus/core/src/network.rs", a, b)

# --- address prefixes (sedrad util/address.go) ---
for a, b in [('"kaspatest"', '"sedratest"'), ('"kaspasim"', '"sedrasim"'), ('"kaspadev"', '"sedradev"'), ('"kaspa"', '"sedra"')]:
    p = pathlib.Path("crypto/addresses/src/lib.rs"); s = p.read_text(); assert a in s, a; p.write_text(s.replace(a, b))

# --- params: DNS seeders, minimum difficulty window, later Kaspa features permanently off ---
p = pathlib.Path("consensus/core/src/config/params.rs"); s = p.read_text()
ms = s.index("pub const MAINNET_PARAMS: Params = Params {"); ds = s.index("dns_seeders: &[", ms); de = s.index("],", ds) + 2
s = s[:ds] + 'dns_seeders: &[\n        // Sedra DNS seeders (sedrad v2.0.0 params.go)\n        "sedra-seed-1.sedracoin.com",\n        "sedra-seed-2.sedracoin.com",\n        "sedra-seed-3.sedracoin.com",\n    ],' + s[de:]
ts = s.index("pub const TESTNET_PARAMS: Params = Params {"); ds = s.index("dns_seeders: &[", ts); de = s.index("],", ds) + 2
s = s[:ds] + "dns_seeders: &[], // Sedra has no testnet seeders" + s[de:]
n = s.count("min_difficulty_window_size: MIN_DIFFICULTY_WINDOW_SIZE,")
s = s.replace("min_difficulty_window_size: MIN_DIFFICULTY_WINDOW_SIZE,",
              "min_difficulty_window_size: LEGACY_DIFFICULTY_WINDOW_SIZE, // Go node: genesis bits until the full 2641-block window exists")
s, k = re.subn(r"crescendo_activation: ForkActivation::(new\([0-9_]+\)|always\(\)|never\(\)),",
               "crescendo_activation: ForkActivation::never(), // Sedra runs the pre-Crescendo (kaspad Go v0.12.15) rules", s)
p.write_text(s); print("min window replaced:", n, " crescendo replaced:", k)

# --- subsidy table (sedrad v2.0.0 coinbasemanager.go, 192 entries, padded with zeros to keep the table size) ---
go = subprocess.run(["git", "-C", str(pathlib.Path.home()/"repos/sedrad"), "show", "4a1153d:domain/consensus/processes/coinbasemanager/coinbasemanager.go"], capture_output=True, text=True, check=True).stdout
body = go[go.index("var subsidyByDeflationaryMonthTable"):]; body = body[body.index("{")+1:body.index("}")]
vals = [int(x) for x in re.findall(r"\d+", body)]; assert len(vals) == 192 and vals[-1] == 0, len(vals)
padded = vals + [0] * (426 - len(vals))
rows = ",\n".join("\t" + ", ".join(str(v) for v in padded[i:i+25]) for i in range(0, 426, 25))
p = pathlib.Path("consensus/src/processes/coinbase.rs"); s = p.read_text()
ts = s.index("const SUBSIDY_BY_MONTH_TABLE: [u64; 426] = ["); te = s.index("];", ts) + 2
s = s[:ts] + "const SUBSIDY_BY_MONTH_TABLE: [u64; 426] = [\n" + rows + ",\n];" + s[te:]
s = s.replace("    This table was pre-calculated by calling `calcDeflationaryPeriodBlockSubsidyFloatCalc` (in kaspad-go) for all months until reaching 0 subsidy.",
              "    SEDRA: the first 192 entries are sedrad v2.0.0's `subsidyByDeflationaryMonthTable` (changed upstream on 2025-04-08, e61214d);\n    the rest is zero padding. Go clamps to its last entry (0), so the padding gives identical results.\n    Original note: this table was pre-calculated by calling `calcDeflationaryPeriodBlockSubsidyFloatCalc` (in kaspad-go) for all months until reaching 0 subsidy.")
p.write_text(s); print("subsidy entries:", len(vals), "sum:", sum(vals))

# --- P2P: accept protocol v5 (Sedra's Go nodes) on every network ---
edit("protocol/flows/src/flow_context.rs",
     "let connect_only_new_versions = self.config.net.network_type() != NetworkType::Testnet;",
     "// SEDRA: Sedra's Go nodes speak protocol v5 only, so older protocol versions stay enabled on every network.\n        let connect_only_new_versions = false;")
print("M1 edits applied")
