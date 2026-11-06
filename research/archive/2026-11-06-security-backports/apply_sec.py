"""Security back-ports from later rusty-kaspa releases into sedra-rusty (issue #29, research/0006). Run from repo root."""
import pathlib


def edit(path, pairs):
    p = pathlib.Path(path)
    s = p.read_text()
    for old, new in pairs:
        assert s.count(old) == 1, f"{path}: expected 1 occurrence of {old[:70]!r}, found {s.count(old)}"
        s = s.replace(old, new)
    p.write_text(s)
    print("ok", path)


# ---------- 1. P2P handshake time offset (upstream 2a47b249, part) ----------
FC = "protocol/flows/src/flow_context.rs"
edit(FC, [(
    "        let time_offset = unix_now() as i64 - peer_version_message.timestamp;",
    "        let time_offset = handshake_time_offset(unix_now() as i64, peer_version_message.timestamp);",
)])
p = pathlib.Path(FC)
p.write_text(p.read_text().rstrip("\n") + '''

/// SEDRA (security back-port, upstream rusty-kaspa 2a47b249): the peer chooses `timestamp`, so the time offset must be
/// computed without overflow. The release build has overflow checks, and a panic ends the whole node.
fn handshake_time_offset(now: i64, peer_timestamp: i64) -> i64 {
    now.saturating_sub(peer_timestamp)
}

#[cfg(test)]
mod sedra_backport_tests {
    use super::handshake_time_offset;

    #[test]
    fn handshake_time_offset_does_not_overflow_test() {
        assert_eq!(handshake_time_offset(1_000, 400), 600);
        assert_eq!(handshake_time_offset(1_000, i64::MIN), i64::MAX);
        assert_eq!(handshake_time_offset(-1_000, i64::MAX), i64::MIN);
    }
}
''')

# ---------- 2. Mempool: unchecked output index (upstream 778b21e2, part) ----------
edit("mining/errors/src/mempool.rs", [(
    "    #[error(\"transaction {0} doesn't exist in transaction pool\")]\n    RejectMissingTransaction(TransactionId),\n",
    "    #[error(\"transaction {0} doesn't exist in transaction pool\")]\n    RejectMissingTransaction(TransactionId),\n\n"
    "    /// SEDRA (security back-port, upstream rusty-kaspa 778b21e2)\n"
    "    #[error(\"at least one outpoint of the transaction is impossible to have a matching UTXO entry\")]\n"
    "    RejectImpossibleOutpoint,\n\n"
    "    /// SEDRA (security back-port, upstream rusty-kaspa eb0a856d)\n"
    "    #[error(\"coinbase transaction {0} cannot be added to the mempool\")]\n"
    "    RejectCoinbase(TransactionId),\n",
)])
edit("mining/src/mempool/populate_entries_and_try_validate.rs", [
    ("use kaspa_mining_errors::mempool::RuleError;\n\nimpl Mempool {\n    pub(crate) fn populate_mempool_entries(&self, transaction: &mut MutableTransaction) {",
     "use kaspa_mining_errors::mempool::RuleError;\n\n"
     "/// SEDRA (security back-port, upstream rusty-kaspa 778b21e2)\n"
     "#[derive(Debug, Clone, Copy, PartialEq, Eq)]\n"
     "pub(crate) enum PopulateError {\n    ImpossibleOutpoint,\n}\n\n"
     "impl From<PopulateError> for RuleError {\n    fn from(err: PopulateError) -> Self {\n        match err {\n"
     "            PopulateError::ImpossibleOutpoint => RuleError::RejectImpossibleOutpoint,\n        }\n    }\n}\n\n"
     "impl Mempool {\n    pub(crate) fn populate_mempool_entries(&self, transaction: &mut MutableTransaction) -> Result<(), PopulateError> {"),
    ("                let output = &parent.mtx.tx.outputs[input.previous_outpoint.index as usize];",
     "                // SEDRA (security back-port, upstream 778b21e2): the index comes from the incoming transaction\n"
     "                let output =\n"
     "                    parent.mtx.tx.outputs.get(input.previous_outpoint.index as usize).ok_or(PopulateError::ImpossibleOutpoint)?;"),
    ("                    Some(UtxoEntry::new(output.value, output.script_public_key.clone(), UNACCEPTED_DAA_SCORE, false));\n            }\n        }\n    }\n}",
     "                    Some(UtxoEntry::new(output.value, output.script_public_key.clone(), UNACCEPTED_DAA_SCORE, false));\n            }\n        }\n        Ok(())\n    }\n}"),
])
edit("mining/src/mempool/validate_and_insert_transaction.rs", [
    ("    ) -> RuleResult<TransactionPreValidation> {\n        self.validate_transaction_unacceptance(&transaction)?;",
     "    ) -> RuleResult<TransactionPreValidation> {\n"
     "        // SEDRA (security back-port, upstream rusty-kaspa eb0a856d): coinbase transactions never belong in the mempool\n"
     "        if transaction.tx.is_coinbase() {\n"
     "            return Err(kaspa_mining_errors::mempool::RuleError::RejectCoinbase(transaction.tx.id()));\n"
     "        }\n"
     "        self.validate_transaction_unacceptance(&transaction)?;"),
    ("        self.populate_mempool_entries(&mut transaction);\n        Ok(TransactionPreValidation",
     "        self.populate_mempool_entries(&mut transaction)?;\n        Ok(TransactionPreValidation"),
])
edit("mining/src/manager.rs", [(
    "                    mempool.populate_mempool_entries(&mut x);\n",
    "                    // SEDRA (upstream 778b21e2): impossible for transactions already admitted to the pool, which were fully\n"
    "                    // populated before insertion; on error the transaction falls through to the missing-outpoints path.\n"
    "                    let _ = mempool.populate_mempool_entries(&mut x);\n",
)])

