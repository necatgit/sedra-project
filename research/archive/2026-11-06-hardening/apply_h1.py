"""Hardening 1: storage mass without division by zero (upstream rusty-kaspa 778b21e2, part). Run from repo root."""
import pathlib

P = "consensus/core/src/mass/mod.rs"
p = pathlib.Path(P)
s = p.read_text()
old = "    let mean_ins = sum_ins / ins_plurality;\n"
new = ("    // SEDRA (security back-port, upstream rusty-kaspa 778b21e2): inputs whose total amount is smaller than their total\n"
       "    // plurality give a mean of 0, and the division below would panic. Storage mass is only enforced in block validation\n"
       "    // after Crescendo (never on Sedra); before that it is computed for mempool transactions only.\n"
       "    let mean_ins = (sum_ins / ins_plurality).max(1);\n")
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
anchor = "#[cfg(test)]\nmod tests {\n"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + '''    /// SEDRA (security back-port, upstream 778b21e2): many tiny inputs (total amount below total plurality) must not
    /// divide by zero in the arithmetic input path.
    #[test]
    fn sedra_storage_mass_tiny_inputs_do_not_divide_by_zero_test() {
        let inputs = vec![UtxoCell::new(2, 1), UtxoCell::new(2, 1), UtxoCell::new(2, 1)]; // plurality 6, amount 3: mean 0
        let outputs = vec![UtxoCell::new(1, 1), UtxoCell::new(1, 1)];
        let mass = calc_storage_mass(false, inputs.into_iter(), outputs.into_iter(), 10_000);
        assert!(mass.is_some());
    }

''', 1)
p.write_text(s)
print("storage mass fix applied")