# ---------- 3. Address with valid checksum but wrong payload length (upstream 2a47b249, part) ----------
edit("crypto/addresses/src/lib.rs", [
    ("pub enum AddressError {\n",
     "pub enum AddressError {\n"
     "    /// SEDRA (security back-port, upstream rusty-kaspa 2a47b249)\n"
     "    #[error(\"The address payload length is invalid: expected {expected} bytes, got {actual}\")]\n"
     "    InvalidPayloadLength { expected: usize, actual: usize },\n\n"),
    ("impl Address {\n    pub fn new(prefix: Prefix, version: Version, payload: &[u8]) -> Self {",
     "impl Address {\n"
     "    /// SEDRA (security back-port, upstream rusty-kaspa 2a47b249): like [`Self::new`], but returns an error instead of\n"
     "    /// panicking when the payload length does not match the version. Use it for any externally supplied address.\n"
     "    pub fn try_new(prefix: Prefix, version: Version, payload: &[u8]) -> Result<Self, AddressError> {\n"
     "        let expected = version.public_key_len();\n"
     "        if !prefix.is_test() && payload.len() != expected {\n"
     "            return Err(AddressError::InvalidPayloadLength { expected, actual: payload.len() });\n"
     "        }\n"
     "        Ok(Self { prefix, payload: PayloadVec::from_slice(payload), version })\n"
     "    }\n\n"
     "    pub fn new(prefix: Prefix, version: Version, payload: &[u8]) -> Self {"),
    ("        let payload: Vec<u8> = borsh::BorshDeserialize::deserialize_reader(reader)?;\n        Ok(Self::new(prefix, version, &payload))",
     "        let payload: Vec<u8> = borsh::BorshDeserialize::deserialize_reader(reader)?;\n"
     "        // SEDRA (security back-port, upstream 2a47b249)\n"
     "        Self::try_new(prefix, version, &payload).map_err(|err| std::io::Error::new(std::io::ErrorKind::InvalidData, err.to_string()))"),
])
edit("crypto/addresses/src/bech32.rs", [(
    "        Ok(Self::new(prefix, payload_u8[0].try_into()?, payload_u8[1..].into()))",
    "        // SEDRA (security back-port, upstream rusty-kaspa 2a47b249): reject a wrong payload length instead of panicking\n"
    "        Self::try_new(prefix, payload_u8[0].try_into()?, &payload_u8[1..])",
)])

# ---------- regression tests ----------
L = "crypto/addresses/src/lib.rs"
edit(L, [(
    "    #[test]\n    fn test_errors() {",
    '''    /// SEDRA (security back-port, upstream 2a47b249): a mainnet address with a valid checksum but the wrong payload
    /// length must be rejected as an error, from a string and from Borsh, instead of crashing the node.
    #[test]
    fn sedra_wrong_payload_length_is_an_error_test() {
        let bad = Address { prefix: Prefix::Mainnet, version: Version::PubKey, payload: PayloadVec::from_slice(&[7u8; 5]) };
        let encoded: String = (&bad).into();
        let parsed: Result<Address, AddressError> = encoded.as_str().try_into();
        assert_eq!(parsed, Err(AddressError::InvalidPayloadLength { expected: 32, actual: 5 }), "{encoded}");
        let bytes = borsh::to_vec(&bad).unwrap();
        assert!(<Address as borsh::BorshDeserialize>::try_from_slice(&bytes).is_err());
        // a correct address still parses
        let good = Address::new(Prefix::Mainnet, Version::PubKey, &[7u8; 32]);
        let good_str: String = (&good).into();
        assert_eq!(Address::try_from(good_str.as_str()), Ok(good));
    }

    #[test]
    fn test_errors() {''',
)])
M = "mining/src/manager_tests.rs"
edit(M, [(
    "    fn create_transaction_with_utxo_entry(i: u32, block_daa_score: u64) -> MutableTransaction {",
    '''    /// SEDRA (security back-port, upstream rusty-kaspa eb0a856d): coinbase transactions are rejected by the mempool.
    #[test]
    fn sedra_reject_coinbase_transaction_test() {
        let consensus = ConsensusMock::new();
        let mining_manager = MiningManager::new(TARGET_TIME_PER_BLOCK, true, MAX_BLOCK_MASS, None, Arc::new(MiningCounters::default()));
        let transaction = Transaction::new(TX_VERSION, vec![], vec![], 0, kaspa_consensus_core::subnets::SUBNETWORK_ID_COINBASE, 0, vec![]);
        let transaction_id = transaction.id();
        let result = into_mempool_result(mining_manager.validate_and_insert_transaction(
            &consensus,
            transaction,
            Priority::Low,
            Orphan::Allowed,
            RbfPolicy::Allowed,
        ));
        assert_eq!(result, Err(RuleError::RejectCoinbase(transaction_id)));
        assert!(mining_manager.get_transaction(&transaction_id, TransactionQuery::All).is_none());
    }

    /// SEDRA (security back-port, upstream rusty-kaspa 778b21e2): a transaction spending a non-existent output index of a
    /// mempool transaction is rejected as an error instead of crashing the node.
    #[test]
    fn sedra_reject_impossible_outpoint_test() {
        let consensus = Arc::new(ConsensusMock::new());
        let mining_manager = MiningManager::new(TARGET_TIME_PER_BLOCK, false, MAX_BLOCK_MASS, None, Arc::new(MiningCounters::default()));
        let parent = create_transaction_with_utxo_entry(0, 0);
        let parent_id = parent.tx.id();
        assert_eq!(parent.tx.outputs.len(), 1);
        into_mempool_result(mining_manager.validate_and_insert_mutable_transaction(
            consensus.as_ref(),
            parent,
            Priority::Low,
            Orphan::Allowed,
            RbfPolicy::Forbidden,
        ))
        .unwrap();
        let (script_public_key, redeem_script) = op_true_script();
        let signature_script = pay_to_script_hash_signature_script(redeem_script, vec![]).unwrap();
        let input = TransactionInput::new(TransactionOutpoint::new(parent_id, 5), signature_script, MAX_TX_IN_SEQUENCE_NUM, 1);
        let child = Transaction::new(
            TX_VERSION,
            vec![input],
            vec![TransactionOutput::new(1_000, script_public_key)],
            0,
            SUBNETWORK_ID_NATIVE,
            0,
            vec![],
        );
        let result = into_mempool_result(mining_manager.validate_and_insert_transaction(
            consensus.as_ref(),
            child,
            Priority::Low,
            Orphan::Allowed,
            RbfPolicy::Forbidden,
        ));
        assert_eq!(result, Err(RuleError::RejectImpossibleOutpoint));
    }

    fn create_transaction_with_utxo_entry(i: u32, block_daa_score: u64) -> MutableTransaction {''',
)])
print("security back-ports applied")
